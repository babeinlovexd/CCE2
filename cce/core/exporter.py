import csv
import io
import json
from datetime import datetime, timezone
from typing import List
from cce.core.models import World, Event
from cce.core.engine import TimeEngine

def export_to_ical(world: World) -> str:
    """Generates an iCalendar (.ics) string representation of all events."""
    engine = TimeEngine(world)
    p_planet = engine.get_primary_planet()

    lines = [
        "BEGIN:VCALENDAR",
        "VERSION:2.0",
        "PRODID:-//Chronix//Fantasy Calendar Engine//EN",
        "CALSCALE:GREGORIAN",
        f"X-WR-CALNAME:{world.name}"
    ]

    for ev in world.events:
        dt_start_str = ""
        if world.earth_sync_enabled:
            dt = engine.tick_to_earth_date(ev.start_tick)
            if dt:
                dt_start_str = dt.strftime("%Y%m%dT%H%M%SZ")

        if not dt_start_str:
            # Fallback date format based on tick
            dt_start_str = f"20000101T000000Z"

        lines.append("BEGIN:VEVENT")
        lines.append(f"UID:{ev.id}@chronix")
        lines.append(f"DTSTAMP:{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')}")
        lines.append(f"DTSTART:{dt_start_str}")
        lines.append(f"SUMMARY:{ev.title}")
        if ev.location:
            lines.append(f"LOCATION:{ev.location}")
        if ev.notes or ev.characters:
            desc = ev.notes
            if ev.characters:
                desc += f" (Characters: {', '.join(ev.characters)})"
            lines.append(f"DESCRIPTION:{desc.replace('\n', ' ')}")
        if getattr(ev, 'category', None):
            lines.append(f"CATEGORIES:{ev.category}")
        lines.append("END:VEVENT")

    lines.append("END:VCALENDAR")
    return "\n".join(lines)


def export_to_csv(world: World) -> str:
    """Generates a CSV string representation of all events."""
    engine = TimeEngine(world)
    p_planet = engine.get_primary_planet()

    output = io.StringIO()
    writer = csv.writer(output)

    # Header
    writer.writerow(["ID", "Title", "Date_String", "Start_Tick", "End_Tick", "Location", "Characters", "Category", "Notes"])

    sorted_events = sorted(world.events, key=lambda e: e.start_tick)
    for ev in sorted_events:
        date_str = f"Tick {ev.start_tick}"
        if p_planet:
            d_info = engine.tick_to_date(p_planet, ev.start_tick)
            m_name = d_info['month'].name if d_info.get('month') else "Intercalary"
            e_name = f"{d_info['era'].name} " if d_info.get('era') else ""
            date_str = f"{e_name}Year {d_info['year']}, {m_name} {d_info['day_of_month']}"

        writer.writerow([
            ev.id,
            ev.title,
            date_str,
            ev.start_tick,
            ev.end_tick,
            ev.location,
            ", ".join(ev.characters),
            getattr(ev, 'category', ''),
            ev.notes
        ])

    return output.getvalue()


def export_to_json(world: World) -> str:
    """Generates a structured JSON string export of events."""
    engine = TimeEngine(world)
    p_planet = engine.get_primary_planet()

    data = []
    for ev in sorted(world.events, key=lambda e: e.start_tick):
        date_str = f"Tick {ev.start_tick}"
        if p_planet:
            d_info = engine.tick_to_date(p_planet, ev.start_tick)
            m_name = d_info['month'].name if d_info.get('month') else "Intercalary"
            e_name = f"{d_info['era'].name} " if d_info.get('era') else ""
            date_str = f"{e_name}Year {d_info['year']}, {m_name} {d_info['day_of_month']}"

        data.append({
            "id": ev.id,
            "title": ev.title,
            "date_string": date_str,
            "start_tick": ev.start_tick,
            "end_tick": ev.end_tick,
            "location": ev.location,
            "characters": ev.characters,
            "category": getattr(ev, 'category', ''),
            "notes": ev.notes
        })

    return json.dumps({"world_name": world.name, "events": data}, indent=2)
