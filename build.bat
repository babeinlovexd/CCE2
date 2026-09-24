@echo off
echo ==========================================
echo Custom Calendar Engine - Windows Build Script
echo ==========================================
echo.
echo Installing requirements...
py -m pip install -r requirements.txt
py -m pip install pyinstaller

echo.
echo Building the Standalone Executable...
py -m PyInstaller --noconsole --onefile --windowed --name="CustomCalendarEngine" main.py

echo.
echo Build Complete! Check the 'dist' folder for CustomCalendarEngine.exe
pause
