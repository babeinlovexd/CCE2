import re

# Fix engine.py weekday logic
with open("cce/core/engine.py", "r") as f: c = f.read()

# Add get_days_in_month if missing
if "def get_days_in_month" not in c:
    new_func = """    def get_days_in_month(self, year: int, month: Month) -> int:
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
        return days

    def tick_to_date(self, planet: Planet, tick: int) -> Dict:"""
    c = re.sub(r"    def tick_to_date\(self, planet: Planet, tick: int\) -> Dict:", new_func, c)

    old_month_logic = """        # Apply leap rules for this year to know which months have extra days
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

        found = False
        for month in self.world.months:
            month_days = month.days + leap_additions.get(month.id, 0)
            # Also support matching by month name if IDs were typed manually
            month_days += leap_additions.get(month.name, 0)

            if day_of_year < current_day + month_days:"""

    new_month_logic = """        found = False
        for month in self.world.months:
            month_days = self.get_days_in_month(year, month)

            if day_of_year < current_day + month_days:"""
    c = c.replace(old_month_logic, new_month_logic)

    old_dt_tick_logic = """        # Add days for months in the current year
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
                days_in_current_year += m.days + leap_additions.get(m.id, 0) + leap_additions.get(m.name, 0)"""

    new_dt_tick_logic = """        days_in_current_year = 0

        # We need to iterate up to month_index
        if month_index >= 0 and month_index < len(self.world.months):
            for i in range(month_index):
                m = self.world.months[i]
                days_in_current_year += self.get_days_in_month(year, m)"""
    c = c.replace(old_dt_tick_logic, new_dt_tick_logic)

c = re.sub(
    r"if days_remaining >= 0:\n\s*while True:\n\s*days_this_year = self\.get_days_in_year\(planet, year\)\n\s*if days_remaining < days_this_year:\n\s*break\n\s*days_remaining -= days_this_year\n\s*year \+= 1\n\s*else:\n\s*while days_remaining < 0:\n\s*year -= 1\n\s*days_this_year = self\.get_days_in_year\(planet, year\)\n\s*days_remaining \+= days_this_year",
    r"if days_remaining >= 0:\n            while True:\n                days_this_year = self.get_days_in_year(planet, year)\n                if days_this_year <= 0:\n                    days_this_year = 1\n                if days_remaining < days_this_year:\n                    break\n                if days_remaining > days_this_year * 10:\n                     skip_years = days_remaining // (days_this_year + 1)\n                     year += max(1, skip_years)\n                     days_remaining -= skip_years * days_this_year\n                     continue\n                days_remaining -= days_this_year\n                year += 1\n        else:\n            while days_remaining < 0:\n                year -= 1\n                days_this_year = self.get_days_in_year(planet, year)\n                if days_this_year <= 0:\n                    days_this_year = 1\n                if days_remaining < -days_this_year * 10:\n                    skip_years = (-days_remaining) // (days_this_year + 1)\n                    year -= max(1, skip_years)\n                    days_remaining += skip_years * days_this_year\n                    continue\n                days_remaining += days_this_year",
    c
)

c = re.sub(r"if planet\.day_length_ticks == 0:", r"if planet.day_length_ticks <= 0:", c)

with open("cce/core/engine.py", "w") as f: f.write(c)

