from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                             QPushButton, QGridLayout, QScrollArea, QFrame,
                             QLineEdit, QListWidget, QListWidgetItem, QFormLayout, QTextEdit, QComboBox)
from PyQt6.QtCore import Qt

from cce.core.engine import TimeEngine
from cce.core.astronomy import AstronomyModel
from cce.core.models import Event

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
        self.btn_back = QPushButton("🔙 Editor")
        self.btn_back.clicked.connect(self.main_window.switch_to_editor)

        self.btn_prev_year = QPushButton("<< Year")
        self.btn_prev_month = QPushButton("< Month")
        self.lbl_current_view = QLabel("Year 0, Month 1")
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
        header_layout.addStretch()

        self.layout.addLayout(header_layout)

        # Search & Sync
        search_layout = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search events, characters, locations...")
        self.search_input.textChanged.connect(self.perform_search)

        self.planet_sync_lbl = QLabel("Sync:")
        self.planet_sync_combo = QComboBox()
        self.planet_sync_combo.currentIndexChanged.connect(self.update_sync_display)
        self.lbl_sync_result = QLabel("")

        search_layout.addWidget(self.search_input)
        search_layout.addWidget(self.planet_sync_lbl)
        search_layout.addWidget(self.planet_sync_combo)
        search_layout.addWidget(self.lbl_sync_result)

        self.layout.addLayout(search_layout)

        # Search Results Dropdown/List (hidden by default)
        self.search_results_list = QListWidget()
        self.search_results_list.setMaximumHeight(100)
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
        self.lbl_day_title = QLabel("Select a Day")
        self.lbl_day_title.setStyleSheet("font-size: 16px; font-weight: bold;")
        self.lbl_astro_info = QLabel("")

        self.event_list = QListWidget()
        self.event_list.itemClicked.connect(self.load_event)

        # Event Editor
        self.event_editor = QWidget()
        ev_layout = QFormLayout(self.event_editor)
        self.ev_title = QLineEdit()
        self.ev_start = QLineEdit()
        self.ev_start.setPlaceholderText("Start Tick")
        self.ev_end = QLineEdit()
        self.ev_end.setPlaceholderText("End Tick")
        self.ev_chars = QLineEdit()
        self.ev_loc = QLineEdit()
        self.ev_notes = QTextEdit()

        ev_layout.addRow("Title:", self.ev_title)
        ev_layout.addRow("Start Tick:", self.ev_start)
        ev_layout.addRow("End Tick:", self.ev_end)
        ev_layout.addRow("Characters:", self.ev_chars)
        ev_layout.addRow("Location:", self.ev_loc)
        ev_layout.addRow("Notes:", self.ev_notes)

        btn_ev_layout = QHBoxLayout()
        btn_ev_save = QPushButton("Save Event")
        btn_ev_save.clicked.connect(self.save_event)
        btn_ev_new = QPushButton("New Event")
        btn_ev_new.clicked.connect(self.new_event)
        btn_ev_layout.addWidget(btn_ev_new)
        btn_ev_layout.addWidget(btn_ev_save)
        ev_layout.addRow(btn_ev_layout)

        details_layout.addWidget(self.lbl_day_title)
        details_layout.addWidget(self.lbl_astro_info)
        details_layout.addWidget(QLabel("Events:"))
        details_layout.addWidget(self.event_list)
        details_layout.addWidget(self.event_editor)

        right_panel = QWidget()
        right_panel.setLayout(details_layout)
        content_layout.addWidget(right_panel, 1)

        self.layout.addLayout(content_layout)

        self.current_event = None

    def refresh_view(self):
        self.engine = TimeEngine(self.main_window.world)
        self.astro = AstronomyModel(self.main_window.world)

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
            self.lbl_current_view.setText("No months defined.")
            return

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

        days_in_month = month.days
        # Apply leap rules to this month
        for rule in world.leap_rules:
            if rule.interval_years > 0 and self.current_year % rule.interval_years == 0:
                is_exception = False
                if rule.exception_interval and rule.exception_interval > 0 and self.current_year % rule.exception_interval == 0:
                    is_exception = True
                if rule.month_id_to_append == month.id:
                    days_in_month += rule.exception_days if is_exception else rule.days_to_add

        p_planet = self.engine.get_primary_planet()

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
            btn = QPushButton(str(day))
            btn.setFixedSize(60, 60)
            btn.setStyleSheet(f"background-color: {month.color};")

            if p_planet:
                exact_tick = self.engine.date_to_tick(p_planet, self.current_year, self.current_month_index, day)

                # Visual badge for events
                events_today = 0
                search_match = False
                day_end_tick = exact_tick + p_planet.day_length_ticks
                query = self.search_input.text().lower().strip()

                for ev in world.events:
                    if ev.start_tick >= exact_tick and ev.start_tick < day_end_tick:
                        events_today += 1
                        if query:
                            if query in ev.title.lower() or query in ev.location.lower() or query in ev.notes.lower():
                                search_match = True
                            for char in ev.characters:
                                if query in char.lower():
                                    search_match = True

                if events_today > 0:
                    btn.setText(f"{day}\n({events_today} 📌)")
                    if search_match:
                        btn.setStyleSheet(f"background-color: yellow; font-weight: bold; border: 3px solid #ffaa00;")
                    else:
                        btn.setStyleSheet(f"background-color: {month.color}; font-weight: bold; border: 2px solid red;")

                btn.clicked.connect(lambda checked, t=exact_tick: self.select_day(t))

            self.calendar_grid.addWidget(btn, row, col)
            col += 1
            if col >= cols_per_row:
                col = 0
                row += 1

    def select_day(self, tick):
        self.selected_tick = tick
        p_planet = self.engine.get_primary_planet()
        if not p_planet:
            return

        date_info = self.engine.tick_to_date(p_planet, tick)

        m_name = date_info['month'].name if date_info['month'] else "Intercalary"
        e_name = date_info['era'].name if date_info.get('era') else ""

        self.lbl_day_title.setText(f"{e_name} Year {date_info['year']}, {m_name} {date_info['day_of_month']}")

        # Astro Info
        astro_text = []
        for moon in self.main_window.world.moons:
            mp = self.astro.get_moon_phase(moon, date_info['total_days'])
            astro_text.append(f"{moon.name}: {mp['phase_name']} ({int(mp['illumination']*100)}%)")
        self.lbl_astro_info.setText(" | ".join(astro_text))

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
            if ev.start_tick >= start_bound and ev.start_tick < end_bound:
                self.event_list.addItem(ev.title)

    def load_event(self, item):
        title = item.text()
        for ev in self.main_window.world.events:
            if ev.title == title:
                self.current_event = ev
                self.ev_title.setText(ev.title)
                self.ev_start.setText(str(ev.start_tick))
                self.ev_end.setText(str(ev.end_tick))
                self.ev_chars.setText(", ".join(ev.characters))
                self.ev_loc.setText(ev.location)
                self.ev_notes.setText(ev.notes)
                break

    def new_event(self):
        self.current_event = None
        self.ev_title.clear()
        self.ev_start.setText(str(self.selected_tick))
        self.ev_end.setText(str(self.selected_tick))
        self.ev_chars.clear()
        self.ev_loc.clear()
        self.ev_notes.clear()

    def save_event(self):
        if not self.current_event:
            self.current_event = Event()
            self.main_window.world.events.append(self.current_event)

        self.current_event.title = self.ev_title.text()
        try:
            self.current_event.start_tick = int(self.ev_start.text())
            self.current_event.end_tick = int(self.ev_end.text())
        except ValueError:
            from PyQt6.QtWidgets import QMessageBox
            QMessageBox.warning(self, 'Invalid Input', 'Tick values must be integers.')
            return
        self.current_event.characters = [c.strip() for c in self.ev_chars.text().split(",") if c.strip()]
        self.current_event.location = self.ev_loc.text()
        self.current_event.notes = self.ev_notes.toPlainText()

        p_planet = self.engine.get_primary_planet()
        self.load_events_for_day(self.selected_tick, p_planet.day_length_ticks if p_planet else 86400)

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
        items = self.event_list.findItems(ev.title, Qt.MatchFlag.MatchExactly)
        if items:
            self.event_list.setCurrentItem(items[0])
            self.load_event(items[0])
