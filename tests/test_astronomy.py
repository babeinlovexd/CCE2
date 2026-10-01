from cce.core.models import World, Moon, Sun, Planet
from cce.core.astronomy import AstronomyModel, get_moon_phase_icon

def test_astronomy_moon_phase():
    world = World()
    moon = Moon(name="Selene", cycle_days=28.0, phase_offset=0.0)
    world.moons = [moon]

    astro = AstronomyModel(world)

    # Day 0: New Moon
    phase0 = astro.get_moon_phase(moon, 0)
    assert phase0["phase_name"] == "New Moon"
    assert phase0["phase_icon"] == "🌑"
    assert phase0["illumination"] < 0.05

    # Day 14 (half cycle): Full Moon
    phase14 = astro.get_moon_phase(moon, 14)
    assert phase14["phase_name"] == "Full Moon"
    assert phase14["phase_icon"] == "🌕"
    assert phase14["illumination"] > 0.95

def test_moon_phase_icons():
    assert get_moon_phase_icon("New Moon") == "🌑"
    assert get_moon_phase_icon("Full Moon") == "🌕"
    assert get_moon_phase_icon("First Quarter") == "🌓"
    assert get_moon_phase_icon("Unknown") == "🌙"

    # Zero cycle moon edge case
    world = World()
    astro = AstronomyModel(world)
    dead_moon = Moon(name="Dead", cycle_days=0.0)
    dead_phase = astro.get_moon_phase(dead_moon, 10)
    assert dead_phase["phase_name"] == "Unknown"

def test_astronomy_phases_for_tick():
    world = World()
    p = Planet(day_length_ticks=100, is_primary=True)
    m = Moon(id="m1", name="Phobos", cycle_days=10.0)
    world.planets = [p]
    world.moons = [m]

    astro = AstronomyModel(world)
    res = astro.get_moon_phases_for_tick(500) # Day 5
    assert "m1" in res
    assert res["m1"]["phase_name"] == "Full Moon"
