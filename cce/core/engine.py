from datetime import datetime, timedelta
from typing import Tuple, List, Dict, Optional
from .models import World, Planet, Era, Month, Holiday, LeapRule

class TimeEngine:
    def __init__(self, world: World):
        self.world = world

    def get_primary_planet(self) -> Optional[Planet]:
        for p in self.world.planets:
            if p.is_primary:
                return p
        return self.world.planets[0] if self.world.planets else None

    def get_days_in_year(self, planet: Planet, year: int) -> int:
        if not planet.is_primary:
            return planet.year_length_days

        base_days = sum(m.days for m in self.world.months)
        for h in self.world.holidays:
            is_intercalary = not h.month_id
            if h.month_id:
                month_exists = any(m.id == h.month_id or m.name == h.month_id for m in self.world.months)
                if not month_exists:
                    is_intercalary = True
            if is_intercalary:
                base_days += 1

        leap_days = 0
        for rule in self.world.leap_rules:
            if rule.interval_years > 0 and year % rule.interval_years == 0:
                # Check for exclusion
                is_excluded = False
                if rule.exclude_interval and rule.exclude_interval > 0 and year % rule.exclude_interval == 0:
                    is_excluded = True
                    # Check for force inclusion (e.g. every 400 years)
                    if rule.force_include_interval and rule.force_include_interval > 0 and year % rule.force_include_interval == 0:
                        is_excluded = False

                if not is_excluded:
                    leap_days += rule.days_to_add

        return base_days + leap_days

    def get_days_in_month(self, year: int, month: Month) -> int:
        days = month.days
        for rule in self.world.leap_rules:
            if rule.interval_years > 0 and year % rule.interval_years == 0:
                is_excluded = False
                if getattr(rule, 'exclude_interval', 0) and getattr(rule, 'exclude_interval', 0) > 0 and year % getattr(rule, 'exclude_interval', 0) == 0:
                    is_excluded = True
                    if getattr(rule, 'force_include_interval', 0) and getattr(rule, 'force_include_interval', 0) > 0 and year % getattr(rule, 'force_include_interval', 0) == 0:
                        is_excluded = False

                if not is_excluded:
                    if rule.month_id_to_append == month.id or rule.month_id_to_append == month.name:
                        days += rule.days_to_add
        return max(1, days)

    def tick_to_date(self, planet: Planet, tick: int) -> Dict:
        """
        Convert an absolute tick to a specific date for a planet.
        Returns: year, month, day_of_month, day_of_year, time_of_day_ticks, etc.
        """
        if planet.day_length_ticks <= 0:
            return {}

        total_days = tick // planet.day_length_ticks
        time_of_day_ticks = tick % planet.day_length_ticks

        year = 0
        days_remaining = total_days

        # We assume year 0 starts at day 0.
        # Calculate year by iterating (could be optimized, but ok for now)
        if days_remaining >= 0:
            while True:
                days_this_year = self.get_days_in_year(planet, year)
                if days_this_year <= 0:
                    days_this_year = 1
                if days_remaining < days_this_year:
                    break
                if days_remaining > days_this_year * 10:
                     skip_years = days_remaining // (days_this_year + 1)
                     year += max(1, skip_years)
                     days_remaining -= skip_years * days_this_year
                     continue
                days_remaining -= days_this_year
                year += 1
        else:
            while days_remaining < 0:
                year -= 1
                days_this_year = self.get_days_in_year(planet, year)
                if days_this_year <= 0:
                    days_this_year = 1
                if days_remaining < -days_this_year * 10:
                    skip_years = (-days_remaining) // (days_this_year + 1)
                    year -= max(1, skip_years)
                    days_remaining += skip_years * days_this_year
                    continue
                days_remaining += days_this_year

        day_of_year = days_remaining # 0-indexed

        # Determine month and day of month
        current_day = 0
        current_month = None
        day_of_month = 0

        found = False
        for month in self.world.months:
            month_days = self.get_days_in_month(year, month)

            if day_of_year < current_day + month_days:
                current_month = month
                day_of_month = day_of_year - current_day + 1 # 1-indexed
                found = True
                break
            current_day += month_days

        # What if it's a holiday outside of months?
        is_holiday = False
        holiday_obj = None
        if not found:
            # It's an intercalary day / unassigned holiday
            for h in self.world.holidays:
                # Treat empty string or None as intercalary (outside of months)
                # Also treat it as intercalary if the month_id doesn't match any real month ID or name
                is_intercalary = not h.month_id
                if h.month_id:
                    month_exists = any(m.id == h.month_id or m.name == h.month_id for m in self.world.months)
                    if not month_exists:
                        is_intercalary = True

                if is_intercalary:
                    if day_of_year == current_day:
                        is_holiday = True
                        holiday_obj = h
                        found = True
                        break
                    current_day += 1

        # Calculate weekday
        weekday = None
        if self.world.weekdays:
            # Need to know total days since epoch that counted as weekdays
            # For simplicity, we just modulo total_days if all days count.
            # If holidays don't count, we need to subtract them.
            # A full implementation would count days from 0.
            # Simplified for now: just count all days if all days are weekdays.
            week_len = len(self.world.weekdays)
            if week_len > 0:
                weekday_index = total_days % week_len
                weekday = self.world.weekdays[weekday_index]

        # Determine era
        current_era = None
        for era in sorted(self.world.eras, key=lambda e: e.start_year, reverse=True):
            if year >= era.start_year:
                current_era = era
                break

        year_in_era = year
        if current_era:
            year_in_era = year - current_era.start_year
            if not current_era.includes_year_zero:
                year_in_era += 1

        return {
            "year": year,
            "year_in_era": year_in_era,
            "era": current_era,
            "month": current_month,
            "day_of_month": day_of_month,
            "day_of_year": day_of_year + 1,
            "weekday": weekday,
            "is_holiday": is_holiday,
            "holiday": holiday_obj,
            "time_of_day_ticks": time_of_day_ticks,
            "total_days": total_days
        }

    def format_time(self, time_ticks: int) -> str:
        """
        Format the time of day based on custom time units.
        Returns a string representation.
        """
        if not self.world.time_units:
            return f"{time_ticks} {self.world.base_tick_name}"

        # Sort units by size descending
        units = sorted(self.world.time_units, key=lambda u: u.ticks, reverse=True)
        remaining = time_ticks
        parts = []
        for u in units:
            if u.ticks <= 0:
                continue
            val = remaining // u.ticks
            remaining = remaining % u.ticks
            parts.append(f"{val} {u.abbreviation or u.name}")

        if remaining > 0 or not parts:
            parts.append(f"{remaining} {self.world.base_tick_name}")

        return ", ".join(parts)

    def date_to_tick(self, planet: Planet, year: int, month_index: int, day_of_month: int) -> int:
        """
        Convert a date to the absolute start tick of that day.
        """
        if not planet or planet.day_length_ticks == 0:
            return 0

        total_days = 0

        # Calculate days for all years prior to current year
        if year >= 0:
            for y in range(0, year):
                total_days += self.get_days_in_year(planet, y)
        else:
            for y in range(year, 0):
                total_days -= self.get_days_in_year(planet, y)

        # Add days for months in the current year
        leap_additions = {}
        for rule in self.world.leap_rules:
            if rule.interval_years > 0 and year % rule.interval_years == 0:
                is_excluded = False
                if rule.exclude_interval and rule.exclude_interval > 0 and year % rule.exclude_interval == 0:
                    is_excluded = True
                    if rule.force_include_interval and rule.force_include_interval > 0 and year % rule.force_include_interval == 0:
                        is_excluded = False

                if not is_excluded:
                    leap_additions[rule.month_id_to_append] = leap_additions.get(rule.month_id_to_append, 0) + rule.days_to_add

        days_in_current_year = 0

        # We need to iterate up to month_index
        if month_index >= 0 and month_index < len(self.world.months):
            for i in range(month_index):
                m = self.world.months[i]
                days_in_current_year += m.days + leap_additions.get(m.id, 0) + leap_additions.get(m.name, 0)

        total_days += days_in_current_year + (day_of_month - 1)

        return total_days * planet.day_length_ticks

    def tick_to_earth_date(self, tick: int) -> Optional[datetime]:
        """
        Converts a universal tick to a real-world Earth datetime.
        Returns None if earth_sync_enabled is False.
        """
        if not self.world.earth_sync_enabled:
            return None

        try:
            # Parse the ISO string to a datetime object
            epoch = datetime.fromisoformat(self.world.earth_epoch_iso)
        except ValueError:
            return None

        # Calculate total real seconds
        total_seconds = tick * self.world.real_seconds_per_tick

        # We might have very large numbers of seconds that exceed timedelta limits depending on the world size.
        # timedelta max is about 999,999,999 days.
        try:
            target_date = epoch + timedelta(seconds=total_seconds)
            return target_date
        except OverflowError:
            return None
