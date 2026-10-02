from cce.core.models import World, Event, Planet, Month
from cce.core.weather import generate_daily_weather
from cce.core.pdf_exporter import generate_printable_html_calendar

def test_weather_generator():
    w1 = generate_daily_weather("world1", 100, "Jan", 15, "Glacial")
    w2 = generate_daily_weather("world1", 100, "Jan", 15, "Glacial")
    assert w1 == w2 # Determinism
    assert w1["temp_c"] < 10 # Glacial climate temperature check
    assert "icon" in w1

def test_chapter_tagging():
    ev = Event(title="The Journey Begins", chapter="Chapter 1: Departure")
    assert ev.chapter == "Chapter 1: Departure"

def test_printable_html_calendar():
    world = World(name="Eldoria Realm")
    world.planets = [Planet(name="Aethel", day_length_ticks=100, is_primary=True)]
    world.months = [Month(name="Bloom", days=10)]
    world.events = [Event(title="Spring Festival", start_tick=100, chapter="Chapter 2")]

    html = generate_printable_html_calendar(world, year=0)
    assert "Eldoria Realm" in html
    assert "Spring Festival" in html
    assert "Chapter 2" in html