# editor.py
with open("cce/gui/editor.py", "r") as f: c = f.read()
if "export_ical" not in c:
    c = c.replace('self.btn_export = QPushButton(translator.t("btn_export"))', 'self.btn_export = QPushButton(translator.t("btn_export"))\n        self.btn_export_ics = QPushButton("Export iCal")')
    c = c.replace('self.btn_export.clicked.connect(self.export_timeline)', 'self.btn_export.clicked.connect(self.export_timeline)\n        self.btn_export_ics.clicked.connect(self.export_ical)')
    c = c.replace('top_bar.addWidget(self.btn_export)', 'top_bar.addWidget(self.btn_export)\n        top_bar.addWidget(self.btn_export_ics)')

    export_ical_func = """
    def export_ical(self):
        self.flush_state_to_model()
        if not self.main_window.world.events:
            from PyQt6.QtWidgets import QMessageBox, QFileDialog
            QMessageBox.information(self, "Export", "No events to export.")
            return

        if not self.main_window.world.earth_sync_enabled:
            from PyQt6.QtWidgets import QMessageBox
            QMessageBox.warning(self, "Export Error", "Earth Sync must be enabled and valid to export to real-world iCal format.")
            return

        from PyQt6.QtWidgets import QFileDialog
        fname, _ = QFileDialog.getSaveFileName(self, "Export iCal", "timeline.ics", "iCalendar Files (*.ics);;All Files (*)")
        if not fname:
            return

        from cce.core.engine import TimeEngine
        engine = TimeEngine(self.main_window.world)

        try:
            import datetime
            with open(fname, 'w', encoding='utf-8') as f:
                f.write("BEGIN:VCALENDAR\\nVERSION:2.0\\nPRODID:-//Chronix//Custom Calendar Engine//EN\\n")

                for ev in self.main_window.world.events:
                    start_dt = engine.tick_to_earth_date(ev.start_tick)
                    end_dt = engine.tick_to_earth_date(ev.end_tick)
                    if not start_dt:
                        continue
                    if not end_dt: end_dt = start_dt + datetime.timedelta(hours=1)

                    dtstamp = datetime.datetime.now(datetime.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
                    dtstart = start_dt.strftime("%Y%m%dT%H%M%SZ")
                    dtend = end_dt.strftime("%Y%m%dT%H%M%SZ")

                    f.write("BEGIN:VEVENT\\n")
                    f.write(f"UID:{ev.id}@chronix\\n")
                    f.write(f"DTSTAMP:{dtstamp}\\n")
                    f.write(f"DTSTART:{dtstart}\\n")
                    f.write(f"DTEND:{dtend}\\n")
                    f.write(f"SUMMARY:{ev.title}\\n")

                    desc = ev.notes.replace("\\n", "\\\\n")
                    if ev.characters:
                        desc += f"\\\\nCharacters: {', '.join(ev.characters)}"
                    if desc:
                        f.write(f"DESCRIPTION:{desc}\\n")

                    if ev.location:
                        f.write(f"LOCATION:{ev.location}\\n")
                    if getattr(ev, 'category', ''):
                        f.write(f"CATEGORIES:{ev.category}\\n")

                    f.write("END:VEVENT\\n")

                f.write("END:VCALENDAR\\n")
            from PyQt6.QtWidgets import QMessageBox
            QMessageBox.information(self, "Success", "iCal exported successfully!")
        except Exception as e:
            from PyQt6.QtWidgets import QMessageBox
            QMessageBox.critical(self, "Error", f"Failed to export iCal:\\n{e}")
"""
    c = c.replace('    def flush_state_to_model(self):', f'{export_ical_func}\n    def flush_state_to_model(self):')

for method in ["populate_time_units", "populate_planets", "populate_eras", "populate_months", "populate_weekdays", "populate_holidays", "populate_leap_rules", "populate_suns", "populate_moons"]:
    pattern = r"(def " + method + r"\(self\):.*?)(self\.main_window\.mark_unsaved\(\)\s+)(self\.\w+\.blockSignals\(False\))"
    c = re.sub(pattern, r"\1\3", c, flags=re.DOTALL)

