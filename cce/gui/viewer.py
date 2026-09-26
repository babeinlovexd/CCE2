from PyQt6.QtWidgets import (QWidget, QGroupBox, QVBoxLayout, QHBoxLayout, QLabel,
                             QPushButton, QGridLayout, QScrollArea, QFrame,
                             QLineEdit, QListWidget, QListWidgetItem, QFormLayout, QTextEdit, QComboBox, QSpinBox)
from PyQt6.QtCore import Qt

from cce.core.engine import TimeEngine
from cce.core.astronomy import AstronomyModel
from cce.core.models import Event
from .translations import translator
from PyQt6.QtCore import QMimeData
from PyQt6.QtGui import QDrag

class TimeInputWidget(QWidget):
    """A custom widget to input time using custom time units instead of raw ticks."""
    def __init__(self, time_units, base_tick_name="Tick"):
        super().__init__()
        self.time_units = sorted(time_units, key=lambda x: x.ticks, reverse=True)
        self.base_tick_name = base_tick_name
        self.inputs = {}

        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        if not self.time_units:
            # Fallback if no custom units exist
            self.base_input = QSpinBox()
            self.base_input.setMaximum(999999)
            layout.addWidget(self.base_input)
            layout.addWidget(QLabel(self.base_tick_name))
        else:
            self.base_input = None
            for unit in self.time_units:
                spin = QSpinBox()
                spin.setMaximum(999999)
                self.inputs[unit.id] = spin
                layout.addWidget(spin)
                layout.addWidget(QLabel(unit.abbreviation or unit.name))

    def get_ticks(self) -> int:
        if self.base_input:
            return self.base_input.value()

        total_ticks = 0
        for unit in self.time_units:
            spin = self.inputs.get(unit.id)
            if spin:
                total_ticks += spin.value() * unit.ticks
        return total_ticks

    def set_ticks(self, ticks: int):
        if self.base_input:
            self.base_input.setValue(ticks)
            return

        remaining = ticks
        for unit in self.time_units:
            spin = self.inputs.get(unit.id)
            if spin:
                val = remaining // unit.ticks
                spin.setValue(val)
                remaining = remaining % unit.ticks


class DayButton(QPushButton):
    def __init__(self, text, day_tick, parent_viewer):
        super().__init__(text)
        self.day_tick = day_tick
        self.parent_viewer = parent_viewer
        self.setAcceptDrops(True)

    def dragEnterEvent(self, event):
        if event.mimeData().hasFormat('text/plain'):
            event.accept()
        else:
            event.ignore()

    def dropEvent(self, event):
        event_id = event.mimeData().text()
        self.parent_viewer.move_event_to_day(event_id, self.day_tick)
        event.accept()

class EventListWidget(QListWidget):
    def __init__(self, parent_viewer):
        super().__init__()
        self.parent_viewer = parent_viewer
        self.setDragEnabled(True)

    def startDrag(self, supportedActions):
        item = self.currentItem()
        if not item: return

        event_id = item.data(Qt.ItemDataRole.UserRole)
        if not event_id: return

        drag = QDrag(self)
        mimeData = QMimeData()
        mimeData.setText(str(event_id))
        drag.setMimeData(mimeData)
        drag.exec(supportedActions)

