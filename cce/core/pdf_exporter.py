from cce.core.models import World
from cce.core.engine import TimeEngine
from cce.core.astronomy import AstronomyModel
from cce.core.weather import generate_daily_weather

def generate_printable_html_calendar(world: World, year: int = 0) -> str:
    """Generates a beautifully styled, printable HTML calendar for a given year."""
    engine = TimeEngine(world)
    astro = AstronomyModel(world)
    p_planet = engine.get_primary_planet()

    html = [
        "<!DOCTYPE html>",
        "<html>",
        "<head>",
        f"<title>Calendar: {world.name} - Year {year}</title>",
        "<style>",
        "  body { font-family: 'Segoe UI', Arial, sans-serif; background: #ffffff; color: #111; margin: 20px; }",
        "  h1 { text-align: center; color: #2b2b2b; border-bottom: 2px solid #00c0f0; padding-bottom: 10px; }",
        "  .month-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 20px; margin-top: 20px; }",
        "  .month-card { border: 1px solid #ccc; border-radius: 8px; padding: 10px; background: #f9f9f9; page-break-inside: avoid; }",
        "  .month-title { font-weight: bold; font-size: 16px; margin-bottom: 8px; color: #0070a0; text-align: center; }",
        "  .days-table { width: 100%; border-collapse: collapse; font-size: 12px; }",
        "  .days-table th, .days-table td { border: 1px solid #ddd; padding: 4px; text-align: center; }",
        "  .days-table th { background: #eef; font-weight: bold; }",
        "  .event-badge { background: #ffe0e0; color: #900; border-radius: 3px; font-size: 10px; padding: 1px 3px; display: block; margin-top: 2px; }",
        "  @media print { .month-grid { grid-template-columns: repeat(2, 1fr); } }",
        "</style>",
        "</head>",
        "<body>",
        f"<h1>📜 {world.name} – Year {year} Calendar</h1>",
        "<div class='month-grid'>"
    ]

    week_len = len(world.weekdays)
    cols = week_len if week_len > 0 else 7

    for m_idx, month in enumerate(world.months):
        html.append("<div class='month-card'>")
        html.append(f"<div class='month-title'>{month.name} ({month.days} Days)</div>")
        html.append("<table class='days-table'>")

        # Header weekdays
        html.append("<tr>")
        if week_len > 0:
            for wd in world.weekdays:
                html.append(f"<th>{wd.name[:3]}</th>")
        else:
            for i in range(1, 8):
                html.append(f"<th>Day {i}</th>")
        html.append("</tr>")

        days_in_month = engine.get_days_in_month(year, month)
        col = 0
        html.append("<tr>")

        for day in range(1, days_in_month + 1):
            exact_tick = engine.date_to_tick(p_planet, year, m_idx, day) if p_planet else 0

            # Check moon
            moons_info = astro.get_moon_phases_for_tick(exact_tick)
            moon_icon = ""
            for m_id, p_info in moons_info.items():
                moon_icon = p_info.get("phase_icon", "")
                break

            # Check events today
            day_events = []
            if p_planet:
                day_end_tick = exact_tick + p_planet.day_length_ticks
                for ev in world.events:
                    if ev.start_tick >= exact_tick and ev.start_tick < day_end_tick:
                        day_events.append(ev)

            ev_html = ""
            for ev in day_events[:2]: # Max 2 events per cell for print layout
                ch_str = f" [{ev.chapter}]" if getattr(ev, 'chapter', None) else ""
                ev_html += f"<span class='event-badge'>{ev.title}{ch_str}</span>"

            html.append(f"<td>{day} {moon_icon}{ev_html}</td>")
            col += 1
            if col >= cols:
                col = 0
                html.append("</tr><tr>")

        while col > 0 and col < cols:
            html.append("<td></td>")
            col += 1

        html.append("</tr></table></div>")

    html.append("</div></body></html>")
    return "\n".join(html)
