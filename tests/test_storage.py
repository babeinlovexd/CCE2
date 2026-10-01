import tempfile
import os
from cce.core.models import World, Planet, Month, TimeUnit, Era, Holiday, LeapRule, Sun, Moon, Event
from cce.core.storage import save_world, load_world

def test_storage_save_and_load():
    world = World(name="Test Cosmos", base_tick_name="Pulse")
    world.time_units.append(TimeUnit(name="Cycle", abbreviation="cy", ticks=100))
    world.planets.append(Planet(name="Mars", day_length_ticks=500, year_length_days=200))
    world.eras.append(Era(name="Age of Starlight", start_year=100))
    world.months.append(Month(name="Sol", days=25, color="#ff0000"))
    world.holidays.append(Holiday(name="Equinox", day_in_month=12))
    world.leap_rules.append(LeapRule(interval_years=5, days_to_add=2))
    world.suns.append(Sun(name="Alpha", twilight_dawn_ticks=10, twilight_dusk_ticks=10))
    world.moons.append(Moon(name="Luna", cycle_days=14.0, phase_offset=0.0))
    world.events.append(Event(title="Great Flare", start_tick=1000, end_tick=2000, characters=["Alice", "Bob"]))

    with tempfile.NamedTemporaryFile(suffix=".worldcal", delete=False) as tmp:
        tmp_path = tmp.name

    try:
        save_world(world, tmp_path)
        loaded = load_world(tmp_path)

        assert loaded.name == "Test Cosmos"
        assert loaded.base_tick_name == "Pulse"
        assert len(loaded.time_units) == len(world.time_units)
        assert len(loaded.planets) == len(world.planets)
        assert loaded.planets[1].name == "Mars"
        assert loaded.eras[0].name == "Age of Starlight"
        assert loaded.events[0].title == "Great Flare"
        assert loaded.events[0].characters == ["Alice", "Bob"]
    finally:
        if os.path.exists(tmp_path):
            os.remove(tmp_path)
