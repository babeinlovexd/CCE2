from PyQt6.QtWidgets import (QWidget, QGroupBox, QVBoxLayout, QHBoxLayout, QLabel,
                             QPushButton, QTabWidget, QLineEdit, QFormLayout,
                             QTableWidget, QTableWidgetItem, QHeaderView, QCheckBox,
                             QFileDialog, QMessageBox, QComboBox, QSpinBox, QScrollArea, QGridLayout)
from PyQt6.QtCore import Qt

from cce.core.models import TimeUnit, Planet, Era, Month, Weekday, Holiday, LeapRule, Sun, Moon
from cce.core.storage import save_world, load_world
from cce.core.engine import TimeEngine
from .translations import translator

class EditorWidget(QWidget):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.layout = QVBoxLayout(self)

        # Top Bar
        top_bar = QHBoxLayout()
        self.btn_save = QPushButton(translator.t("btn_save"))
        self.btn_open = QPushButton(translator.t("btn_open"))
        self.btn_presets = QPushButton(translator.t("btn_presets"))
        self.btn_sample = QPushButton(translator.t("btn_sample"))
        self.btn_export = QPushButton(translator.t("btn_export"))
        self.btn_generate = QPushButton(translator.t("btn_generate"))
        self.btn_generate.setObjectName("primaryAction")

        self.btn_save.clicked.connect(self.save_project)
        self.btn_open.clicked.connect(self.open_project)
        self.btn_presets.clicked.connect(self.open_preset_wizard)
        self.btn_sample.clicked.connect(self.load_sample_world)
        self.btn_export.clicked.connect(self.export_timeline)
        self.btn_generate.clicked.connect(self.main_window.switch_to_viewer)

        top_bar.addWidget(self.btn_open)
        top_bar.addWidget(self.btn_save)
        top_bar.addWidget(self.btn_presets)
        top_bar.addWidget(self.btn_sample)
        top_bar.addWidget(self.btn_export)
        top_bar.addStretch()
        self.btn_generate.setMinimumHeight(35)
        top_bar.addWidget(self.btn_generate)

        self.layout.addLayout(top_bar)

        # Split Layout: Tabs on Left, Live Preview on Right
        main_split = QHBoxLayout()

        self.tabs = QTabWidget()

        self.tab_world = QWidget()
        self.tab_planets = QWidget()
        self.tab_calendar = QWidget()
        self.tab_holidays = QWidget()
        self.tab_astronomy = QWidget()

        self.tabs.addTab(self.tab_world, translator.t("tab_world"))
        self.tabs.addTab(self.tab_planets, translator.t("tab_planets"))
        self.tabs.addTab(self.tab_calendar, translator.t("tab_calendar"))
        self.tabs.addTab(self.tab_holidays, translator.t("tab_holidays"))
        self.tabs.addTab(self.tab_astronomy, translator.t("tab_astronomy"))

        main_split.addWidget(self.tabs, 3)

        # Live Preview Panel
        preview_group = QGroupBox(translator.t("live_preview_title"))
        preview_group.setMinimumWidth(220)
        preview_group.setMaximumWidth(300)
        preview_layout = QVBoxLayout(preview_group)

        self.lbl_preview_info = QLabel("")
        self.lbl_preview_info.setStyleSheet("font-weight: bold; color: #00c0f0;")
        preview_layout.addWidget(self.lbl_preview_info)

        self.preview_scroll = QScrollArea()
        self.preview_scroll.setWidgetResizable(True)
        self.preview_widget = QWidget()
        self.preview_grid = QGridLayout(self.preview_widget)
        self.preview_scroll.setWidget(self.preview_widget)
        preview_layout.addWidget(self.preview_scroll)

        main_split.addWidget(preview_group, 2)

        self.layout.addLayout(main_split)

        self.setup_world_tab()
        self.setup_planets_tab()
        self.setup_calendar_tab()
        self.setup_holidays_tab()
        self.setup_astronomy_tab()

    def refresh_view(self):
        w = self.main_window.world
        self.world_name_input.setText(w.name)
        self.base_tick_input.setText(w.base_tick_name)

        # Earth Sync
        self.chk_earth_sync.blockSignals(True)
        self.chk_earth_sync.setChecked(w.earth_sync_enabled)
        self.chk_earth_sync.blockSignals(False)
        self.earth_epoch_input.setText(w.earth_epoch_iso)
        self.real_seconds_input.setText(str(w.real_seconds_per_tick))
        self.update_earth_sync_state()

        self.populate_time_units()
        self.populate_planets()
        self.populate_months()
        self.populate_weekdays()
        self.populate_eras()
        self.populate_holidays()
        self.populate_leap_rules()
        self.populate_suns()
        self.populate_moons()
        self.update_live_preview()

    def update_live_preview(self):
        # Clear grid
        for i in reversed(range(self.preview_grid.count())):
            widget = self.preview_grid.itemAt(i).widget()
            if widget:
                widget.setParent(None)

        world = self.main_window.world
        if not world.months:
            self.lbl_preview_info.setText("No months defined.")
            return

        m0 = world.months[0]
        self.lbl_preview_info.setText(f"Month 1: {m0.name} ({m0.days} days)")

        # Weekdays header
        week_len = len(world.weekdays)
        cols = week_len if week_len > 0 else 7
        if week_len > 0:
            for i, wd in enumerate(world.weekdays):
                lbl = QLabel(wd.name[:3])
                lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
                lbl.setStyleSheet("font-size: 11px; font-weight: bold; color: #a6adc8;")
                self.preview_grid.addWidget(lbl, 0, i)

        row, col = 1, 0
        for day in range(1, min(m0.days + 1, 32)): # Limit mini preview to max 31 days for compactness
            btn = QPushButton(str(day))
            btn.setFixedSize(28, 28)
            btn.setStyleSheet(f"background-color: {m0.color}; font-size: 10px;")
            self.preview_grid.addWidget(btn, row, col)
            col += 1
            if col >= cols:
                col = 0
                row += 1


    def export_timeline(self):
        from cce.core.exporter import export_to_ical, export_to_csv, export_to_json

        self.flush_state_to_model()

        if not self.main_window.world.events:
            QMessageBox.information(self, "Export", "No events to export.")
            return

        filters = "iCalendar Files (*.ics);;CSV Files (*.csv);;JSON Files (*.json);;Markdown Files (*.md);;Text Files (*.txt);;All Files (*)"
        fname, selected_filter = QFileDialog.getSaveFileName(self, translator.t("btn_export"), "timeline.ics", filters)
        if not fname:
            return

        engine = TimeEngine(self.main_window.world)
        p_planet = engine.get_primary_planet()

        try:
            if fname.endswith(".ics") or "iCalendar" in selected_filter:
                content = export_to_ical(self.main_window.world)
            elif fname.endswith(".csv") or "CSV" in selected_filter:
                content = export_to_csv(self.main_window.world)
            elif fname.endswith(".json") or "JSON" in selected_filter:
                content = export_to_json(self.main_window.world)
            else:
                # Default Markdown format
                sorted_events = sorted(self.main_window.world.events, key=lambda e: e.start_tick)
                md_lines = [f"# Timeline: {self.main_window.world.name}\n"]
                for ev in sorted_events:
                    date_str = f"Tick {ev.start_tick}"
                    if p_planet:
                        d_info = engine.tick_to_date(p_planet, ev.start_tick)
                        m_name = d_info['month'].name if d_info.get('month') else "Intercalary"
                        e_name = f"{d_info['era'].name} " if d_info.get('era') else ""
                        date_str = f"{e_name}Year {d_info['year']}, {m_name} {d_info['day_of_month']}"

                    earth_str = ""
                    if self.main_window.world.earth_sync_enabled:
                        earth_dt = engine.tick_to_earth_date(ev.start_tick)
                        if earth_dt:
                            earth_str = f" | 🌍 *{earth_dt.strftime('%Y-%m-%d')}*"

                    chars = f"**Characters:** {', '.join(ev.characters)}\n" if ev.characters else ""
                    loc = f"**Location:** {ev.location}\n" if ev.location else ""

                    md_lines.append(f"## {ev.title}")
                    md_lines.append(f"**Date:** {date_str}{earth_str}\n")
                    if chars: md_lines.append(chars)
                    if loc: md_lines.append(loc)
                    if ev.notes: md_lines.append(f"\n{ev.notes}\n")
                    md_lines.append("\n---\n")

                content = "\n".join(md_lines)

            with open(fname, 'w', encoding='utf-8') as f:
                f.write(content)

            QMessageBox.information(self, "Success", translator.t("export_success"))
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to export:\n{e}")

    def flush_state_to_model(self):
        if hasattr(self, 'world_name_input') and self.world_name_input:
            self.main_window.world.name = self.world_name_input.text()
        if hasattr(self, 'base_tick_input') and self.base_tick_input:
            self.main_window.world.base_tick_name = self.base_tick_input.text()
        if hasattr(self, 'chk_earth_sync') and self.chk_earth_sync:
            self.main_window.world.earth_sync_enabled = self.chk_earth_sync.isChecked()
        if hasattr(self, 'earth_epoch_input') and self.earth_epoch_input:
            dt_str = self.earth_epoch_input.text().strip()
            if len(dt_str) == 10: dt_str += "T00:00:00"
            self.main_window.world.earth_epoch_iso = dt_str
        if hasattr(self, 'real_seconds_input') and self.real_seconds_input:
            try:
                self.main_window.world.real_seconds_per_tick = float(self.real_seconds_input.text())
            except ValueError:
                pass

    def save_project(self):
        # Update basic info before saving
        self.flush_state_to_model()




        fname, _ = QFileDialog.getSaveFileName(self, "Save World", "", "Worldcal Files (*.worldcal);;All Files (*)")
        if fname:
            try:
                save_world(self.main_window.world, fname)
                self.main_window.mark_saved()
                QMessageBox.information(self, "Success", "Project saved successfully!")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to save:\n{e}")

    def load_sample_world(self):
        if not self.main_window.check_unsaved_changes():
            return

        import os
        from cce.core.storage import load_world
        from cce.gui.app import get_resource_path

        sample_path = get_resource_path(os.path.join("assets", "samples", "eldoria.worldcal"))
        if os.path.exists(sample_path):
            try:
                self.main_window.world = load_world(sample_path)
                self.main_window.mark_saved()
                self.refresh_view()
                QMessageBox.information(self, "Sample World Loaded", "Loaded sample world: 'Kingdom of Eldoria'!\nClick 'Generate Calendar' to explore.")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to load sample world:\n{e}")
        else:
            QMessageBox.warning(self, "Not Found", f"Sample world file not found at: {sample_path}")

    def open_preset_wizard(self):
        if not self.main_window.check_unsaved_changes():
            return

        from cce.core.presets import PRESETS
        from PyQt6.QtWidgets import QDialog, QListWidget, QDialogButtonBox, QVBoxLayout, QLabel

        dialog = QDialog(self)
        dialog.setWindowTitle(translator.t("btn_presets"))
        dialog.resize(450, 300)

        dlg_layout = QVBoxLayout(dialog)
        lbl = QLabel("Choose a world preset to quickly bootstrap your calendar:")
        lbl.setWordWrap(True)
        dlg_layout.addWidget(lbl)

        preset_list = QListWidget()
        for key in PRESETS.keys():
            preset_list.addItem(key)
        preset_list.setCurrentRow(0)
        dlg_layout.addWidget(preset_list)

        btn_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        dlg_layout.addWidget(btn_box)

        btn_box.accepted.connect(dialog.accept)
        btn_box.rejected.connect(dialog.reject)

        if dialog.exec() == QDialog.DialogCode.Accepted:
            selected = preset_list.currentItem()
            if selected and selected.text() in PRESETS:
                self.main_window.world = PRESETS[selected.text()]()
                self.main_window.mark_unsaved()
                self.refresh_view()
                QMessageBox.information(self, "Template Applied", f"Successfully loaded template: {selected.text()}")

    def open_project(self):
        if not self.main_window.check_unsaved_changes():
            return

        fname, _ = QFileDialog.getOpenFileName(self, "Open World", "", "Worldcal Files (*.worldcal);;All Files (*)")
        if fname:
            try:
                self.main_window.world = load_world(fname)
                self.main_window.mark_saved()
                self.refresh_view()
                QMessageBox.information(self, "Success", "Project loaded successfully!")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to load:\n{e}")

    # --- World & Units ---
    def setup_world_tab(self):
        layout = QVBoxLayout(self.tab_world)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)

        # Group 1: Basics
        group_basics = QGroupBox(translator.t("tab_world"))
        form = QFormLayout(group_basics)
        form.setSpacing(15)

        self.world_name_input = QLineEdit()
        self.base_tick_input = QLineEdit()

        form.addRow(translator.t("world_name"), self.world_name_input)
        form.addRow(translator.t("base_tick_name"), self.base_tick_input)
        layout.addWidget(group_basics)


        # Group 1.5: Earth Synchronization
        group_earth = QGroupBox(translator.t("lbl_earth_sync"))
        earth_layout = QFormLayout(group_earth)
        earth_layout.setSpacing(15)

        self.chk_earth_sync = QCheckBox(translator.t("chk_earth_sync"))
        self.chk_earth_sync.setToolTip(translator.t("tt_earth_sync"))
        self.earth_epoch_input = QLineEdit()
        self.earth_epoch_input.setToolTip(translator.t("tt_earth_epoch"))
        self.real_seconds_input = QLineEdit()
        self.real_seconds_input.setToolTip(translator.t("tt_real_seconds"))

        earth_layout.addRow("", self.chk_earth_sync)
        earth_layout.addRow(translator.t("lbl_earth_epoch"), self.earth_epoch_input)
        earth_layout.addRow(translator.t("lbl_real_seconds"), self.real_seconds_input)
        layout.addWidget(group_earth)

        # Connect signals
        self.chk_earth_sync.stateChanged.connect(self.update_earth_sync_state)
        self.world_name_input.textChanged.connect(lambda t: (setattr(self.main_window.world, 'name', t), self.main_window.mark_unsaved()))
        self.base_tick_input.textChanged.connect(lambda t: (setattr(self.main_window.world, 'base_tick_name', t), self.main_window.mark_unsaved()))
        self.earth_epoch_input.textChanged.connect(lambda: self.main_window.mark_unsaved())
        self.real_seconds_input.textChanged.connect(lambda: self.main_window.mark_unsaved())


        # Group 2: Time Units
        group_units = QGroupBox(translator.t("time_units_lbl"))
        unit_layout = QVBoxLayout(group_units)

        self.units_table = QTableWidget(0, 3)
        self.units_table.setHorizontalHeaderLabels([translator.t("col_name"), translator.t("col_abbrev"), translator.t("col_ticks")])
        self.units_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.units_table.setAlternatingRowColors(True)
        unit_layout.addWidget(self.units_table)

        btn_layout = QHBoxLayout()
        btn_add_unit = QPushButton(translator.t("btn_add_unit"))
        btn_add_unit.clicked.connect(self.add_time_unit)
        btn_del_unit = QPushButton(translator.t("btn_del_unit"))
        btn_del_unit.clicked.connect(self.remove_time_unit)

        btn_layout.addWidget(btn_add_unit)
        btn_layout.addWidget(btn_del_unit)
        unit_layout.addLayout(btn_layout)
        layout.addWidget(group_units)

        self.world_name_input.setToolTip(translator.t("tt_world_name"))
        self.base_tick_input.setToolTip(translator.t("tt_base_tick"))
        self.units_table.setToolTip(translator.t("tt_time_units"))

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

    def _cell_text(self, table: QTableWidget, row: int, col: int, default: str = "") -> str:
        item = table.item(row, col)
        return item.text().strip() if item and item.text() is not None else default

    def update_time_units(self):
        for r in range(self.units_table.rowCount()):
            if r >= len(self.main_window.world.time_units):
                break
            u = self.main_window.world.time_units[r]
            u.name = self._cell_text(self.units_table, r, 0)
            u.abbreviation = self._cell_text(self.units_table, r, 1)
            try:
                u.ticks = int(self._cell_text(self.units_table, r, 2, "1"))
            except ValueError:
                QMessageBox.warning(self, 'Invalid Input', 'Please enter a valid number.')
                self.refresh_view()

    def update_earth_sync_state(self):
        is_enabled = self.chk_earth_sync.isChecked()
        self.earth_epoch_input.setEnabled(is_enabled)
        self.real_seconds_input.setEnabled(is_enabled)

    # --- Planets ---
    def setup_planets_tab(self):
        layout = QVBoxLayout(self.tab_planets)
        layout.setContentsMargins(20, 20, 20, 20)

        group = QGroupBox(translator.t("tab_planets"))
        group_layout = QVBoxLayout(group)

        self.planets_table = QTableWidget(0, 4)
        self.planets_table.setHorizontalHeaderLabels([translator.t("col_name"), translator.t("col_day_length"), translator.t("col_year_length"), translator.t("col_is_primary")])
        self.planets_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.planets_table.setAlternatingRowColors(True)
        self.planets_table.setToolTip(translator.t("tt_day_length") + " | " + translator.t("tt_year_length") + " | " + translator.t("tt_is_primary"))
        group_layout.addWidget(self.planets_table)

        btn_layout = QHBoxLayout()
        btn_add = QPushButton(translator.t("btn_add_planet"))
        btn_add.clicked.connect(self.add_planet)
        btn_del = QPushButton(translator.t("btn_del_planet"))
        btn_del.clicked.connect(self.remove_planet)

        btn_layout.addWidget(btn_add)
        btn_layout.addWidget(btn_del)
        group_layout.addLayout(btn_layout)

        layout.addWidget(group)

        # Quick Day Length Calculator Group
        calc_group = QGroupBox(translator.t("day_calc_title"))
        calc_layout = QHBoxLayout(calc_group)

        self.spin_hours_per_day = QSpinBox()
        self.spin_hours_per_day.setRange(1, 1000)
        self.spin_hours_per_day.setValue(24)

        self.spin_mins_per_hour = QSpinBox()
        self.spin_mins_per_hour.setRange(1, 1000)
        self.spin_mins_per_hour.setValue(60)

        self.spin_secs_per_min = QSpinBox()
        self.spin_secs_per_min.setRange(1, 1000)
        self.spin_secs_per_min.setValue(60)

        btn_apply_calc = QPushButton(translator.t("btn_apply_calc"))
        btn_apply_calc.clicked.connect(self.apply_quick_day_length)

        calc_layout.addWidget(QLabel(translator.t("lbl_hours_day")))
        calc_layout.addWidget(self.spin_hours_per_day)
        calc_layout.addWidget(QLabel(translator.t("lbl_mins_hour")))
        calc_layout.addWidget(self.spin_mins_per_hour)
        calc_layout.addWidget(QLabel(translator.t("lbl_secs_min")))
        calc_layout.addWidget(self.spin_secs_per_min)
        calc_layout.addWidget(btn_apply_calc)

        layout.addWidget(calc_group)

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

    def apply_quick_day_length(self):
        engine = TimeEngine(self.main_window.world)
        p = engine.get_primary_planet()
        if p:
            tot = self.spin_hours_per_day.value() * self.spin_mins_per_hour.value() * self.spin_secs_per_min.value()
            p.day_length_ticks = tot
            self.populate_planets()
            self.main_window.mark_unsaved()
            QMessageBox.information(self, "Success", f"Set primary planet '{p.name}' day length to {tot} ticks ({self.spin_hours_per_day.value()} hours).")

    def remove_planet(self):
        row = self.planets_table.currentRow()
        if row >= 0:
            self.main_window.world.planets.pop(row)
            self.populate_planets()

    def update_planets(self, item):
        r = item.row()
        if r >= len(self.main_window.world.planets):
            return
        p = self.main_window.world.planets[r]
        p.name = self._cell_text(self.planets_table, r, 0)
        try:
            dl = int(self._cell_text(self.planets_table, r, 1, "86400"))
            if dl <= 0: dl = 1
            p.day_length_ticks = dl
            p.year_length_days = int(self._cell_text(self.planets_table, r, 2, "365"))
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
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        # Eras
        group_era = QGroupBox(translator.t("lbl_eras"))
        era_layout = QVBoxLayout(group_era)
        self.era_table = QTableWidget(0, 4)
        self.era_table.setHorizontalHeaderLabels([translator.t("col_name"), translator.t("col_abbrev"), translator.t("col_start_year"), translator.t("col_inc_yr_0")])
        self.era_table.setAlternatingRowColors(True)
        self.era_table.setToolTip(translator.t("tt_eras"))
        era_layout.addWidget(self.era_table)

        btn_era_layout = QHBoxLayout()
        btn_add_era = QPushButton(translator.t("btn_add_era"))
        btn_add_era.clicked.connect(lambda: (self.main_window.world.eras.append(Era(name="New Era")), self.populate_eras()))
        btn_del_era = QPushButton(translator.t("btn_del_era"))
        btn_del_era.clicked.connect(self.remove_era)
        btn_era_layout.addWidget(btn_add_era)
        btn_era_layout.addWidget(btn_del_era)
        era_layout.addLayout(btn_era_layout)
        self.era_table.itemChanged.connect(self.update_eras)

        # Months
        group_month = QGroupBox(translator.t("lbl_months"))
        month_layout = QVBoxLayout(group_month)
        self.month_table = QTableWidget(0, 3)
        self.month_table.setHorizontalHeaderLabels([translator.t("col_name"), translator.t("col_days"), translator.t("col_color")])
        self.month_table.setAlternatingRowColors(True)
        self.month_table.setToolTip(translator.t("tt_months"))
        month_layout.addWidget(self.month_table)

        btn_m_layout = QHBoxLayout()
        btn_add_month = QPushButton(translator.t("btn_add_month"))
        btn_add_month.clicked.connect(lambda: (self.main_window.world.months.append(Month(name="New Month")), self.populate_months()))
        btn_del_month = QPushButton(translator.t("btn_del_month"))
        btn_del_month.clicked.connect(self.remove_month)
        btn_m_layout.addWidget(btn_add_month)
        btn_m_layout.addWidget(btn_del_month)
        month_layout.addLayout(btn_m_layout)
        self.month_table.itemChanged.connect(self.update_months)

        # Weekdays
        group_wd = QGroupBox(translator.t("lbl_weekdays"))
        weekday_layout = QVBoxLayout(group_wd)
        self.weekday_table = QTableWidget(0, 1)
        self.weekday_table.setHorizontalHeaderLabels([translator.t("col_name")])
        self.weekday_table.setAlternatingRowColors(True)
        self.weekday_table.setToolTip(translator.t("tt_weekdays"))
        weekday_layout.addWidget(self.weekday_table)

        btn_wd_layout = QHBoxLayout()
        btn_add_wd = QPushButton(translator.t("btn_add_wd"))
        btn_add_wd.clicked.connect(lambda: (self.main_window.world.weekdays.append(Weekday(name="New Day")), self.populate_weekdays()))
        btn_del_wd = QPushButton(translator.t("btn_del_wd"))
        btn_del_wd.clicked.connect(self.remove_weekday)
        btn_wd_layout.addWidget(btn_add_wd)
        btn_wd_layout.addWidget(btn_del_wd)
        weekday_layout.addLayout(btn_wd_layout)
        self.weekday_table.itemChanged.connect(self.update_weekdays)

        layout.addWidget(group_era)
        layout.addWidget(group_month)
        layout.addWidget(group_wd)

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

    def remove_era(self):
        row = self.era_table.currentRow()
        if row >= 0 and row < len(self.main_window.world.eras):
            self.main_window.world.eras.pop(row)
            self.populate_eras()

    def remove_month(self):
        row = self.month_table.currentRow()
        if row >= 0 and row < len(self.main_window.world.months):
            self.main_window.world.months.pop(row)
            self.populate_months()

    def remove_weekday(self):
        row = self.weekday_table.currentRow()
        if row >= 0 and row < len(self.main_window.world.weekdays):
            self.main_window.world.weekdays.pop(row)
            self.populate_weekdays()

    def update_eras(self, item):
        r = item.row()
        if r >= len(self.main_window.world.eras):
            return
        e = self.main_window.world.eras[r]
        e.name = self._cell_text(self.era_table, r, 0)
        e.abbreviation = self._cell_text(self.era_table, r, 1)
        try:
            e.start_year = int(self._cell_text(self.era_table, r, 2, "0"))
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
        self.update_live_preview()

    def update_months(self):
        for r in range(self.month_table.rowCount()):
            if r >= len(self.main_window.world.months):
                break
            m = self.main_window.world.months[r]
            m.name = self._cell_text(self.month_table, r, 0)
            try:
                m.days = int(self._cell_text(self.month_table, r, 1, "30"))
            except ValueError:
                QMessageBox.warning(self, 'Invalid Input', 'Please enter a valid number.')
                self.refresh_view()
            m.color = self._cell_text(self.month_table, r, 2, "#FFFFFF")

    def populate_weekdays(self):
        self.weekday_table.blockSignals(True)
        self.weekday_table.setRowCount(len(self.main_window.world.weekdays))
        for r, w in enumerate(self.main_window.world.weekdays):
            self.weekday_table.setItem(r, 0, QTableWidgetItem(w.name))
        self.weekday_table.blockSignals(False)
        self.update_live_preview()

    def update_weekdays(self):
        for r in range(self.weekday_table.rowCount()):
            if r >= len(self.main_window.world.weekdays):
                break
            w = self.main_window.world.weekdays[r]
            w.name = self._cell_text(self.weekday_table, r, 0)

    # --- Holidays & Leap Rules ---
    def setup_holidays_tab(self):
        layout = QVBoxLayout(self.tab_holidays)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        # Holidays
        group_hol = QGroupBox(translator.t("lbl_holidays"))
        hol_layout = QVBoxLayout(group_hol)
        self.holiday_table = QTableWidget(0, 4)
        self.holiday_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.holiday_table.setAlternatingRowColors(True)
        self.holiday_table.setHorizontalHeaderLabels([translator.t("col_name"), translator.t("col_month_opt"), translator.t("col_day_in_month"), translator.t("col_counts_wd")])
        self.holiday_table.setToolTip(translator.t("tt_holidays"))
        hol_layout.addWidget(self.holiday_table)

        btn_hol_layout = QHBoxLayout()
        btn_add_hol = QPushButton(translator.t("btn_add_hol"))
        btn_add_hol.clicked.connect(lambda: (self.main_window.world.holidays.append(Holiday(name="New Holiday")), self.populate_holidays()))
        btn_del_hol = QPushButton(translator.t("btn_del_hol"))
        btn_del_hol.clicked.connect(self.remove_holiday)
        btn_hol_layout.addWidget(btn_add_hol)
        btn_hol_layout.addWidget(btn_del_hol)
        hol_layout.addLayout(btn_hol_layout)
        self.holiday_table.itemChanged.connect(self.update_holidays)
        layout.addWidget(group_hol)

        # Leap Rules
        group_leap = QGroupBox(translator.t("lbl_leap"))
        leap_layout = QVBoxLayout(group_leap)
        self.leap_table = QTableWidget(0, 5)
        self.leap_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.leap_table.setAlternatingRowColors(True)
        self.leap_table.setHorizontalHeaderLabels([translator.t("col_interval"), translator.t("col_month_append"), translator.t("col_days_add"), translator.t("col_exc_int"), translator.t("col_exc_days")])
        self.leap_table.setToolTip(translator.t("tt_leap"))
        leap_layout.addWidget(self.leap_table)

        btn_leap_layout = QHBoxLayout()
        btn_add_leap = QPushButton(translator.t("btn_add_leap"))
        btn_add_leap.clicked.connect(lambda: (self.main_window.world.leap_rules.append(LeapRule()), self.populate_leap_rules()))
        btn_del_leap = QPushButton(translator.t("btn_del_leap"))
        btn_del_leap.clicked.connect(self.remove_leap_rule)
        btn_leap_layout.addWidget(btn_add_leap)
        btn_leap_layout.addWidget(btn_del_leap)
        leap_layout.addLayout(btn_leap_layout)
        self.leap_table.itemChanged.connect(self.update_leap_rules)
        layout.addWidget(group_leap)

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

    def remove_holiday(self):
        row = self.holiday_table.currentRow()
        if row >= 0 and row < len(self.main_window.world.holidays):
            self.main_window.world.holidays.pop(row)
            self.populate_holidays()

    def remove_leap_rule(self):
        row = self.leap_table.currentRow()
        if row >= 0 and row < len(self.main_window.world.leap_rules):
            self.main_window.world.leap_rules.pop(row)
            self.populate_leap_rules()

    def update_holidays(self, item):
        r = item.row()
        if r >= len(self.main_window.world.holidays):
            return
        h = self.main_window.world.holidays[r]
        h.name = self._cell_text(self.holiday_table, r, 0)

        m_name = self._cell_text(self.holiday_table, r, 1)
        if not m_name:
            h.month_id = None
        else:
            found = False
            for m in self.main_window.world.months:
                if m.name == m_name:
                    h.month_id = m.id
                    found = True
                    break
            if not found:
                h.month_id = m_name

        try:
            h.day_in_month = int(self._cell_text(self.holiday_table, r, 2, "1"))
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
            self.leap_table.setItem(r, 3, QTableWidgetItem(str(l.exclude_interval)))
            self.leap_table.setItem(r, 4, QTableWidgetItem(str(l.force_include_interval)))
        self.leap_table.blockSignals(False)

    def update_leap_rules(self):
        for r in range(self.leap_table.rowCount()):
            if r >= len(self.main_window.world.leap_rules):
                break
            l = self.main_window.world.leap_rules[r]
            try:
                l.interval_years = int(self._cell_text(self.leap_table, r, 0, "0"))
                l.month_id_to_append = self._cell_text(self.leap_table, r, 1)
                l.days_to_add = int(self._cell_text(self.leap_table, r, 2, "0"))
                l.exclude_interval = int(self._cell_text(self.leap_table, r, 3, "0"))
                l.force_include_interval = int(self._cell_text(self.leap_table, r, 4, "0"))
            except ValueError:
                QMessageBox.warning(self, 'Invalid Input', 'Please enter a valid number.')
                self.refresh_view()

    # --- Astronomy ---
    def setup_astronomy_tab(self):
        layout = QHBoxLayout(self.tab_astronomy)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        # Suns
        group_sun = QGroupBox(translator.t("lbl_suns"))
        sun_layout = QVBoxLayout(group_sun)
        self.sun_table = QTableWidget(0, 3)
        self.sun_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.sun_table.setAlternatingRowColors(True)
        self.sun_table.setHorizontalHeaderLabels([translator.t("col_name"), translator.t("col_dawn"), translator.t("col_dusk")])
        self.sun_table.setToolTip(translator.t("tt_suns"))
        sun_layout.addWidget(self.sun_table)

        btn_sun_layout = QHBoxLayout()
        btn_add_sun = QPushButton(translator.t("btn_add_sun"))
        btn_add_sun.clicked.connect(lambda: (self.main_window.world.suns.append(Sun(name="New Sun")), self.populate_suns()))
        btn_del_sun = QPushButton(translator.t("btn_del_sun"))
        btn_del_sun.clicked.connect(self.remove_sun)
        btn_sun_layout.addWidget(btn_add_sun)
        btn_sun_layout.addWidget(btn_del_sun)
        sun_layout.addLayout(btn_sun_layout)
        self.sun_table.itemChanged.connect(self.update_suns)
        layout.addWidget(group_sun)

        # Moons
        group_moon = QGroupBox(translator.t("lbl_moons"))
        moon_layout = QVBoxLayout(group_moon)
        self.moon_table = QTableWidget(0, 3)
        self.moon_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.moon_table.setAlternatingRowColors(True)
        self.moon_table.setHorizontalHeaderLabels([translator.t("col_name"), translator.t("col_cycle"), translator.t("col_phase_off")])
        self.moon_table.setToolTip(translator.t("tt_moons"))
        moon_layout.addWidget(self.moon_table)

        btn_moon_layout = QHBoxLayout()
        btn_add_moon = QPushButton(translator.t("btn_add_moon"))
        btn_add_moon.clicked.connect(lambda: (self.main_window.world.moons.append(Moon(name="New Moon")), self.populate_moons()))
        btn_del_moon = QPushButton(translator.t("btn_del_moon"))
        btn_del_moon.clicked.connect(self.remove_moon)
        btn_moon_layout.addWidget(btn_add_moon)
        btn_moon_layout.addWidget(btn_del_moon)
        moon_layout.addLayout(btn_moon_layout)
        self.moon_table.itemChanged.connect(self.update_moons)
        layout.addWidget(group_moon)

    def populate_suns(self):
        self.sun_table.blockSignals(True)
        self.sun_table.setRowCount(len(self.main_window.world.suns))
        for r, s in enumerate(self.main_window.world.suns):
            self.sun_table.setItem(r, 0, QTableWidgetItem(s.name))
            self.sun_table.setItem(r, 1, QTableWidgetItem(str(s.twilight_dawn_ticks)))
            self.sun_table.setItem(r, 2, QTableWidgetItem(str(s.twilight_dusk_ticks)))
        self.sun_table.blockSignals(False)

    def remove_sun(self):
        row = self.sun_table.currentRow()
        if row >= 0 and row < len(self.main_window.world.suns):
            self.main_window.world.suns.pop(row)
            self.populate_suns()

    def remove_moon(self):
        row = self.moon_table.currentRow()
        if row >= 0 and row < len(self.main_window.world.moons):
            self.main_window.world.moons.pop(row)
            self.populate_moons()

    def update_suns(self):
        for r in range(self.sun_table.rowCount()):
            if r >= len(self.main_window.world.suns):
                break
            s = self.main_window.world.suns[r]
            s.name = self._cell_text(self.sun_table, r, 0)
            try:
                s.twilight_dawn_ticks = int(self._cell_text(self.sun_table, r, 1, "0"))
                s.twilight_dusk_ticks = int(self._cell_text(self.sun_table, r, 2, "0"))
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
            if r >= len(self.main_window.world.moons):
                break
            m = self.main_window.world.moons[r]
            m.name = self._cell_text(self.moon_table, r, 0)
            try:
                m.cycle_days = float(self._cell_text(self.moon_table, r, 1, "28.0"))
                m.phase_offset = float(self._cell_text(self.moon_table, r, 2, "0.0"))
            except ValueError:
                QMessageBox.warning(self, 'Invalid Input', 'Please enter a valid number.')
                self.refresh_view()
