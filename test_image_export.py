import sys
from PyQt6.QtWidgets import QApplication
from cce.gui.app import MainWindow

app = QApplication(sys.argv)
win = MainWindow()
win.viewer_widget.export_calendar_image
print("Export method exists and is reachable")
