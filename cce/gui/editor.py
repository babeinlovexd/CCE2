from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                             QPushButton, QTabWidget, QLineEdit, QFormLayout,
                             QTableWidget, QTableWidgetItem, QHeaderView, QCheckBox,
                             QFileDialog, QMessageBox, QComboBox)
from PyQt6.QtCore import Qt

from cce.core.models import TimeUnit, Planet, Era, Month, Weekday, Holiday, LeapRule, Sun, Moon
from cce.core.storage import save_world, load_world

class EditorWidget(QWidget):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.layout = QVBoxLayout(self)

        # Top Bar
        top_bar = QHBoxLayout()
        self.btn_save = QPushButton("Save Project")
        self.btn_open = QPushButton("Open Project")
        self.btn_generate = QPushButton("🚀 Generate Calendar & Open Viewer")

        self.btn_save.clicked.connect(self.save_project)
        self.btn_open.clicked.connect(self.open_project)
        self.btn_generate.clicked.connect(self.main_window.switch_to_viewer)

        top_bar.addWidget(self.btn_open)
        top_bar.addWidget(self.btn_save)
        top_bar.addStretch()
        top_bar.addWidget(self.btn_generate)

        self.layout.addLayout(top_bar)

        # Tabs
        self.tabs = QTabWidget()

        self.tab_world = QWidget()
        self.tab_planets = QWidget()
        self.tab_calendar = QWidget()
        self.tab_holidays = QWidget()
        self.tab_astronomy = QWidget()

        self.tabs.addTab(self.tab_world, "World & Units")
        self.tabs.addTab(self.tab_planets, "Planets & Orbit")
        self.tabs.addTab(self.tab_calendar, "Eras, Months & Weekdays")
        self.tabs.addTab(self.tab_holidays, "Holidays & Leap Rules")
        self.tabs.addTab(self.tab_astronomy, "Suns & Moons")

        self.layout.addWidget(self.tabs)

        self.setup_world_tab()
        self.setup_planets_tab()
        self.setup_calendar_tab()
        self.setup_holidays_tab()
        self.setup_astronomy_tab()

    def refresh_view(self):
        w = self.main_window.world
        self.world_name_input.setText(w.name)
        self.base_tick_input.setText(w.base_tick_name)
        self.populate_time_units()
        self.populate_planets()
        self.populate_months()
        self.populate_weekdays()
        self.populate_eras()
        self.populate_holidays()
        self.populate_leap_rules()
        self.populate_suns()
        self.populate_moons()

    def save_project(self):
        # Update basic info before saving
        self.main_window.world.name = self.world_name_input.text()
        self.main_window.world.base_tick_name = self.base_tick_input.text()

        fname, _ = QFileDialog.getSaveFileName(self, "Save World", "", "Worldcal Files (*.worldcal);;All Files (*)")
        if fname:
            try:
                save_world(self.main_window.world, fname)
                QMessageBox.information(self, "Success", "Project saved successfully!")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to save:\n{e}")

    def open_project(self):
        fname, _ = QFileDialog.getOpenFileName(self, "Open World", "", "Worldcal Files (*.worldcal);;All Files (*)")
        if fname:
            try:
                self.main_window.world = load_world(fname)
                self.refresh_view()
                QMessageBox.information(self, "Success", "Project loaded successfully!")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to load:\n{e}")

    # --- World & Units ---
    def setup_world_tab(self):
        layout = QVBoxLayout(self.tab_world)
        form = QFormLayout()

        self.world_name_input = QLineEdit()
        self.base_tick_input = QLineEdit()

        form.addRow("World Name:", self.world_name_input)
        form.addRow("Base Tick Name:", self.base_tick_input)

        layout.addLayout(form)

        layout.addWidget(QLabel("Time Units (e.g. Second, Minute, Hour, Watch)"))
        self.units_table = QTableWidget(0, 3)
        self.units_table.setHorizontalHeaderLabels(["Name", "Abbreviation", "Ticks"])
        self.units_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        layout.addWidget(self.units_table)

        btn_layout = QHBoxLayout()
        btn_add_unit = QPushButton("Add Unit")
        btn_add_unit.clicked.connect(self.add_time_unit)
        btn_del_unit = QPushButton("Remove Selected")
        btn_del_unit.clicked.connect(self.remove_time_unit)

        btn_layout.addWidget(btn_add_unit)
        btn_layout.addWidget(btn_del_unit)
        layout.addLayout(btn_layout)

        self.units_table.itemChanged.connect(self.update_time_units)

    def populate_time_units(self):
        self.units_table.blockSignals(True)
        self.units_table.setRowCount(len(self.main_window.world.time_units))
        for r, u in enumerate(self.main_window.world.time_units):
            self.units_table.setItem(r, 0, QTableWidgetItem(u.name))
            self.units_table.setItem(r, 1, QTableWidgetItem(u.abbreviation))
            self.units_table.setItem(r, 2, QTableWidgetItem(str(u.ticks)))
        self.units_table.blockSignals(False)

    def add_time_unit(self):
        self.main_window.world.time_units.append(TimeUnit(name="New Unit", abbreviation="NU", ticks=1))
        self.populate_time_units()

    def remove_time_unit(self):
        row = self.units_table.currentRow()
        if row >= 0:
            self.main_window.world.time_units.pop(row)
            self.populate_time_units()

    def update_time_units(self):
        for r in range(self.units_table.rowCount()):
            u = self.main_window.world.time_units[r]
            u.name = self.units_table.item(r, 0).text()
            u.abbreviation = self.units_table.item(r, 1).text()
            try:
                u.ticks = int(self.units_table.item(r, 2).text())
            except ValueError:
                QMessageBox.warning(self, 'Invalid Input', 'Please enter a valid number.')
                self.refresh_view()

    # --- Planets ---
    def setup_planets_tab(self):
        layout = QVBoxLayout(self.tab_planets)

        self.planets_table = QTableWidget(0, 4)
        self.planets_table.setHorizontalHeaderLabels(["Name", "Day Length (Ticks)", "Year Length (Days)", "Is Primary"])
        self.planets_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        layout.addWidget(self.planets_table)

        btn_layout = QHBoxLayout()
        btn_add = QPushButton("Add Planet")
        btn_add.clicked.connect(self.add_planet)
        btn_del = QPushButton("Remove Selected")
        btn_del.clicked.connect(self.remove_planet)

        btn_layout.addWidget(btn_add)
        btn_layout.addWidget(btn_del)
        layout.addLayout(btn_layout)

        self.planets_table.itemChanged.connect(self.update_planets)

    def populate_planets(self):
        self.planets_table.blockSignals(True)
        self.planets_table.setRowCount(len(self.main_window.world.planets))
        for r, p in enumerate(self.main_window.world.planets):
            self.planets_table.setItem(r, 0, QTableWidgetItem(p.name))
            self.planets_table.setItem(r, 1, QTableWidgetItem(str(p.day_length_ticks)))
            self.planets_table.setItem(r, 2, QTableWidgetItem(str(p.year_length_days)))

            chk = QTableWidgetItem()
            chk.setFlags(Qt.ItemFlag.ItemIsUserCheckable | Qt.ItemFlag.ItemIsEnabled)
            chk.setCheckState(Qt.CheckState.Checked if p.is_primary else Qt.CheckState.Unchecked)
            self.planets_table.setItem(r, 3, chk)
        self.planets_table.blockSignals(False)

    def add_planet(self):
        self.main_window.world.planets.append(Planet(name="New Planet"))
        self.populate_planets()

    def remove_planet(self):
        row = self.planets_table.currentRow()
        if row >= 0:
            self.main_window.world.planets.pop(row)
            self.populate_planets()

    def update_planets(self, item):
        r = item.row()
        p = self.main_window.world.planets[r]
        p.name = self.planets_table.item(r, 0).text()
        try:
            p.day_length_ticks = int(self.planets_table.item(r, 1).text())
            p.year_length_days = int(self.planets_table.item(r, 2).text())
        except ValueError:
            QMessageBox.warning(self, 'Invalid Input', 'Please enter a valid number.')
            self.refresh_view()

        # Handle exclusive primary selection
        if item.column() == 3:
            is_checked = (item.checkState() == Qt.CheckState.Checked)
            if is_checked:
                for idx, planet in enumerate(self.main_window.world.planets):
                    planet.is_primary = (idx == r)
                self.populate_planets()
            else:
                p.is_primary = False

    # --- Calendar (Eras, Months, Weekdays) ---
    def setup_calendar_tab(self):
        layout = QHBoxLayout(self.tab_calendar)

        # Eras
        era_layout = QVBoxLayout()
        era_layout.addWidget(QLabel("Eras"))
        self.era_table = QTableWidget(0, 4)
        self.era_table.setHorizontalHeaderLabels(["Name", "Abbrev", "Start Year", "Inc Yr 0"])
        era_layout.addWidget(self.era_table)
        btn_add_era = QPushButton("Add Era")
        btn_add_era.clicked.connect(lambda: (self.main_window.world.eras.append(Era(name="New Era")), self.populate_eras()))
        era_layout.addWidget(btn_add_era)
        self.era_table.itemChanged.connect(self.update_eras)

        # Months
        month_layout = QVBoxLayout()
        month_layout.addWidget(QLabel("Months / Seasons"))
        self.month_table = QTableWidget(0, 3)
        self.month_table.setHorizontalHeaderLabels(["Name", "Days", "Color"])
        month_layout.addWidget(self.month_table)
        btn_add_month = QPushButton("Add Month")
        btn_add_month.clicked.connect(lambda: (self.main_window.world.months.append(Month(name="New Month")), self.populate_months()))
        month_layout.addWidget(btn_add_month)
        self.month_table.itemChanged.connect(self.update_months)

        # Weekdays
        weekday_layout = QVBoxLayout()
        weekday_layout.addWidget(QLabel("Weekdays"))
        self.weekday_table = QTableWidget(0, 1)
        self.weekday_table.setHorizontalHeaderLabels(["Name"])
        weekday_layout.addWidget(self.weekday_table)
        btn_add_wd = QPushButton("Add Weekday")
        btn_add_wd.clicked.connect(lambda: (self.main_window.world.weekdays.append(Weekday(name="New Day")), self.populate_weekdays()))
        weekday_layout.addWidget(btn_add_wd)
        self.weekday_table.itemChanged.connect(self.update_weekdays)

        layout.addLayout(era_layout)
        layout.addLayout(month_layout)
        layout.addLayout(weekday_layout)

    def populate_eras(self):
        self.era_table.blockSignals(True)
        self.era_table.setRowCount(len(self.main_window.world.eras))
        for r, e in enumerate(self.main_window.world.eras):
            self.era_table.setItem(r, 0, QTableWidgetItem(e.name))
            self.era_table.setItem(r, 1, QTableWidgetItem(e.abbreviation))
            self.era_table.setItem(r, 2, QTableWidgetItem(str(e.start_year)))
            chk = QTableWidgetItem()
            chk.setFlags(Qt.ItemFlag.ItemIsUserCheckable | Qt.ItemFlag.ItemIsEnabled)
            chk.setCheckState(Qt.CheckState.Checked if e.includes_year_zero else Qt.CheckState.Unchecked)
            self.era_table.setItem(r, 3, chk)
        self.era_table.blockSignals(False)

    def update_eras(self, item):
        r = item.row()
        e = self.main_window.world.eras[r]
        e.name = self.era_table.item(r, 0).text()
        e.abbreviation = self.era_table.item(r, 1).text()
        try:
            e.start_year = int(self.era_table.item(r, 2).text())
        except ValueError:
            QMessageBox.warning(self, 'Invalid Input', 'Please enter a valid number.')
            self.refresh_view()
        if item.column() == 3:
            e.includes_year_zero = (item.checkState() == Qt.CheckState.Checked)

    def populate_months(self):
        self.month_table.blockSignals(True)
        self.month_table.setRowCount(len(self.main_window.world.months))
        for r, m in enumerate(self.main_window.world.months):
            self.month_table.setItem(r, 0, QTableWidgetItem(m.name))
            self.month_table.setItem(r, 1, QTableWidgetItem(str(m.days)))
            self.month_table.setItem(r, 2, QTableWidgetItem(m.color))
        self.month_table.blockSignals(False)

    def update_months(self):
        for r in range(self.month_table.rowCount()):
            m = self.main_window.world.months[r]
            m.name = self.month_table.item(r, 0).text()
            try:
                m.days = int(self.month_table.item(r, 1).text())
            except ValueError:
                QMessageBox.warning(self, 'Invalid Input', 'Please enter a valid number.')
                self.refresh_view()
            m.color = self.month_table.item(r, 2).text()

    def populate_weekdays(self):
        self.weekday_table.blockSignals(True)
        self.weekday_table.setRowCount(len(self.main_window.world.weekdays))
        for r, w in enumerate(self.main_window.world.weekdays):
            self.weekday_table.setItem(r, 0, QTableWidgetItem(w.name))
        self.weekday_table.blockSignals(False)

    def update_weekdays(self):
        for r in range(self.weekday_table.rowCount()):
            w = self.main_window.world.weekdays[r]
            w.name = self.weekday_table.item(r, 0).text()

    # --- Holidays & Leap Rules ---
    def setup_holidays_tab(self):
        layout = QVBoxLayout(self.tab_holidays)

        # Holidays
        layout.addWidget(QLabel("Holidays"))
        self.holiday_table = QTableWidget(0, 4)
        self.holiday_table.setHorizontalHeaderLabels(["Name", "Month (Leave blank for inter-month)", "Day in Month", "Counts as Weekday"])
        self.holiday_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        layout.addWidget(self.holiday_table)
        btn_add_hol = QPushButton("Add Holiday")
        btn_add_hol.clicked.connect(lambda: (self.main_window.world.holidays.append(Holiday(name="New Holiday")), self.populate_holidays()))
        layout.addWidget(btn_add_hol)
        self.holiday_table.itemChanged.connect(self.update_holidays)

        # Leap Rules
        layout.addWidget(QLabel("Leap Rules"))
        self.leap_table = QTableWidget(0, 5)
        self.leap_table.setHorizontalHeaderLabels(["Interval (Years)", "Month ID to Append", "Days to Add", "Exception Interval", "Exception Days"])
        self.leap_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        layout.addWidget(self.leap_table)
        btn_add_leap = QPushButton("Add Leap Rule")
        btn_add_leap.clicked.connect(lambda: (self.main_window.world.leap_rules.append(LeapRule()), self.populate_leap_rules()))
        layout.addWidget(btn_add_leap)
        self.leap_table.itemChanged.connect(self.update_leap_rules)

    def populate_holidays(self):
        self.holiday_table.blockSignals(True)
        self.holiday_table.setRowCount(len(self.main_window.world.holidays))
        for r, h in enumerate(self.main_window.world.holidays):
            self.holiday_table.setItem(r, 0, QTableWidgetItem(h.name))

            # Simple approach for now: put month ID or blank
            month_name = ""
            if h.month_id:
                for m in self.main_window.world.months:
                    if m.id == h.month_id:
                        month_name = m.name
                        break
            if not month_name:
                month_name = h.month_id if h.month_id else ""

            self.holiday_table.setItem(r, 1, QTableWidgetItem(month_name))
            self.holiday_table.setItem(r, 2, QTableWidgetItem(str(h.day_in_month)))
            chk = QTableWidgetItem()
            chk.setFlags(Qt.ItemFlag.ItemIsUserCheckable | Qt.ItemFlag.ItemIsEnabled)
            chk.setCheckState(Qt.CheckState.Checked if h.counts_as_weekday else Qt.CheckState.Unchecked)
            self.holiday_table.setItem(r, 3, chk)
        self.holiday_table.blockSignals(False)

    def update_holidays(self, item):
        r = item.row()
        h = self.main_window.world.holidays[r]
        h.name = self.holiday_table.item(r, 0).text()

        m_name = self.holiday_table.item(r, 1).text()
        if not m_name:
            h.month_id = None
        else:
            # find month by name
            found = False
            for m in self.main_window.world.months:
                if m.name == m_name:
                    h.month_id = m.id
                    found = True
                    break
            if not found:
                h.month_id = m_name # Fallback

        try:
            h.day_in_month = int(self.holiday_table.item(r, 2).text())
        except ValueError:
            QMessageBox.warning(self, 'Invalid Input', 'Please enter a valid number.')
            self.refresh_view()

        if item.column() == 3:
            h.counts_as_weekday = (item.checkState() == Qt.CheckState.Checked)

    def populate_leap_rules(self):
        self.leap_table.blockSignals(True)
        self.leap_table.setRowCount(len(self.main_window.world.leap_rules))
        for r, l in enumerate(self.main_window.world.leap_rules):
            self.leap_table.setItem(r, 0, QTableWidgetItem(str(l.interval_years)))
            self.leap_table.setItem(r, 1, QTableWidgetItem(l.month_id_to_append))
            self.leap_table.setItem(r, 2, QTableWidgetItem(str(l.days_to_add)))
            self.leap_table.setItem(r, 3, QTableWidgetItem(str(l.exception_interval) if l.exception_interval else ""))
            self.leap_table.setItem(r, 4, QTableWidgetItem(str(l.exception_days)))
        self.leap_table.blockSignals(False)

    def update_leap_rules(self):
        for r in range(self.leap_table.rowCount()):
            l = self.main_window.world.leap_rules[r]
            try:
                l.interval_years = int(self.leap_table.item(r, 0).text())
                l.month_id_to_append = self.leap_table.item(r, 1).text()
                l.days_to_add = int(self.leap_table.item(r, 2).text())
                ex_int = self.leap_table.item(r, 3).text()
                l.exception_interval = int(ex_int) if ex_int else None
                l.exception_days = int(self.leap_table.item(r, 4).text())
            except ValueError:
                QMessageBox.warning(self, 'Invalid Input', 'Please enter a valid number.')
                self.refresh_view()

    # --- Astronomy ---
    def setup_astronomy_tab(self):
        layout = QHBoxLayout(self.tab_astronomy)

        # Suns
        sun_layout = QVBoxLayout()
        sun_layout.addWidget(QLabel("Suns"))
        self.sun_table = QTableWidget(0, 3)
        self.sun_table.setHorizontalHeaderLabels(["Name", "Dawn Ticks", "Dusk Ticks"])
        sun_layout.addWidget(self.sun_table)
        btn_add_sun = QPushButton("Add Sun")
        btn_add_sun.clicked.connect(lambda: (self.main_window.world.suns.append(Sun(name="New Sun")), self.populate_suns()))
        sun_layout.addWidget(btn_add_sun)
        self.sun_table.itemChanged.connect(self.update_suns)

        # Moons
        moon_layout = QVBoxLayout()
        moon_layout.addWidget(QLabel("Moons"))
        self.moon_table = QTableWidget(0, 3)
        self.moon_table.setHorizontalHeaderLabels(["Name", "Cycle (Days)", "Phase Offset"])
        moon_layout.addWidget(self.moon_table)
        btn_add_moon = QPushButton("Add Moon")
        btn_add_moon.clicked.connect(lambda: (self.main_window.world.moons.append(Moon(name="New Moon")), self.populate_moons()))
        moon_layout.addWidget(btn_add_moon)
        self.moon_table.itemChanged.connect(self.update_moons)

        layout.addLayout(sun_layout)
        layout.addLayout(moon_layout)

    def populate_suns(self):
        self.sun_table.blockSignals(True)
        self.sun_table.setRowCount(len(self.main_window.world.suns))
        for r, s in enumerate(self.main_window.world.suns):
            self.sun_table.setItem(r, 0, QTableWidgetItem(s.name))
            self.sun_table.setItem(r, 1, QTableWidgetItem(str(s.twilight_dawn_ticks)))
            self.sun_table.setItem(r, 2, QTableWidgetItem(str(s.twilight_dusk_ticks)))
        self.sun_table.blockSignals(False)

    def update_suns(self):
        for r in range(self.sun_table.rowCount()):
            s = self.main_window.world.suns[r]
            s.name = self.sun_table.item(r, 0).text()
            try:
                s.twilight_dawn_ticks = int(self.sun_table.item(r, 1).text())
                s.twilight_dusk_ticks = int(self.sun_table.item(r, 2).text())
            except ValueError:
                QMessageBox.warning(self, 'Invalid Input', 'Please enter a valid number.')
                self.refresh_view()

    def populate_moons(self):
        self.moon_table.blockSignals(True)
        self.moon_table.setRowCount(len(self.main_window.world.moons))
        for r, m in enumerate(self.main_window.world.moons):
            self.moon_table.setItem(r, 0, QTableWidgetItem(m.name))
            self.moon_table.setItem(r, 1, QTableWidgetItem(str(m.cycle_days)))
            self.moon_table.setItem(r, 2, QTableWidgetItem(str(m.phase_offset)))
        self.moon_table.blockSignals(False)

    def update_moons(self):
        for r in range(self.moon_table.rowCount()):
            m = self.main_window.world.moons[r]
            m.name = self.moon_table.item(r, 0).text()
            try:
                m.cycle_days = float(self.moon_table.item(r, 1).text())
                m.phase_offset = float(self.moon_table.item(r, 2).text())
            except ValueError:
                QMessageBox.warning(self, 'Invalid Input', 'Please enter a valid number.')
                self.refresh_view()
