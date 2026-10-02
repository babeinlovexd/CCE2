import sys
from PyQt6.QtWidgets import QApplication
from cce.gui.app import MainWindow

def test_language_switch_preserves_world_name():
    app = QApplication.instance() or QApplication(sys.argv)

    window = MainWindow()
    window.editor_widget.world_name_input.setText("Middle-Earth Realm")
    window.editor_widget.base_tick_input.setText("SecondOfTime")

    # Switch language to German
    window.switch_language("de")

    # Verify input text was preserved in model and populated in new EditorWidget
    assert window.world.name == "Middle-Earth Realm"
    assert window.world.base_tick_name == "SecondOfTime"
    assert window.editor_widget.world_name_input.text() == "Middle-Earth Realm"
    assert window.editor_widget.base_tick_input.text() == "SecondOfTime"
