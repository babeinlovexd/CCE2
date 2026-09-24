# Modern Dark Theme Qt Style Sheet (QSS)

MODERN_DARK_STYLE = """
/* Base Colors:
   Background: #1e1e2e
   Surface (Panels/Inputs): #313244
   Primary Accent (Blue): #89b4fa
   Text: #cdd6f4
   Border: #45475a
*/

QWidget {
    background-color: #1e1e2e;
    color: #cdd6f4;
    font-family: "Segoe UI", "Helvetica Neue", Arial, sans-serif;
    font-size: 13px;
}

/* Tooltips */
QToolTip {
    background-color: #313244;
    color: #cdd6f4;
    border: 1px solid #89b4fa;
    border-radius: 4px;
    padding: 4px;
}

/* Menus */
QMenuBar {
    background-color: #11111b;
    border-bottom: 1px solid #45475a;
}
QMenuBar::item:selected {
    background-color: #313244;
}
QMenu {
    background-color: #313244;
    border: 1px solid #45475a;
}
QMenu::item:selected {
    background-color: #89b4fa;
    color: #1e1e2e;
}

/* Tabs */
QTabWidget::pane {
    border: 1px solid #45475a;
    border-radius: 4px;
    background-color: #1e1e2e;
    margin-top: -1px;
}
QTabBar::tab {
    background-color: #313244;
    color: #a6adc8;
    border: 1px solid #45475a;
    border-bottom-color: #45475a;
    border-top-left-radius: 6px;
    border-top-right-radius: 6px;
    padding: 8px 16px;
    margin-right: 2px;
}
QTabBar::tab:selected {
    background-color: #1e1e2e;
    color: #89b4fa;
    border-bottom-color: #1e1e2e;
    font-weight: bold;
}
QTabBar::tab:hover:!selected {
    background-color: #45475a;
}

/* Buttons */
QPushButton {
    background-color: #313244;
    border: 1px solid #45475a;
    border-radius: 5px;
    padding: 6px 14px;
    color: #cdd6f4;
    font-weight: bold;
}
QPushButton:hover {
    background-color: #45475a;
    border-color: #89b4fa;
}
QPushButton:pressed {
    background-color: #89b4fa;
    color: #1e1e2e;
}
/* Primary Action Button (e.g. Generate) */
QPushButton#primaryAction {
    background-color: #89b4fa;
    color: #1e1e2e;
    border: none;
}
QPushButton#primaryAction:hover {
    background-color: #b4befe;
}
QPushButton#primaryAction:pressed {
    background-color: #74c7ec;
}

/* Calendar Grid Buttons */
QPushButton.calendar-day {
    background-color: #313244;
    border: 1px solid #45475a;
    border-radius: 6px;
    font-size: 14px;
}
QPushButton.calendar-day:hover {
    border: 2px solid #89b4fa;
}
QPushButton.calendar-day-event {
    background-color: #313244;
    border: 2px solid #f38ba8;
    color: #f38ba8;
    font-weight: bold;
}
QPushButton.calendar-day-search {
    background-color: #f9e2af;
    color: #1e1e2e;
    border: 2px solid #fab387;
    font-weight: bold;
}

/* Inputs */
QLineEdit, QTextEdit, QComboBox {
    background-color: #181825;
    border: 1px solid #45475a;
    border-radius: 4px;
    padding: 6px;
    color: #cdd6f4;
}
QLineEdit:focus, QTextEdit:focus, QComboBox:focus {
    border: 1px solid #89b4fa;
    background-color: #11111b;
}

/* ComboBox Dropdown */
QComboBox::drop-down {
    border-left: 1px solid #45475a;
}
QComboBox QAbstractItemView {
    background-color: #313244;
    border: 1px solid #45475a;
    selection-background-color: #89b4fa;
    selection-color: #1e1e2e;
}

/* Group Boxes for better layout */
QGroupBox {
    border: 1px solid #45475a;
    border-radius: 6px;
    margin-top: 1.5ex;
    padding: 10px;
}
QGroupBox::title {
    subcontrol-origin: margin;
    subcontrol-position: top left;
    padding: 0 5px;
    color: #89b4fa;
    font-weight: bold;
}

/* Tables */
QTableWidget {
    background-color: #181825;
    alternate-background-color: #1e1e2e;
    border: 1px solid #45475a;
    border-radius: 4px;
    gridline-color: #45475a;
}
QTableWidget::item {
    padding: 4px;
}
QTableWidget::item:selected {
    background-color: #89b4fa;
    color: #1e1e2e;
}
QHeaderView::section {
    background-color: #313244;
    color: #cdd6f4;
    padding: 6px;
    border: none;
    border-right: 1px solid #45475a;
    border-bottom: 1px solid #45475a;
    font-weight: bold;
}

/* Lists (e.g. Search results, Events) */
QListWidget {
    background-color: #181825;
    border: 1px solid #45475a;
    border-radius: 4px;
}
QListWidget::item {
    padding: 8px;
    border-bottom: 1px solid #313244;
}
QListWidget::item:selected {
    background-color: #89b4fa;
    color: #1e1e2e;
    border-radius: 3px;
}
QListWidget::item:hover:!selected {
    background-color: #313244;
}

/* Scrollbars */
QScrollBar:vertical {
    border: none;
    background-color: #181825;
    width: 12px;
    margin: 0px;
}
QScrollBar::handle:vertical {
    background-color: #45475a;
    min-height: 20px;
    border-radius: 6px;
}
QScrollBar::handle:vertical:hover {
    background-color: #585b70;
}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    height: 0px;
}
"""
