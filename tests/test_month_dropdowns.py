import sys
from PyQt6.QtWidgets import QApplication
from cce.core.models import World, Month, Holiday, LeapRule
from cce.gui.app import MainWindow
from cce.gui.editor import EditorWidget

def test_month_dropdown_resolution():
    app = QApplication.instance() or QApplication(sys.argv)

    world = World(name="Test World")
    m1 = Month(id="m1_id", name="Frostreach", days=30)
    m2 = Month(id="m2_id", name="Sunpeak", days=30)
    world.months = [m1, m2]

    h1 = Holiday(name="Festival of Sun", month_id=None)
    l1 = LeapRule(interval_years=4, month_id_to_append="", days_to_add=1)
    world.holidays = [h1]
    world.leap_rules = [l1]

    win = MainWindow()
    win.world = world
    editor = EditorWidget(win)
    editor.refresh_view()

    # Change holiday month dropdown to index 2 ("Sunpeak" -> m2_id)
    editor._on_holiday_month_changed(0, 2)
    assert world.holidays[0].month_id == "m2_id"

    # Change leap rule month dropdown to index 1 ("Frostreach" -> m1_id)
    editor._on_leap_month_changed(0, 1)
    assert world.leap_rules[0].month_id_to_append == "m1_id"