class ViewerWidget(QWidget):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.engine = None
        self.astro = None

        self.current_year = 0
        self.current_month_index = 0
        self.selected_tick = 0

        self.layout = QVBoxLayout(self)

        # Header / Navigation
        header_layout = QHBoxLayout()
        self.btn_back = QPushButton(translator.t("btn_back"))
        self.btn_back.clicked.connect(self.main_window.switch_to_editor)

        self.btn_prev_year = QPushButton("<< Year")
        self.btn_prev_month = QPushButton("< Month")
        self.lbl_current_view = QLabel("Year 0, Month 1")
        self.lbl_current_view.setStyleSheet("font-size: 18px; font-weight: bold;")
        self.lbl_current_view.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.btn_next_month = QPushButton("Month >")
        self.btn_next_year = QPushButton("Year >>")

        self.btn_prev_year.clicked.connect(lambda: self.change_year(-1))
        self.btn_prev_month.clicked.connect(lambda: self.change_month(-1))
        self.btn_next_month.clicked.connect(lambda: self.change_month(1))
        self.btn_next_year.clicked.connect(lambda: self.change_year(1))

        header_layout.addWidget(self.btn_back)
        header_layout.addStretch()
        header_layout.addWidget(self.btn_prev_year)
        header_layout.addWidget(self.btn_prev_month)
        header_layout.addWidget(self.lbl_current_view)
        header_layout.addWidget(self.btn_next_month)
        header_layout.addWidget(self.btn_next_year)
        self.btn_toggle_view = QPushButton("Toggle Yearly View")
        self.btn_toggle_view.setCheckable(True)
        self.btn_toggle_view.clicked.connect(self.render_calendar)
        header_layout.addWidget(self.btn_toggle_view)
        header_layout.addStretch()

        self.layout.addLayout(header_layout)

        # Search & Sync
        search_layout = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText(translator.t("search_ph"))
        self.search_input.textChanged.connect(self.perform_search)

        self.planet_sync_lbl = QLabel(translator.t("sync_lbl"))
        self.planet_sync_combo = QComboBox()
        self.planet_sync_combo.currentIndexChanged.connect(self.update_sync_display)
        self.planet_sync_combo.setToolTip(translator.t("tt_sync"))
        self.lbl_sync_result = QLabel("")

        search_layout.addWidget(self.search_input)
        search_layout.addWidget(self.planet_sync_lbl)
        search_layout.addWidget(self.planet_sync_combo)
        search_layout.addWidget(self.lbl_sync_result)

        btn_export_img = QPushButton("Export Calendar Image")
        btn_export_img.clicked.connect(self.export_calendar_image)
        search_layout.addWidget(btn_export_img)

        self.layout.addLayout(search_layout)

        # Search Results Dropdown/List (hidden by default)
        self.search_results_list = QListWidget()
        self.search_results_list.setMaximumHeight(120)
        self.search_results_list.setVisible(False)
        self.search_results_list.itemClicked.connect(self.jump_to_search_result)
        self.layout.addWidget(self.search_results_list)

        # Main Content Split
        content_layout = QHBoxLayout()

        # Left: Calendar Grid
        self.calendar_scroll = QScrollArea()
        self.calendar_scroll.setWidgetResizable(True)
        self.calendar_widget = QWidget()
        self.calendar_grid = QGridLayout(self.calendar_widget)
        self.calendar_scroll.setWidget(self.calendar_widget)
        content_layout.addWidget(self.calendar_scroll, 2)


        # Right: Day Details & Events
        details_layout = QVBoxLayout()
        details_layout.setSpacing(15)

        # Day Details Group
        group_day = QGroupBox(translator.t("select_day"))
        day_layout = QVBoxLayout(group_day)
        self.lbl_day_title = QLabel(translator.t("select_day"))
        self.lbl_day_title.setStyleSheet("font-size: 16px; font-weight: bold; color: #89b4fa;")

        self.lbl_earth_date = QLabel("")
        self.lbl_earth_date.setStyleSheet("color: #a6e3a1; font-weight: bold;")
        self.lbl_earth_date.setVisible(False)

        self.lbl_astro_info = QLabel("")
        self.lbl_astro_info.setWordWrap(True)

        self.lbl_sun_info = QLabel("")
        self.lbl_sun_info.setWordWrap(True)

        day_layout.addWidget(self.lbl_day_title)
        day_layout.addWidget(self.lbl_earth_date)
        day_layout.addWidget(self.lbl_astro_info)
        day_layout.addWidget(self.lbl_sun_info)
        details_layout.addWidget(group_day)

        # Events List Group
        group_list = QGroupBox(translator.t("lbl_events"))
        list_layout = QVBoxLayout(group_list)
        self.event_list = EventListWidget(self)
        self.event_list.itemClicked.connect(self.load_event)
        list_layout.addWidget(self.event_list)
        details_layout.addWidget(group_list, 1) # Give it stretch

        # Event Editor Group
        self.event_editor = QGroupBox("Event Editor")
        self.ev_layout = QFormLayout(self.event_editor)
        self.ev_layout.setSpacing(10)
        self.ev_title = QLineEdit()

        self.ev_start = TimeInputWidget(self.main_window.world.time_units, self.main_window.world.base_tick_name)

        self.ev_duration_days = QSpinBox()
        self.ev_duration_days.setMinimum(0)
        self.ev_duration_days.setMaximum(99999)
        self.ev_duration_days.setToolTip("Duration of the event in days.")

        self.ev_chars = QLineEdit()
        self.ev_chars.setToolTip(translator.t("tt_ev_chars"))
        self.ev_loc = QLineEdit()

        # Categories & Color
        self.ev_cat_layout = QHBoxLayout()
        self.ev_category = QComboBox()
        self.ev_category.addItems(["General", "Battle", "Birth", "Death", "Travel", "Politics", "Magic"])
        self.ev_category.setEditable(True)
        self.ev_color = QComboBox()
        self.ev_color.addItems(["#89b4fa", "#f38ba8", "#a6e3a1", "#f9e2af", "#cba6f7", "#fab387"])
        self.ev_cat_layout.addWidget(self.ev_category)
        self.ev_cat_layout.addWidget(self.ev_color)

        # Recurrence
        from PyQt6.QtWidgets import QCheckBox
        self.ev_rec_layout = QHBoxLayout()
        self.chk_recurring = QCheckBox("Repeat every")
        self.spin_recur_interval = QSpinBox()
        self.spin_recur_interval.setMinimum(1)
        self.spin_recur_interval.setMaximum(99999)
        self.spin_recur_interval.setValue(365)
        self.spin_recur_interval.setSuffix(" days")
        self.ev_rec_layout.addWidget(self.chk_recurring)
        self.ev_rec_layout.addWidget(self.spin_recur_interval)

        self.ev_notes = QTextEdit()
        self.ev_notes.setMaximumHeight(80)

        self.ev_layout.addRow(translator.t("ev_title"), self.ev_title)
        self.ev_layout.addRow("Start Time", self.ev_start)
        self.ev_layout.addRow("Duration (Days)", self.ev_duration_days)
        self.ev_layout.addRow("Recurrence", self.ev_rec_layout)
        self.ev_layout.addRow("Category/Color", self.ev_cat_layout)
        self.ev_layout.addRow(translator.t("ev_chars"), self.ev_chars)
        self.ev_layout.addRow(translator.t("ev_loc"), self.ev_loc)
        self.ev_layout.addRow(translator.t("ev_notes"), self.ev_notes)

        btn_ev_layout = QHBoxLayout()
        btn_ev_save = QPushButton(translator.t("btn_ev_save"))
        btn_ev_save.clicked.connect(self.save_event)
        btn_ev_save.setObjectName("primaryAction")
        btn_ev_new = QPushButton(translator.t("btn_ev_new"))
        btn_ev_new.clicked.connect(self.new_event)

        self.btn_ev_delete = QPushButton(translator.t("btn_ev_delete"))
        self.btn_ev_delete.clicked.connect(self.delete_event)
        self.btn_ev_delete.setStyleSheet("background-color: #f38ba8; color: #11111b;")
        self.btn_ev_delete.setVisible(False)

        btn_ev_layout.addWidget(btn_ev_new)
        btn_ev_layout.addWidget(self.btn_ev_delete)
        btn_ev_layout.addWidget(btn_ev_save)
        self.ev_layout.addRow(btn_ev_layout)

        details_layout.addWidget(self.event_editor)

        right_panel = QWidget()
        right_panel.setLayout(details_layout)
        right_panel.setMinimumWidth(350)
        content_layout.addWidget(right_panel, 1)

        self.layout.addLayout(content_layout)

        self.current_event = None

    def refresh_view(self):
        self.engine = TimeEngine(self.main_window.world)
        self.astro = AstronomyModel(self.main_window.world)

        # Re-build time input widget just in case time_units changed in editor
        self.ev_layout.removeRow(self.ev_start)
        self.ev_start.deleteLater()
        self.ev_start = TimeInputWidget(self.main_window.world.time_units, self.main_window.world.base_tick_name)
        self.ev_layout.insertRow(1, "Start Time", self.ev_start)

        # Update sync combo
        self.planet_sync_combo.clear()
        for p in self.main_window.world.planets:
            self.planet_sync_combo.addItem(p.name, userData=p.id)

        self.render_calendar()

    def change_year(self, delta):
        self.current_year += delta
        self.render_calendar()

    def change_month(self, delta):
        world = self.main_window.world
        if not world.months:
            return

        self.current_month_index += delta
        if self.current_month_index >= len(world.months):
            self.current_month_index = 0
            self.current_year += 1
        elif self.current_month_index < 0:
            self.current_month_index = len(world.months) - 1
            self.current_year -= 1

        self.render_calendar()

    def render_calendar(self):
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
                    from PyQt6.QtWidgets import QSizePolicy
                    btn.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
                    btn.setMinimumSize(30, 30)
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
                            btn.setText(f"{day}\n📍")
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
                from PyQt6.QtWidgets import QSizePolicy
                btn.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
                btn.setMinimumSize(60, 60)
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
                        btn.setText(f"{day}\n🌘")

                    if events_today > 0:
                        base_text = str(day)
                        if moon_tooltip: base_text += "\n🌘"
                        btn.setText(f"{base_text}\n({events_today} 📌)")

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
        self.select_day(tick)

    def select_day(self, tick):
        self.selected_tick = tick
        self.new_event()
        p_planet = self.engine.get_primary_planet()
        if not p_planet:
            return

        date_info = self.engine.tick_to_date(p_planet, tick)

        m_name = date_info['month'].name if date_info['month'] else "Intercalary"
        e_name = date_info['era'].name if date_info.get('era') else ""

        self.lbl_day_title.setText(f"{e_name} Year {date_info['year']}, {m_name} {date_info['day_of_month']}")

        # Earth Sync
        earth_dt = self.engine.tick_to_earth_date(tick)
        if earth_dt:
            self.lbl_earth_date.setText(f"{translator.t('lbl_earth_date')} {earth_dt.strftime('%Y-%m-%d %H:%M')}")
            self.lbl_earth_date.setVisible(True)
        else:
            self.lbl_earth_date.setVisible(False)

        # Astro Info
        astro_text = []
        for moon in self.main_window.world.moons:
            mp = self.astro.get_moon_phase(moon, date_info['total_days'])
            astro_text.append(f"{moon.name}: {mp['phase_name']} ({int(mp['illumination']*100)}%)")
        self.lbl_astro_info.setText(" | ".join(astro_text))

        # Sun Info (Graphical text representation for now as Qt HTML doesn't support linear-gradient)
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

            sun_layout_html += f"""
            <div style='margin-bottom: 5px;'>
                <span style='color: #cdd6f4; font-size: 11px;'>☀️ {sun.name}</span><br/>
                <span style='font-size: 8px;'>{bar}</span>
                <div style='display: flex; justify-content: space-between; font-size: 9px; color: #a6adc8;'>
                    <span>Dawn ({sun.twilight_dawn_ticks})</span>
                    <span>Dusk ({sun.twilight_dusk_ticks})</span>
                </div>
            </div>
            """

        if not self.main_window.world.suns:
            if hasattr(self, 'lbl_sun_info'):
                self.lbl_sun_info.setText("")
        else:
            if not hasattr(self, 'lbl_sun_info'):
                pass
            else:
                self.lbl_sun_info.setText(sun_layout_html)

        self.update_sync_display()
        self.load_events_for_day(tick, p_planet.day_length_ticks)

    def update_sync_display(self):
        target_p_id = self.planet_sync_combo.currentData()
        if not target_p_id or self.selected_tick == 0:
            return

        target_p = next((p for p in self.main_window.world.planets if p.id == target_p_id), None)
        if target_p:
            d_info = self.engine.tick_to_date(target_p, self.selected_tick)
            m_name = d_info['month'].name if d_info.get('month') else "N/A"
            time_str = self.engine.format_time(d_info['time_of_day_ticks'])
            self.lbl_sync_result.setText(f"➔ Yr {d_info['year']}, {m_name} {d_info['day_of_month']}, Time: {time_str}")

    def load_events_for_day(self, tick, day_length):
        self.event_list.clear()
        start_bound = tick - (tick % day_length)
        end_bound = start_bound + day_length

        for ev in self.main_window.world.events:
            occurs_today = False
            if ev.start_tick >= start_bound and ev.start_tick < end_bound:
                occurs_today = True
            elif getattr(ev, 'is_recurring', False) and ev.start_tick < end_bound:
                p_planet = self.engine.get_primary_planet()
                day_len = p_planet.day_length_ticks if p_planet and p_planet.day_length_ticks > 0 else 86400
                interval = getattr(ev, 'recurrence_interval_days', 365) * day_len
                if interval > 0:
                    start_of_event_day = ev.start_tick - (ev.start_tick % day_len)
                    diff = start_bound - start_of_event_day
                    if diff % interval < day_len and diff >= 0:
                        occurs_today = True

            if occurs_today:
                title = ev.title
                if getattr(ev, 'is_recurring', False) and ev.start_tick < start_bound:
                    title += " (Recurring)"

                list_item = QListWidgetItem(title)
                list_item.setData(Qt.ItemDataRole.UserRole, ev.id)
                from PyQt6.QtGui import QColor, QBrush
                if getattr(ev, "color", None):
                    list_item.setForeground(QBrush(QColor(ev.color)))
                self.event_list.addItem(list_item)

    def move_event_to_day(self, event_id: str, new_day_tick: int):
        for ev in self.main_window.world.events:
            if ev.id == event_id:
                # Calculate duration
                duration = ev.end_tick - ev.start_tick
                # We need to preserve time of day. Find old time of day.
                p_planet = self.engine.get_primary_planet()
                old_tod = ev.start_tick % p_planet.day_length_ticks if p_planet else 0

                ev.start_tick = new_day_tick + old_tod
                ev.end_tick = ev.start_tick + duration

                self.main_window.mark_unsaved()
                self.refresh_view()
                break

    def load_event(self, item):
        event_id = item.data(Qt.ItemDataRole.UserRole)
        for ev in self.main_window.world.events:
            if ev.id == event_id:
                self.current_event = ev
                self.ev_title.setText(ev.title)

                # Convert tick back to time_of_day and duration
                p_planet = self.engine.get_primary_planet()
                day_len = p_planet.day_length_ticks if p_planet and p_planet.day_length_ticks > 0 else 86400
                time_of_day = ev.start_tick % day_len
                duration_ticks = max(0, ev.end_tick - ev.start_tick)
                duration_days = duration_ticks // day_len

                self.ev_start.set_ticks(time_of_day)
                self.ev_duration_days.setValue(duration_days)

                self.ev_chars.setText(", ".join(ev.characters))
                self.ev_loc.setText(ev.location)
                self.ev_notes.setText(ev.notes)

                cat = getattr(ev, "category", "")
                idx = self.ev_category.findText(cat)
                if idx >= 0:
                    self.ev_category.setCurrentIndex(idx)
                else:
                    self.ev_category.setCurrentText(cat)

                col = getattr(ev, "color", "#89b4fa")
                idx = self.ev_color.findText(col)
                if idx >= 0:
                    self.ev_color.setCurrentIndex(idx)
                else:
                    self.ev_color.setCurrentText(col)

                is_rec = getattr(ev, 'is_recurring', False)
                self.chk_recurring.setChecked(is_rec)
                self.spin_recur_interval.setValue(getattr(ev, 'recurrence_interval_days', 365))
                self.btn_ev_delete.setVisible(True)
                break

    def new_event(self):
        self.current_event = None
        self.ev_title.clear()
        self.ev_start.set_ticks(0)
        self.ev_duration_days.setValue(0)
        self.chk_recurring.setChecked(False)
        self.spin_recur_interval.setValue(365)
        self.ev_chars.clear()
        self.ev_loc.clear()
        self.ev_notes.clear()
        self.ev_category.setCurrentIndex(0)
        self.ev_color.setCurrentIndex(0)
        self.btn_ev_delete.setVisible(False)

    def save_event(self):
        if not self.current_event:
            self.current_event = Event()
            self.main_window.world.events.append(self.current_event)

        self.current_event.title = self.ev_title.text()

        p_planet = self.engine.get_primary_planet()
        day_len = p_planet.day_length_ticks if p_planet and p_planet.day_length_ticks > 0 else 86400

        # We need the absolute start of the day
        start_of_day_tick = self.selected_tick - (self.selected_tick % day_len)

        # Apply the time of day from input widget
        time_of_day_ticks = self.ev_start.get_ticks()

        self.current_event.start_tick = start_of_day_tick + time_of_day_ticks
        duration_ticks = self.ev_duration_days.value() * day_len
        self.current_event.end_tick = self.current_event.start_tick + duration_ticks

        self.current_event.characters = [c.strip() for c in self.ev_chars.text().split(",") if c.strip()]
        self.current_event.location = self.ev_loc.text()
        self.current_event.category = self.ev_category.currentText()
        self.current_event.color = self.ev_color.currentText()
        self.current_event.notes = self.ev_notes.toPlainText()

        self.current_event.is_recurring = self.chk_recurring.isChecked()
        self.current_event.recurrence_interval_days = self.spin_recur_interval.value()

        self.main_window.mark_unsaved()

        p_planet = self.engine.get_primary_planet()
        self.load_events_for_day(self.selected_tick, p_planet.day_length_ticks if p_planet else 86400)
        self.render_calendar()

    def delete_event(self):
        if self.current_event in self.main_window.world.events:
            self.main_window.world.events.remove(self.current_event)
            self.main_window.mark_unsaved()
            self.new_event()

            p_planet = self.engine.get_primary_planet()
            self.load_events_for_day(self.selected_tick, p_planet.day_length_ticks if p_planet else 86400)
            self.render_calendar()

    def export_calendar_image(self):
        from PyQt6.QtWidgets import QFileDialog, QMessageBox
        from PyQt6.QtGui import QPixmap
        import os

        file_path, _ = QFileDialog.getSaveFileName(self, "Export Calendar as Image", "", "PNG Images (*.png)")
        if file_path:
            # Grab the widget containing the calendar grid
            pixmap = self.calendar_grid.parentWidget().grab()
            if pixmap.save(file_path, "PNG"):
                QMessageBox.information(self, "Success", f"Calendar exported successfully to {os.path.basename(file_path)}!")
            else:
                QMessageBox.critical(self, "Error", "Failed to export calendar image.")

    def perform_search(self):
        query = self.search_input.text().lower().strip()
        self.search_results_list.clear()

        if not query:
            self.search_results_list.setVisible(False)
            self.render_calendar()
            return

        self.search_results_list.setVisible(True)

        # Search events
        for ev in self.main_window.world.events:
            match = False
            if query in ev.title.lower() or query in ev.location.lower() or query in ev.notes.lower():
                match = True
            for char in ev.characters:
                if query in char.lower():
                    match = True
                    break

            if match:
                item = QListWidgetItem(f"{ev.title} (Tick {ev.start_tick})")
                item.setData(Qt.ItemDataRole.UserRole, ev)
                self.search_results_list.addItem(item)

        self.render_calendar() # Re-render to highlight matches

    def jump_to_search_result(self, item):
        ev = item.data(Qt.ItemDataRole.UserRole)
        if not ev:
            return

        p_planet = self.engine.get_primary_planet()
        if not p_planet:
            return

        # Select the day
        day_tick = ev.start_tick - (ev.start_tick % p_planet.day_length_ticks)

        # Determine year and month for calendar view sync
        date_info = self.engine.tick_to_date(p_planet, day_tick)

        # Attempt to sync calendar view to the event's month
        self.current_year = date_info['year']
        if date_info['month']:
            for i, m in enumerate(self.main_window.world.months):
                if m.id == date_info['month'].id:
                    self.current_month_index = i
                    break

        self.render_calendar()
        self.select_day(day_tick)

        # Select event in list
        for i in range(self.event_list.count()):
            list_item = self.event_list.item(i)
            if list_item.data(Qt.ItemDataRole.UserRole) == ev.id:
                self.event_list.setCurrentRow(i)
                self.load_event(list_item)
                break