add_remove_blocks = [
    ("self.populate_time_units()", "self.populate_time_units()\n        self.main_window.mark_unsaved()"),
    ("self.populate_planets()", "self.populate_planets()\n        self.main_window.mark_unsaved()"),
    ("self.populate_eras()", "self.populate_eras()\n        self.main_window.mark_unsaved()"),
    ("self.populate_months()", "self.populate_months()\n        self.main_window.mark_unsaved()"),
    ("self.populate_weekdays()", "self.populate_weekdays()\n        self.main_window.mark_unsaved()"),
    ("self.populate_holidays()", "self.populate_holidays()\n        self.main_window.mark_unsaved()"),
    ("self.populate_leap_rules()", "self.populate_leap_rules()\n        self.main_window.mark_unsaved()"),
    ("self.populate_suns()", "self.populate_suns()\n        self.main_window.mark_unsaved()"),
    ("self.populate_moons()", "self.populate_moons()\n        self.main_window.mark_unsaved()"),
]
lambda_repl = [
    (r"self\.populate_eras\(\)\)\)", r"self.populate_eras(), self.main_window.mark_unsaved()))"),
    (r"self\.populate_months\(\)\)\)", r"self.populate_months(), self.main_window.mark_unsaved()))"),
    (r"self\.populate_weekdays\(\)\)\)", r"self.populate_weekdays(), self.main_window.mark_unsaved()))"),
    (r"self\.populate_holidays\(\)\)\)", r"self.populate_holidays(), self.main_window.mark_unsaved()))"),
    (r"self\.populate_leap_rules\(\)\)\)", r"self.populate_leap_rules(), self.main_window.mark_unsaved()))"),
    (r"self\.populate_suns\(\)\)\)", r"self.populate_suns(), self.main_window.mark_unsaved()))"),
    (r"self\.populate_moons\(\)\)\)", r"self.populate_moons(), self.main_window.mark_unsaved()))")
]

for old, new in lambda_repl:
    c = re.sub(old, new, c)
for old, new in add_remove_blocks:
    c = c.replace("        " + old, "        " + new)

# Fix blockSignals for ValueError
c = re.sub(
    r"except ValueError:\n\s*QMessageBox.warning\(self, 'Invalid Input', 'Please enter a valid number.'\)\n\s*self.refresh_view\(\)",
    r"except ValueError:\n                QMessageBox.warning(self, 'Invalid Input', 'Please enter a valid number.')\n                return",
    c
)
c = c.replace("            else:\n                p.is_primary = False\n        self.main_window.mark_unsaved()", "            else:\n                p.is_primary = False\n            self.main_window.mark_unsaved()")

if "def pick_month_color" not in c:
    c = re.sub(
        r"self\.month_table\.itemChanged\.connect\(self\.update_months\)",
        r"self.month_table.itemChanged.connect(self.update_months)\n        self.month_table.itemDoubleClicked.connect(self.pick_month_color)",
        c
    )
    c = re.sub(
        r"(def update_months\(self\):.*?m\.color = self\.month_table\.item\(r, 2\)\.text\(\)\n)",
        r"\1\n    def pick_month_color(self, item):\n        if item.column() == 2:\n            from PyQt6.QtWidgets import QColorDialog\n            from PyQt6.QtGui import QColor\n            color = QColorDialog.getColor(QColor(item.text()), self, 'Select Month Color')\n            if color.isValid():\n                item.setText(color.name())\n                self.update_months()\n                self.main_window.mark_unsaved()\n",
        c, flags=re.DOTALL
    )

with open("cce/gui/editor.py", "w") as f: f.write(c)

# viewer.py
with open("cce/gui/viewer.py", "r") as f: c = f.read()

if "btn_toggle_view" not in c:
    c = c.replace('header_layout.addWidget(self.btn_next_year)', 'header_layout.addWidget(self.btn_next_year)\n        self.btn_toggle_view = QPushButton("Toggle Yearly View")\n        self.btn_toggle_view.setCheckable(True)\n        self.btn_toggle_view.clicked.connect(self.render_calendar)\n        header_layout.addWidget(self.btn_toggle_view)')

