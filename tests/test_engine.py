import pytest
from datetime import datetime, timedelta

from cce.core.models import World, Planet, Month, Holiday
from cce.core.engine import TimeEngine

def test_engine_tick_conversion():
    world = World()
    world.months.clear()
    world.planets.clear()
    world.leap_rules.clear()
    world.holidays.clear()
    world.months.append(Month(id="m1", name="Jan", days=30, color="#fff"))
    world.months.append(Month(id="m2", name="Feb", days=30, color="#fff"))

    planet = Planet(id="p1", name="Earth", day_length_ticks=100, is_primary=True)
    world.planets.append(planet)

    engine = TimeEngine(world)

    # Tick 0 should be year 0, month 0, day 1, time 0
    res = engine.tick_to_date(planet, 0)
    assert res["year"] == 0
    assert res["month"].name == "Jan"
    assert res["day_of_month"] == 1
    assert res["time_of_day_ticks"] == 0

    # Tick 50 should be same day, time 50
    res = engine.tick_to_date(planet, 50)
    assert res["day_of_month"] == 1
    assert res["time_of_day_ticks"] == 50

    # Tick 150 should be day 2, time 50
    res = engine.tick_to_date(planet, 150)
    assert res["day_of_month"] == 2
    assert res["time_of_day_ticks"] == 50

    # Tick 3000 should be exactly Month 2, Day 1
    res = engine.tick_to_date(planet, 3000)
    assert res["month"].name == "Feb"
    assert res["day_of_month"] == 1

    # Tick 6000 should be year 1, Month 1, Day 1 (since year is 60 days)
    res = engine.tick_to_date(planet, 6000)
    assert res["year"] == 1
    assert res["month"].name == "Jan"
    assert res["day_of_month"] == 1

def test_engine_earth_sync():
    world = World()
    world.months.clear()
    world.planets.clear()
    world.leap_rules.clear()
    world.holidays.clear()
    world.earth_sync_enabled = True
    world.earth_epoch_iso = "2000-01-01T00:00:00"
    world.real_seconds_per_tick = 2.0 # 1 tick = 2 seconds

    engine = TimeEngine(world)

    dt = engine.tick_to_earth_date(0)
    assert dt == datetime(2000, 1, 1, 0, 0, 0)

    dt = engine.tick_to_earth_date(30)
    assert dt == datetime(2000, 1, 1, 0, 1, 0) # 60 seconds later

def test_engine_date_to_tick():
    world = World()
    world.months.clear()
    world.planets.clear()
    world.leap_rules.clear()
    world.holidays.clear()
    world.months.append(Month(id="m1", name="Jan", days=30, color="#fff"))
    planet = Planet(id="p1", name="Earth", day_length_ticks=100, is_primary=True)
    world.planets.append(planet)

    engine = TimeEngine(world)

    # Year 0, Month 0, Day 1 -> Tick 0
    t = engine.date_to_tick(planet, 0, 0, 1)
    assert t == 0

    # Year 0, Month 0, Day 2 -> Tick 100
    t = engine.date_to_tick(planet, 0, 0, 2)
    assert t == 100

    # Year 1, Month 0, Day 1 -> Tick 3000
    t = engine.date_to_tick(planet, 1, 0, 1)
    assert t == 3000

def test_engine_format_time():
    from cce.core.models import TimeUnit
    world = World()
    world.time_units = [
        TimeUnit(name="Hour", abbreviation="h", ticks=3600),
        TimeUnit(name="Minute", abbreviation="m", ticks=60)
    ]
    engine = TimeEngine(world)

    s = engine.format_time(3665)
    assert "1 h" in s
    assert "1 m" in s
    assert "5 Tick" in s

def test_intercalary_holiday():
    world = World()
    world.months = [Month(id="m1", name="Month1", days=10)]
    world.holidays = [Holiday(id="h1", name="New Year Day", month_id=None)]
    planet = Planet(id="p1", day_length_ticks=10, is_primary=True)
    world.planets = [planet]

    engine = TimeEngine(world)

    days = engine.get_days_in_year(planet, 0)
    assert days == 11 # 10 days in month + 1 intercalary holiday

    # Day 10 (0-indexed) should be the intercalary holiday
    date_info = engine.tick_to_date(planet, 10 * 10)
    assert date_info["is_holiday"] is True
    assert date_info["holiday"].name == "New Year Day"
