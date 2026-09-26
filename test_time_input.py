from PyQt6.QtWidgets import QApplication
from cce.core.models import TimeUnit
from cce.gui.viewer import TimeInputWidget
import sys

app = QApplication(sys.argv)
units = [TimeUnit(name="Hour", ticks=100), TimeUnit(name="Minute", ticks=10)]
w = TimeInputWidget(units)

w.set_ticks(250)
print("Ticks after set(250):", w.get_ticks())

w.inputs[units[0].id].setValue(5) # 5 hours
w.inputs[units[1].id].setValue(2) # 2 mins
print("Ticks after spin box change:", w.get_ticks())