if "chk_recurring" not in c:
    recurrence_ui = """        # Recurrence
        from PyQt6.QtWidgets import QCheckBox, QSpinBox
        self.ev_rec_layout = QHBoxLayout()
        self.chk_recurring = QCheckBox("Repeat every")
        self.spin_recur_interval = QSpinBox()
        self.spin_recur_interval.setMinimum(1)
        self.spin_recur_interval.setMaximum(99999)
        self.spin_recur_interval.setValue(365)
        self.spin_recur_interval.setSuffix(" days")
        self.ev_rec_layout.addWidget(self.chk_recurring)
        self.ev_rec_layout.addWidget(self.spin_recur_interval)

        self.ev_notes = QTextEdit()"""
    c = c.replace('self.ev_notes = QTextEdit()', recurrence_ui)
    c = c.replace('self.ev_layout.addRow("Category/Color", self.ev_cat_layout)', 'self.ev_layout.addRow("Recurrence", self.ev_rec_layout)\n        self.ev_layout.addRow("Category/Color", self.ev_cat_layout)')

    # Add to new_event
    c = c.replace('self.ev_chars.clear()', 'self.chk_recurring.setChecked(False)\n        self.spin_recur_interval.setValue(365)\n        self.ev_chars.clear()')

    # Add to load_event
    c = c.replace('self.btn_ev_delete.setVisible(True)', "is_rec = getattr(ev, 'is_recurring', False)\n                self.chk_recurring.setChecked(is_rec)\n                self.spin_recur_interval.setValue(getattr(ev, 'recurrence_interval_days', 365))\n                self.btn_ev_delete.setVisible(True)")

    # Add to save_event
    c = c.replace('self.main_window.mark_unsaved()', "self.current_event.is_recurring = self.chk_recurring.isChecked()\n        self.current_event.recurrence_interval_days = self.spin_recur_interval.value()\n        self.main_window.mark_unsaved()", 1)


if "☀️" not in c:
    sun_indicator_old = """        # Sun Info
        sun_text = []
        for sun in self.main_window.world.suns:
            sun_text.append(f"☀️ {sun.name}: Dawn {sun.twilight_dawn_ticks}T, Dusk {sun.twilight_dusk_ticks}T")
        if not sun_text:
            self.lbl_sun_info.setText("")
        else:
            self.lbl_sun_info.setText(" | ".join(sun_text))"""
    sun_indicator_new = """        # Sun Info (Graphical progress bar)
        sun_layout_html = ""
        for sun in self.main_window.world.suns:
            dl = p_planet.day_length_ticks if p_planet and p_planet.day_length_ticks > 0 else 86400
            dawn_pct = (sun.twilight_dawn_ticks / dl) * 100
            dusk_pct = (sun.twilight_dusk_ticks / dl) * 100

            dawn_pct = max(0, min(100, dawn_pct))
            dusk_pct = max(0, min(100, dusk_pct))

            if dawn_pct > dusk_pct:
                dawn_pct, dusk_pct = dusk_pct, dawn_pct

            # Simple text-based bar
            bar_len = 30
            dawn_idx = int((dawn_pct / 100) * bar_len)
            dusk_idx = int((dusk_pct / 100) * bar_len)

            bar = ""
            for i in range(bar_len):
                if i < dawn_idx or i > dusk_idx:
                    bar += "🌙"
                else:
                    bar += "☀️"

            sun_layout_html += f\"\"\"
            <div style='margin-bottom: 5px;'>
                <span style='color: #cdd6f4; font-size: 11px;'>☀️ {sun.name}</span><br/>
                <span style='font-size: 8px;'>{bar}</span>
                <div style='display: flex; justify-content: space-between; font-size: 9px; color: #a6adc8;'>
                    <span>Dawn ({sun.twilight_dawn_ticks})</span>
                    <span>Dusk ({sun.twilight_dusk_ticks})</span>
                </div>
            </div>
            \"\"\"

        if not self.main_window.world.suns:
            if hasattr(self, 'lbl_sun_info'):
                self.lbl_sun_info.setText("")
        else:
            if not hasattr(self, 'lbl_sun_info'):
                pass
            else:
                self.lbl_sun_info.setText(sun_layout_html)"""
    c = c.replace(sun_indicator_old, sun_indicator_new)


