#!/bin/bash
# To build the standalone executable on Linux/Windows
pyinstaller --noconsole --onefile --windowed --name="CustomCalendarEngine" main.py
