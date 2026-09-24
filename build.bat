@echo off
echo ==========================================
echo Chronix - Windows Build Script
echo ==========================================
echo.
echo Installing requirements...
py -m pip install -r requirements.txt
py -m pip install pyinstaller

echo.
echo Building the Standalone Executable...
py -m PyInstaller --noconsole --onefile --windowed --name="Chronix" --icon="assets\icon.ico" --add-data="assets;assets" main.py

echo.
echo Build Complete! Check the 'dist' folder for Chronix.exe
pause
