# Dictionary for translations and tooltips

LANGUAGES = {
    "en": {
        # App Level
        "menu_language": "Language",

        # Editor Top Bar
        "btn_save": "Save Project",
        "btn_open": "Open Project",
        "btn_generate": "🚀 Generate Calendar & Open Viewer",

        # Editor Tabs
        "tab_world": "World & Units",
        "tab_planets": "Planets & Orbit",
        "tab_calendar": "Eras, Months & Weekdays",
        "tab_holidays": "Holidays & Leap Rules",
        "tab_astronomy": "Suns & Moons",

        # World Tab
        "world_name": "World Name:",
        "base_tick_name": "Base Tick Name:",
        "time_units_lbl": "Time Units (e.g. Second, Minute, Hour, Watch)",
        "col_name": "Name",
        "col_abbrev": "Abbrev",
        "col_ticks": "Ticks",
        "btn_add_unit": "Add Unit",
        "btn_del_unit": "Remove Selected",
        "tt_world_name": "The name of your entire fantasy/sci-fi world.",
        "tt_base_tick": "The smallest, most fundamental unit of time (e.g., 'Second' or 'Pulse'). Everything is calculated in these ticks.",
        "tt_time_units": "Create your daily time hierarchy here. E.g., an 'Hour' could equal 3600 Ticks.",
        # Earth Sync
        "lbl_earth_sync": "Real-World Earth Synchronization",
        "chk_earth_sync": "Enable Earth Synchronization",
        "lbl_earth_epoch": "Earth Date at Tick 0 (YYYY-MM-DD):",
        "lbl_real_seconds": "Real Seconds per 1 Tick:",
        "tt_earth_sync": "Links your fantasy calendar to the real world (e.g. to celebrate character birthdays in real life).",
        "tt_earth_epoch": "The real world date that corresponds to the very beginning of your calendar (Tick 0).",
        "tt_real_seconds": "How many real-world seconds make up one of your base ticks. (e.g. 1.0 = normal time, 2.0 = half speed).",
        "lbl_earth_date": "Earth Date:",
        # New Features
        "btn_ev_delete": "Delete Event",
        "btn_export": "Export Timeline",
        "warn_unsaved_title": "Unsaved Changes",
        "warn_unsaved_msg": "You have unsaved changes. Are you sure you want to proceed without saving?",
        "export_success": "Timeline exported successfully!",



        # Planets Tab
        "col_day_length": "Day Length (Ticks)",
        "col_year_length": "Year Length (Days)",
        "col_is_primary": "Is Primary",
        "btn_add_planet": "Add Planet",
        "btn_del_planet": "Remove Selected",
        "tt_day_length": "How many base ticks make up one full day on this planet.",
        "tt_year_length": "How many full days make up one orbital year on this planet.",
        "tt_is_primary": "The main planet used as the reference point for the Calendar Viewer.",

        # Calendar Tab
        "lbl_eras": "Eras",
        "col_start_year": "Start Year",
        "col_inc_yr_0": "Inc Yr 0",
        "btn_add_era": "Add Era",
        "lbl_months": "Months / Seasons",
        "col_days": "Days",
        "col_color": "Color",
        "btn_add_month": "Add Month",
        "lbl_weekdays": "Weekdays",
        "btn_add_wd": "Add Weekday",
        "tt_eras": "Define historical epochs (e.g., 'Third Age'). Start Year determines when it begins.",
        "tt_months": "Define the months or seasons that make up a year.",
        "tt_weekdays": "List your days of the week. Order matters. If empty, weekdays are ignored.",

        # Holidays Tab
        "lbl_holidays": "Holidays",
        "col_month_opt": "Month (Leave blank for inter-month)",
        "col_day_in_month": "Day in Month",
        "col_counts_wd": "Counts as Weekday",
        "btn_add_hol": "Add Holiday",
        "lbl_leap": "Leap Rules",
        "col_interval": "Interval (Years)",
        "col_month_append": "Month ID to Append",
        "col_days_add": "Days to Add",
        "col_exc_int": "Exception Interval",
        "col_exc_days": "Exception Days",
        "btn_add_leap": "Add Leap Rule",
        "tt_holidays": "Special days. If Month is blank, it acts as an intercalary day (outside normal months).",
        "tt_leap": "Rules for leap years. E.g., add 1 day every 4 years, but ignore every 100 years.",

        # Astronomy Tab
        "lbl_suns": "Suns",
        "col_dawn": "Dawn Ticks",
        "col_dusk": "Dusk Ticks",
        "btn_add_sun": "Add Sun",
        "lbl_moons": "Moons",
        "col_cycle": "Cycle (Days)",
        "col_phase_off": "Phase Offset",
        "btn_add_moon": "Add Moon",
        "tt_suns": "Define the stars of this world. Dawn/Dusk ticks define sunrise/sunset times.",
        "tt_moons": "Define moons. Cycle is days from Full Moon to Full Moon. Offset shifts the start phase.",

        # Viewer Strings
        "btn_back": "🔙 Editor",
        "sync_lbl": "Sync:",
        "search_ph": "Search events, characters, locations...",
        "no_months": "No months defined.",
        "select_day": "Select a Day",
        "lbl_events": "Events:",
        "ev_title": "Title:",
        "ev_start": "Start Tick:",
        "ev_end": "End Tick:",
        "ev_chars": "Characters:",
        "ev_loc": "Location:",
        "ev_notes": "Notes:",
        "btn_ev_save": "Save Event",
        "btn_ev_new": "New Event",
        "tt_sync": "Select a different planet to see what time it is there exactly when this day happens on the primary planet.",
        "tt_ev_start": "The exact tick when this event begins.",
        "tt_ev_chars": "Comma-separated list of characters involved.",
    },

    "de": {
        # App Level
        "menu_language": "Sprache",

        # Editor Top Bar
        "btn_save": "Projekt Speichern",
        "btn_open": "Projekt Öffnen",
        "btn_generate": "🚀 Kalender generieren & ansehen",

        # Editor Tabs
        "tab_world": "Welt & Einheiten",
        "tab_planets": "Planeten & Orbit",
        "tab_calendar": "Epochen, Monate & Wochentage",
        "tab_holidays": "Feiertage & Schaltregeln",
        "tab_astronomy": "Sonnen & Monde",

        # World Tab
        "world_name": "Name der Welt:",
        "base_tick_name": "Basis-Tick Name:",
        "time_units_lbl": "Zeiteinheiten (z.B. Sekunde, Minute, Stunde, Wache)",
        "col_name": "Name",
        "col_abbrev": "Kürzel",
        "col_ticks": "Ticks",
        "btn_add_unit": "Einheit hinzufügen",
        "btn_del_unit": "Auswahl löschen",
        "tt_world_name": "Der Name deiner gesamten Fantasy/Sci-Fi Welt.",
        "tt_base_tick": "Die kleinste, grundlegendste Zeiteinheit (z.B. 'Sekunde' oder 'Puls'). Alles wird intern in Ticks berechnet.",
        "tt_time_units": "Erschaffe hier deine tägliche Zeithierarchie. Z.B. entspricht eine 'Stunde' 3600 Ticks.",
        # Earth Sync
        "lbl_earth_sync": "Real-Welt Erd-Synchronisation",
        "chk_earth_sync": "Erd-Synchronisation aktivieren",
        "lbl_earth_epoch": "Erd-Datum bei Tick 0 (JJJJ-MM-TT):",
        "lbl_real_seconds": "Echte Sekunden pro 1 Tick:",
        "tt_earth_sync": "Verknüpft deinen Fantasy-Kalender mit der echten Welt (z.B. um Geburtstage im echten Leben zu feiern).",
        "tt_earth_epoch": "Das reale Datum, das dem absoluten Beginn deines Kalenders (Tick 0) entspricht.",
        "tt_real_seconds": "Wie viele echte Sekunden einem deiner Basis-Ticks entsprechen. (z.B. 1.0 = normale Zeit, 0.5 = doppelt so schnell).",
        "lbl_earth_date": "Erd-Datum:",
        # New Features
        "btn_ev_delete": "Event löschen",
        "btn_export": "Timeline exportieren",
        "warn_unsaved_title": "Ungespeicherte Änderungen",
        "warn_unsaved_msg": "Du hast ungespeicherte Änderungen. Möchtest du wirklich fortfahren, ohne zu speichern?",
        "export_success": "Timeline erfolgreich exportiert!",



        # Planets Tab
        "col_day_length": "Tageslänge (Ticks)",
        "col_year_length": "Jahreslänge (Tage)",
        "col_is_primary": "Hauptplanet",
        "btn_add_planet": "Planet hinzufügen",
        "btn_del_planet": "Auswahl löschen",
        "tt_day_length": "Aus wie vielen Basis-Ticks ein ganzer Tag auf diesem Planeten besteht.",
        "tt_year_length": "Wie viele ganze Tage ein volles Umlauf-Jahr auf diesem Planeten ergeben.",
        "tt_is_primary": "Der primäre Planet, dessen Kalender im Viewer standardmäßig angezeigt wird.",

        # Calendar Tab
        "lbl_eras": "Epochen / Zeitalter",
        "col_start_year": "Startjahr",
        "col_inc_yr_0": "Inkl. Jahr 0",
        "btn_add_era": "Epoche hinzufügen",
        "lbl_months": "Monate / Jahreszeiten",
        "col_days": "Tage",
        "col_color": "Farbe",
        "btn_add_month": "Monat hinzufügen",
        "lbl_weekdays": "Wochentage",
        "btn_add_wd": "Wochentag hinzufügen",
        "tt_eras": "Definiere historische Zeitalter (z.B. 'Dritte Ära'). Das Startjahr bestimmt den Beginn.",
        "tt_months": "Definiere die Monate oder Jahreszeiten, die ein Jahr bilden.",
        "tt_weekdays": "Liste deine Wochentage auf. Die Reihenfolge ist wichtig. (Leer = keine Wochentage).",

        # Holidays Tab
        "lbl_holidays": "Feiertage",
        "col_month_opt": "Monat (Leer lassen für Zwischenmonatstage)",
        "col_day_in_month": "Tag im Monat",
        "col_counts_wd": "Zählt als Wochentag",
        "btn_add_hol": "Feiertag hinzufügen",
        "lbl_leap": "Schaltjahr-Regeln",
        "col_interval": "Intervall (Jahre)",
        "col_month_append": "Monats-ID (Anhängen an)",
        "col_days_add": "Tage hinzufügen",
        "col_exc_int": "Ausnahme-Intervall",
        "col_exc_days": "Ausnahme-Tage",
        "btn_add_leap": "Regel hinzufügen",
        "tt_holidays": "Besondere Tage. Wenn der Monat leer bleibt, agiert er als Einschalttag außerhalb normaler Monate.",
        "tt_leap": "Regeln für Schaltjahre. Z.B.: Füge alle 4 Jahre 1 Tag hinzu, außer alle 100 Jahre.",

        # Astronomy Tab
        "lbl_suns": "Sonnen",
        "col_dawn": "Aufgang (Ticks)",
        "col_dusk": "Untergang (Ticks)",
        "btn_add_sun": "Sonne hinzufügen",
        "lbl_moons": "Monde",
        "col_cycle": "Zyklus (Tage)",
        "col_phase_off": "Phasen-Versatz",
        "btn_add_moon": "Mond hinzufügen",
        "tt_suns": "Definiere die Sterne dieser Welt. Auf-/Untergang (Ticks) definieren die Tageslichtzeiten.",
        "tt_moons": "Definiere Monde. Der Zyklus bemisst die Tage von Vollmond zu Vollmond. Versatz verschiebt die Startphase an Tag 0.",

        # Viewer Strings
        "btn_back": "🔙 Editor",
        "sync_lbl": "Sync:",
        "search_ph": "Suche Events, Charaktere, Orte...",
        "no_months": "Keine Monate definiert.",
        "select_day": "Wähle einen Tag",
        "lbl_events": "Ereignisse:",
        "ev_title": "Titel:",
        "ev_start": "Start-Tick:",
        "ev_end": "End-Tick:",
        "ev_chars": "Charaktere:",
        "ev_loc": "Ort:",
        "ev_notes": "Notizen:",
        "btn_ev_save": "Event speichern",
        "btn_ev_new": "Neues Event",
        "tt_sync": "Wähle einen anderen Planeten aus, um zu sehen, wie spät es dort exakt ist, wenn dieser Tag auf dem Hauptplaneten anbricht.",
        "tt_ev_start": "Der absolute Tick, an dem das Event beginnt.",
        "tt_ev_chars": "Kommagetrennte Liste der involvierten Charaktere.",
    }
}

class Translator:
    def __init__(self):
        self.lang = "en"

    def set_language(self, lang_code: str):
        if lang_code in LANGUAGES:
            self.lang = lang_code

    def t(self, key: str) -> str:
        return LANGUAGES.get(self.lang, LANGUAGES["en"]).get(key, f"[{key}]")

translator = Translator()
