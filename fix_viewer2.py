with open("cce/gui/viewer.py", "r") as f:
    c = f.read()

c = c.replace("""                ev.start_tick = new_day_tick + old_tod
                ev.end_tick = ev.start_tick + duration
                self.current_event.is_recurring = self.chk_recurring.isChecked()
        self.current_event.recurrence_interval_days = self.spin_recur_interval.value()
        self.main_window.mark_unsaved()
                self.refresh_view()
                break""", """                ev.start_tick = new_day_tick + old_tod
                ev.end_tick = ev.start_tick + duration
                ev.is_recurring = self.chk_recurring.isChecked()
                ev.recurrence_interval_days = self.spin_recur_interval.value()
                self.main_window.mark_unsaved()
                self.refresh_view()
                break""")

with open("cce/gui/viewer.py", "w") as f:
    f.write(c)
