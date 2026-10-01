from typing import List, Dict, Callable
from cce.core.models import World, Planet, Month, Weekday, Holiday, TimeUnit, Sun, Moon, Era, LeapRule

def get_fantasy_standard() -> World:
    world = World(name="Fantasy Kingdom", base_tick_name="Second")
    world.time_units = [
        TimeUnit(name="Hour", abbreviation="h", ticks=3600),
        TimeUnit(name="Minute", abbreviation="m", ticks=60)
    ]
    world.planets = [Planet(name="Aethelgard", day_length_ticks=86400, year_length_days=360, is_primary=True)]
    world.eras = [Era(name="Age of Dragons", abbreviation="AD", start_year=1, includes_year_zero=False)]
    world.months = [
        Month(name="Frostreach", days=30, color="#89b4fa"),
        Month(name="Thawmel", days=30, color="#89b4fa"),
        Month(name="Bloomtide", days=30, color="#a6e3a1"),
        Month(name="Sunpeak", days=30, color="#f9e2af"),
        Month(name="Highsummer", days=30, color="#fab387"),
        Month(name="Goldleaf", days=30, color="#f38ba8"),
        Month(name="Harvestide", days=30, color="#cba6f7"),
        Month(name="Emberfall", days=30, color="#f2cdcd"),
        Month(name="Shadowsown", days=30, color="#b4befe"),
        Month(name="Frostfall", days=30, color="#74c7ec"),
        Month(name="Deepwinter", days=30, color="#89dceb"),
        Month(name="Yearsend", days=30, color="#313244")
    ]
    world.weekdays = [
        Weekday(name="Moonday"),
        Weekday(name="Towerday"),
        Weekday(name="Windday"),
        Weekday(name="Thunderday"),
        Weekday(name="Fireday"),
        Weekday(name="Starday"),
        Weekday(name="Sunnday")
    ]
    world.suns = [Sun(name="Solarius", twilight_dawn_ticks=21600, twilight_dusk_ticks=64800)]
    world.moons = [Moon(name="Lunaria", cycle_days=28.0, phase_offset=0.0)]
    world.leap_rules = [LeapRule(interval_years=4, month_id_to_append=world.months[-1].id, days_to_add=1)]
    return world

def get_faerun_harptos() -> World:
    world = World(name="Faerûn (Calendar of Harptos)", base_tick_name="Second")
    world.time_units = [
        TimeUnit(name="Hour", abbreviation="h", ticks=3600),
        TimeUnit(name="Minute", abbreviation="m", ticks=60)
    ]
    world.planets = [Planet(name="Toril", day_length_ticks=86400, year_length_days=365, is_primary=True)]
    world.eras = [Era(name="Dalereckoning", abbreviation="DR", start_year=1, includes_year_zero=False)]

    m1 = Month(name="Hammer (Deepwinter)", days=30, color="#74c7ec")
    m2 = Month(name="Alturiak (The Claw of Winter)", days=30, color="#89dceb")
    m3 = Month(name="Ches (The Claw of Sunsets)", days=30, color="#a6e3a1")
    m4 = Month(name="Tarsakh (The Claw of Storms)", days=30, color="#94e2d5")
    m5 = Month(name="Mirtul (The Melting)", days=30, color="#f9e2af")
    m6 = Month(name="Kythorn (The Time of Flowers)", days=30, color="#fab387")
    m7 = Month(name="Flamerule (Summertide)", days=30, color="#f38ba8")
    m8 = Month(name="Eleasis (Highsun)", days=30, color="#eb6f92")
    m9 = Month(name="Eleint (The Fading)", days=30, color="#cba6f7")
    m10 = Month(name="Marpenoth (Leaffall)", days=30, color="#f2cdcd")
    m11 = Month(name="Uktar (The Rotting)", days=30, color="#b4befe")
    m12 = Month(name="Nightal (The Drawing Down)", days=30, color="#313244")

    world.months = [m1, m2, m3, m4, m5, m6, m7, m8, m9, m10, m11, m12]

    world.holidays = [
        Holiday(name="Midwinter", month_id=None, day_in_month=1, counts_as_weekday=False),
        Holiday(name="Greengrass", month_id=None, day_in_month=2, counts_as_weekday=False),
        Holiday(name="Midsummer", month_id=None, day_in_month=3, counts_as_weekday=False),
        Holiday(name="Highharvestide", month_id=None, day_in_month=4, counts_as_weekday=False),
        Holiday(name="The Feast of the Moon", month_id=None, day_in_month=5, counts_as_weekday=False)
    ]

    world.weekdays = [Weekday(name=f"Day {i}") for i in range(1, 11)] # Tenday
    world.suns = [Sun(name="Anauria", twilight_dawn_ticks=21600, twilight_dusk_ticks=64800)]
    world.moons = [Moon(name="Selûne", cycle_days=30.4375, phase_offset=0.0)]
    world.leap_rules = [LeapRule(interval_years=4, month_id_to_append=m7.id, days_to_add=1)] # Shieldmeet
    return world

def get_sci_fi_mars() -> World:
    world = World(name="Ares Colony (Mars Calendar)", base_tick_name="Second")
    world.time_units = [
        TimeUnit(name="Sol Hour", abbreviation="sh", ticks=3699),
        TimeUnit(name="Sol Minute", abbreviation="sm", ticks=61)
    ]
    world.planets = [Planet(name="Mars", day_length_ticks=88775, year_length_days=668, is_primary=True)]
    world.eras = [Era(name="Post-Landing", abbreviation="PL", start_year=1, includes_year_zero=False)]

    months = []
    month_names = ["Gemini", "Cancer", "Leo", "Virgo", "Libra", "Scorpius",
                   "Sagittarius", "Capricornus", "Aquarius", "Pisces", "Aries", "Taurus"]
    for i, name in enumerate(month_names * 2):
        months.append(Month(name=f"{name} {1 if i < 12 else 2}", days=28 if i % 6 != 5 else 27, color="#f38ba8" if i % 2 == 0 else "#fab387"))

    world.months = months
    world.weekdays = [Weekday(name=d) for d in ["Sol 1", "Sol 2", "Sol 3", "Sol 4", "Sol 5", "Sol 6", "Sol 7"]]
    world.suns = [Sun(name="Sol", twilight_dawn_ticks=22000, twilight_dusk_ticks=66000)]
    world.moons = [
        Moon(name="Phobos", cycle_days=0.3189, phase_offset=0.0),
        Moon(name="Deimos", cycle_days=1.263, phase_offset=0.0)
    ]
    world.earth_sync_enabled = True
    world.earth_epoch_iso = "2040-01-01T00:00:00"
    world.real_seconds_per_tick = 1.02749125 # Mars Sol tick factor
    return world

PRESETS: Dict[str, Callable[[], World]] = {
    "Fantasy Standard (12 Months, 360 Days)": get_fantasy_standard,
    "D&D Forgotten Realms (Harptos Calendar)": get_faerun_harptos,
    "Sci-Fi Mars Colony (668 Sols)": get_sci_fi_mars
}
