# Modern Dark Theme Qt Style Sheet (QSS)

MODERN_DARK_STYLE = """
/* Base Colors:
   Background: #100020
   Surface (Panels/Inputs): #313244
   Primary Accent (Blue): #00c0f0
   Text: #cdd6f4
   Border: #45475a
*/

QWidget {
    background-color: #100020;
    color: #cdd6f4;
    font-family: "Segoe UI", "Helvetica Neue", Arial, sans-serif;
    font-size: 14px;
}

/* Tooltips */
QToolTip {
    background-color: #313244;
    color: #cdd6f4;
    border: 1px solid #00c0f0;
    border-radius: 8px;
    padding: 6px;
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
    background-color: #00c0f0;
    color: #100020;
}

/* Tabs */
QTabWidget::pane {
    border: 1px solid #45475a;
    border-radius: 8px;
    background-color: #100020;
    margin-top: -1px;
}
QTabBar::tab {
    background-color: #313244;
    color: #a6adc8;
    border: 1px solid #45475a;
    border-bottom-color: #45475a;
    border-top-left-radius: 8px;
    border-top-right-radius: 8px;
    padding: 10px 18px;
    margin-right: 4px;
}
QTabBar::tab:selected {
    background-color: #100020;
    color: #00c0f0;
    border-bottom-color: #100020;
    font-weight: bold;
}
QTabBar::tab:hover:!selected {
    background-color: #45475a;
}

/* Buttons */
QPushButton {
    background-color: #313244;
    border: 1px solid #45475a;
    border-radius: 8px;
    padding: 8px 16px;
    color: #cdd6f4;
    font-weight: bold;
}
QPushButton:hover {
    background-color: #45475a;
    border-color: #00c0f0;
}
QPushButton:pressed {
    background-color: #00c0f0;
    color: #100020;
}
/* Primary Action Button (e.g. Generate) */
QPushButton#primaryAction {
    background-color: #00c0f0;
    color: #100020;
    border: none;
}
QPushButton#primaryAction:hover {
    background-color: #2080f0;
}
QPushButton#primaryAction:pressed {
    background-color: #3060f0;
}

/* Calendar Grid Buttons */
QPushButton.calendar-day {
    background-color: #313244;
    border: 1px solid #45475a;
    border-radius: 8px;
    font-size: 15px;
}
QPushButton.calendar-day:hover {
    border: 2px solid #00c0f0;
}
QPushButton.calendar-day-event {
    background-color: #313244;
    border: 2px solid #f38ba8;
    color: #f38ba8;
    font-weight: bold;
}
QPushButton.calendar-day-search {
    background-color: #f9e2af;
    color: #100020;
    border: 2px solid #fab387;
    font-weight: bold;
}

/* Inputs */
QLineEdit, QTextEdit, QComboBox, QSpinBox {
    background-color: #181825;
    border: 1px solid #45475a;
    border-radius: 8px;
    padding: 8px;
    color: #cdd6f4;
}
QLineEdit:focus, QTextEdit:focus, QComboBox:focus, QSpinBox:focus {
    border: 1px solid #00c0f0;
    background-color: #11111b;
}

/* ComboBox Dropdown */
QComboBox::drop-down {
    border-left: 1px solid #45475a;
}
QComboBox QAbstractItemView {
    background-color: #313244;
    border: 1px solid #45475a;
    selection-background-color: #00c0f0;
    selection-color: #100020;
}

/* Group Boxes for better layout */
QGroupBox {
    border: 1px solid #45475a;
    border-radius: 12px;
    margin-top: 2ex;
    padding: 14px;
}
QGroupBox::title {
    subcontrol-origin: margin;
    subcontrol-position: top left;
    padding: 0 5px;
    color: #00c0f0;
    font-weight: bold;
}

/* Tables */
QTableWidget {
    background-color: #181825;
    alternate-background-color: #100020;
    border: 1px solid #45475a;
    border-radius: 8px;
    gridline-color: #45475a;
}
QTableWidget::item {
    padding: 4px;
}
QTableWidget::item:selected {
    background-color: #00c0f0;
    color: #100020;
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
    border-radius: 8px;
}
QListWidget::item {
    padding: 8px;
    border-bottom: 1px solid #313244;
}
QListWidget::item:selected {
    background-color: #00c0f0;
    color: #100020;
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
