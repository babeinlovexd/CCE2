from cce.core.models import World, Event, Planet, Month
from cce.core.exporter import export_to_ical, export_to_csv, export_to_json

def test_export_formats():
    world = World(name="Test Export Realm")
    world.planets = [Planet(name="Terra", day_length_ticks=100, is_primary=True)]
    world.months = [Month(name="Janus", days=30)]
    world.events = [
        Event(title="Council Meeting", start_tick=100, end_tick=200, location="High Citadel", characters=["Arthur", "Merlin"], category="Politics", notes="Discuss invasion threats.")
    ]

    # Test iCal export
    ics = export_to_ical(world)
    assert "BEGIN:VCALENDAR" in ics
    assert "BEGIN:VEVENT" in ics
    assert "SUMMARY:Council Meeting" in ics
    assert "LOCATION:High Citadel" in ics
    assert "CATEGORIES:Politics" in ics
    assert "END:VCALENDAR" in ics

    # Test CSV export
    csv_str = export_to_csv(world)
    assert "Council Meeting" in csv_str
    assert "High Citadel" in csv_str
    assert "Arthur, Merlin" in csv_str

    # Test JSON export
    json_str = export_to_json(world)
    assert '"world_name": "Test Export Realm"' in json_str
    assert '"title": "Council Meeting"' in json_str
    assert '"location": "High Citadel"' in json_str
