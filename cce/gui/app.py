import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QStackedWidget, QWidget, QVBoxLayout, QPushButton, QHBoxLayout
from PyQt6.QtCore import Qt

from cce.core.models import World
from .editor import EditorWidget
from .viewer import ViewerWidget

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Custom Calendar Engine")
        self.resize(1200, 800)

        self.world = World()

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout(self.central_widget)

        self.stack = QStackedWidget()

        self.editor_widget = EditorWidget(self)
        self.viewer_widget = ViewerWidget(self)

        self.stack.addWidget(self.editor_widget)
        self.stack.addWidget(self.viewer_widget)

        self.layout.addWidget(self.stack)

    def switch_to_viewer(self):
        self.viewer_widget.refresh_view()
        self.stack.setCurrentWidget(self.viewer_widget)

    def switch_to_editor(self):
        self.editor_widget.refresh_view()
        self.stack.setCurrentWidget(self.editor_widget)

def run_app():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
