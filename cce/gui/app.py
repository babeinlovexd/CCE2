import os
import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QStackedWidget, QWidget, QVBoxLayout, QPushButton, QHBoxLayout, QMenuBar, QLabel, QMessageBox, QScrollArea, QFrame
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QIcon, QPixmap

from cce.core.models import World
from .translations import translator
from .styles import MODERN_DARK_STYLE

from .editor import EditorWidget
from .viewer import ViewerWidget

def get_resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Chronix")
        self.resize(1000, 680)
        self.setMinimumSize(600, 450)

        icon_path = get_resource_path(os.path.join("assets", "chronix_logo.png"))
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))

        self.world = World()
        self.is_unsaved = False

        self.create_menu_bar()

        self.central_widget = QWidget()

        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout(self.central_widget)

                        # --- LOGO BANNER ---
        self.logo_label = QLabel()
        self.logo_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.logo_path = get_resource_path(os.path.join("assets", "chronix_breit.png"))
        self.icon_path = icon_path

        self.update_logo_size() # Initial sizing

        self.layout.addWidget(self.logo_label)
        # -------------------

        self.stack = QStackedWidget()

        self.editor_widget = EditorWidget(self)
        self.viewer_widget = ViewerWidget(self)

        self.stack.addWidget(self.editor_widget)
        self.stack.addWidget(self.viewer_widget)

        main_scroll = QScrollArea()
        main_scroll.setWidgetResizable(True)
        main_scroll.setFrameShape(QFrame.Shape.NoFrame)
        main_scroll.setWidget(self.stack)

        self.layout.addWidget(main_scroll)


    def create_menu_bar(self):
        self.menu_bar = self.menuBar()
        self.lang_menu = self.menu_bar.addMenu(translator.t("menu_language"))

        action_en = self.lang_menu.addAction("English")
        action_de = self.lang_menu.addAction("Deutsch")

        action_en.triggered.connect(lambda: self.switch_language("en"))
        action_de.triggered.connect(lambda: self.switch_language("de"))


    def mark_unsaved(self):
        self.is_unsaved = True
        self.setWindowTitle("Chronix *")

    def mark_saved(self):
        self.is_unsaved = False
        self.setWindowTitle("Chronix")

    def check_unsaved_changes(self) -> bool:
        if not self.is_unsaved:
            return True

        reply = QMessageBox.question(self, translator.t("warn_unsaved_title"),
                                     translator.t("warn_unsaved_msg"),
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                                     QMessageBox.StandardButton.No)

        return reply == QMessageBox.StandardButton.Yes

    def update_logo_size(self):
        # Calculate maximum height based on window height, or set a dynamic range
        # E.g. at least 80, at most 200, typically 15% of window height
        target_height = max(80, min(200, int(self.height() * 0.15)))

        if os.path.exists(self.logo_path):
            pixmap = QPixmap(self.logo_path)
            scaled_pixmap = pixmap.scaledToHeight(target_height, Qt.TransformationMode.SmoothTransformation)
            self.logo_label.setPixmap(scaled_pixmap)
        elif os.path.exists(self.icon_path):
            pixmap = QPixmap(self.icon_path)
            scaled_pixmap = pixmap.scaledToHeight(target_height, Qt.TransformationMode.SmoothTransformation)
            self.logo_label.setPixmap(scaled_pixmap)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.update_logo_size()

    def closeEvent(self, event):
        if self.check_unsaved_changes():
            event.accept()
        else:
            event.ignore()

    def switch_language(self, lang_code):
        if hasattr(self, 'editor_widget') and self.editor_widget:
            self.editor_widget.flush_state_to_model()

        translator.set_language(lang_code)
        self.lang_menu.setTitle(translator.t("menu_language"))

        # We need to completely rebuild the widgets to apply translations cleanly
        # given the current architecture
        current_idx = self.stack.currentIndex()

        # Remove old widgets
        self.stack.removeWidget(self.editor_widget)
        self.stack.removeWidget(self.viewer_widget)

        # Recreate them
        self.editor_widget = EditorWidget(self)
        self.viewer_widget = ViewerWidget(self)

        self.stack.addWidget(self.editor_widget)
        self.stack.addWidget(self.viewer_widget)

        # Restore state
        self.stack.setCurrentIndex(current_idx)
        if current_idx == 0:
            self.editor_widget.refresh_view()
        else:
            self.viewer_widget.refresh_view()

    def switch_to_viewer(self):

        self.viewer_widget.refresh_view()
        self.stack.setCurrentWidget(self.viewer_widget)

    def switch_to_editor(self):
        self.editor_widget.refresh_view()
        self.stack.setCurrentWidget(self.editor_widget)

def run_app():
    app = QApplication(sys.argv)
    icon_path = get_resource_path(os.path.join("assets", "chronix_logo.png"))
    if os.path.exists(icon_path):
        app.setWindowIcon(QIcon(icon_path))
    app.setStyleSheet(MODERN_DARK_STYLE)
    window = MainWindow()

    # Check if a file was passed as an argument (e.g., from double-clicking a .worldcal file)
    if len(sys.argv) > 1:
        file_path = sys.argv[1]
        if os.path.exists(file_path) and file_path.endswith('.worldcal'):
            from cce.core.storage import load_world
            from PyQt6.QtWidgets import QMessageBox
            try:
                window.world = load_world(file_path)
                window.editor_widget.refresh_view()
                window.mark_saved()
            except Exception as e:
                QMessageBox.critical(window, "Error", f"Could not load file:\n{e}")

    window.show()
    sys.exit(app.exec())
