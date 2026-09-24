#!/bin/bash
# To build the standalone executable on Linux
pyinstaller --noconsole --onefile --windowed --name="Chronix" --icon="assets/icon.ico" --add-data="assets:assets" main.py
