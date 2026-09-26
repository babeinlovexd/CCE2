with open("cce/gui/viewer.py", "r") as f:
    c = f.read()

c = c.replace('self.ev_duration_days = QSpinBox()', 'from PyQt6.QtWidgets import QSpinBox\n        self.ev_duration_days = QSpinBox()')

with open("cce/gui/viewer.py", "w") as f:
    f.write(c)