# Render calendar yearly toggle
new_render = """    def render_calendar(self):
        # Clear grid
        for i in reversed(range(self.calendar_grid.count())):
            widget = self.calendar_grid.itemAt(i).widget()
            if widget:
                widget.setParent(None)

        world = self.main_window.world
        if not world.months:
            self.lbl_current_view.setText(translator.t("no_months"))
            return

        is_yearly = self.btn_toggle_view.isChecked() if hasattr(self, 'btn_toggle_view') else False
        p_planet = self.engine.get_primary_planet()

        if is_yearly:
            self.lbl_current_view.setText(f"Year {self.current_year}")

            # Yearly view layout
            cols = 3
            for m_idx, month in enumerate(world.months):
                from PyQt6.QtWidgets import QGridLayout
                month_group = QGroupBox(month.name)
                m_layout = QGridLayout(month_group)
                m_layout.setContentsMargins(5, 5, 5, 5)
                m_layout.setSpacing(2)

                days_in_month = self.engine.get_days_in_month(self.current_year, month)
                m_row, m_col = 0, 0
                for day in range(1, days_in_month + 1):
                    exact_tick = self.engine.date_to_tick(p_planet, self.current_year, m_idx, day) if p_planet else 0
                    btn = DayButton(str(day), exact_tick, self)
                    btn.setFixedSize(30, 30) # Smaller buttons for yearly view
                    btn.setStyleSheet(f"background-color: {month.color}; font-size: 10px;")

                    if p_planet:
                        events_today = 0
                        day_end_tick = exact_tick + p_planet.day_length_ticks
                        for ev in world.events:
                            occurs_today = False
                            if ev.start_tick >= exact_tick and ev.start_tick < day_end_tick:
                                occurs_today = True
                            elif getattr(ev, 'is_recurring', False) and ev.start_tick < day_end_tick:
                                interval = getattr(ev, 'recurrence_interval_days', 365) * p_planet.day_length_ticks
                                if interval > 0:
                                    start_of_event_day = ev.start_tick - (ev.start_tick % p_planet.day_length_ticks)
                                    diff = exact_tick - start_of_event_day
                                    if diff % interval < p_planet.day_length_ticks and diff >= 0:
                                        occurs_today = True
                            if occurs_today:
                                events_today += 1

                        if events_today > 0:
                            btn.setProperty("class", "calendar-day-event")
                            btn.setText(f"{day}\\n📍")
                        else:
                            btn.setProperty("class", "calendar-day")

                        btn.style().unpolish(btn)
                        btn.style().polish(btn)
                        btn.clicked.connect(lambda checked, t=exact_tick, midx=m_idx: self.switch_to_month_and_select_day(t, midx))

                    m_layout.addWidget(btn, m_row, m_col)
                    m_col += 1
                    if m_col >= 7: # arbitrarily use 7 columns for compact mini-months if not strictly aligning weekdays
                        m_col = 0
                        m_row += 1

                grid_row = m_idx // cols
                grid_col = m_idx % cols
                self.calendar_grid.addWidget(month_group, grid_row, grid_col)

        else:
            month = world.months[self.current_month_index]
            self.lbl_current_view.setText(f"Year {self.current_year}, {month.name}")

            # Draw Weekday headers if they exist
            week_len = len(world.weekdays)
            if week_len > 0:
                for i, wd in enumerate(world.weekdays):
                    lbl = QLabel(wd.name)
                    lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
                    lbl.setStyleSheet("font-weight: bold; padding: 5px;")
                    self.calendar_grid.addWidget(lbl, 0, i)

            days_in_month = self.engine.get_days_in_month(self.current_year, month)

            # Calculate start weekday for alignment
            start_tick = self.engine.date_to_tick(p_planet, self.current_year, self.current_month_index, 1)
            start_date_info = self.engine.tick_to_date(p_planet, start_tick)

            row = 1
            col = 0
            cols_per_row = week_len if week_len > 0 else 7

            if week_len > 0 and start_date_info.get('weekday'):
                # Find index of weekday
                for i, wd in enumerate(world.weekdays):
                    if wd.id == start_date_info['weekday'].id:
                        col = i
                        break

            for day in range(1, days_in_month + 1):
                exact_tick = self.engine.date_to_tick(p_planet, self.current_year, self.current_month_index, day) if p_planet else 0
                btn = DayButton(str(day), exact_tick, self)
                btn.setFixedSize(60, 60)
                btn.setStyleSheet(f"background-color: {month.color};")

                if p_planet:

                    # Visual badge for events
                    events_today = 0
                    search_match = False
                    day_end_tick = exact_tick + p_planet.day_length_ticks
                    query = self.search_input.text().lower().strip()

                    for ev in world.events:
                        occurs_today = False
                        if ev.start_tick >= exact_tick and ev.start_tick < day_end_tick:
                            occurs_today = True
                        elif getattr(ev, 'is_recurring', False) and ev.start_tick < day_end_tick:
                            interval = getattr(ev, 'recurrence_interval_days', 365) * p_planet.day_length_ticks
                            if interval > 0:
                                start_of_event_day = ev.start_tick - (ev.start_tick % p_planet.day_length_ticks)
                                diff = exact_tick - start_of_event_day
                                if diff % interval < p_planet.day_length_ticks and diff >= 0:
                                    occurs_today = True

                        if occurs_today:
                            events_today += 1
                            if query:
                                if query in ev.title.lower() or query in ev.location.lower() or query in ev.notes.lower():
                                    search_match = True
                                for char in ev.characters:
                                    if query in char.lower():
                                        search_match = True

                    moons_info = self.astro.get_moon_phases_for_tick(exact_tick)
                    moon_tooltip = ""
                    for m_id, p_info in moons_info.items():
                        moon_tooltip += f"{p_info['moon'].name}: {p_info['phase_name']} ({int(p_info['phase_percent']*100)}%)\\n"
                    if moon_tooltip:
                        btn.setToolTip(moon_tooltip.strip())
                        btn.setText(f"{day}\\n🌘")

                    if events_today > 0:
                        base_text = str(day)
                        if moon_tooltip: base_text += "\\n🌘"
                        btn.setText(f"{base_text}\\n({events_today} 📌)")

                    if search_match:
                        btn.setProperty("class", "calendar-day-search")
                    elif events_today > 0:
                        btn.setProperty("class", "calendar-day-event")
                    else:
                        btn.setProperty("class", "calendar-day")

                    # Force style re-evaluation
                    btn.style().unpolish(btn)
                    btn.style().polish(btn)

                    btn.clicked.connect(lambda checked, t=exact_tick: self.select_day(t))

                self.calendar_grid.addWidget(btn, row, col)
                col += 1
                if col >= cols_per_row:
                    col = 0
                    row += 1

    def switch_to_month_and_select_day(self, tick, month_idx):
        if hasattr(self, 'btn_toggle_view'):
            self.btn_toggle_view.setChecked(False)
        self.current_month_index = month_idx
        self.render_calendar()
        self.select_day(tick)"""

old_render = r"    def render_calendar\(self\):.*?self\.calendar_grid\.addWidget\(btn, row, col\)\n\s*col \+= 1\n\s*if col >= cols_per_row:\n\s*col = 0\n\s*row \+= 1"
c = re.sub(old_render, new_render, c, flags=re.DOTALL)

# Fix the exception_interval bug
old_leap = """        days_in_month = month.days
        # Apply leap rules to this month
        for rule in world.leap_rules:
            if rule.interval_years > 0 and self.current_year % rule.interval_years == 0:
                is_exception = False
                if rule.exception_interval and rule.exception_interval > 0 and self.current_year % rule.exception_interval == 0:
                    is_exception = True
                if rule.month_id_to_append == month.id:
                    days_in_month += rule.exception_days if is_exception else rule.days_to_add"""

new_leap = """        days_in_month = self.engine.get_days_in_month(self.current_year, month)"""
c = c.replace(old_leap, new_leap)


with open("cce/gui/viewer.py", "w") as f: f.write(c)
