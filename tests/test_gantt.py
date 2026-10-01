from cce.core.models import World, Event, Planet
from cce.gui.viewer import ViewerWidget
from cce.gui.app import MainWindow
from PyQt6.QtWidgets import QApplication
import sys

def test_gantt_occurrence_check():
    # Ensure QApplication exists for GUI widget tests
    app = QApplication.instance() or QApplication(sys.argv)

    world = World()
    planet = Planet(day_length_ticks=100, is_primary=True)
    world.planets = [planet]

    ev1 = Event(title="Battle of Red Valley", start_tick=100, end_tick=300, category="Battle") # Days 1..3
    world.events = [ev1]

    win = MainWindow()
    win.world = world
    viewer = ViewerWidget(win)

    # Check Day 1 (tick 100) -> True
    assert viewer._event_occurs_on_day(ev1, 100, 100) is True
    # Check Day 2 (tick 200) -> True
    assert viewer._event_occurs_on_day(ev1, 200, 100) is True
    # Check Day 5 (tick 500) -> False
    assert viewer._event_occurs_on_day(ev1, 500, 100) is False
