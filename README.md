# Custom Calendar Engine (CCE)

A complete, standalone Python desktop GUI application for worldbuilders, fantasy, and sci-fi authors to create custom, hierarchical calendar/time systems and track story events across multiple planets.

## Features

- **No Hardcoded 24h Limits:** The engine is based purely on universal "Ticks". You can define an entirely new time system (e.g., Decimal time with 10 hours of 100 minutes, or fantasy systems utilizing "Bells", "Breaths", and "Watches").
- **Multi-Planet Support:** Track time synchronously across multiple planets with entirely different day lengths and year lengths (e.g., Day 45 on Planet A automatically syncs to the exact time on Planet B).
- **Custom Eras, Months, Weekdays:** Completely flexible calendar structures with custom names, lengths, and colors.
- **Holidays & Leap Rules:** Complex scheduling for special days (even intercalary days outside normal months) and intricate leap year exceptions.
- **Astronomy:** Track suns (binary/trinary systems) and calculate dynamic moon phases for any number of moons.
- **Story Event Tracking:** Create, edit, and search through story events attached to specific days. Includes real-time search filtering.
- **Portable Saves:** Everything is saved into a single, easily portable `.worldcal` (JSON) project file.

---

## 🛠️ Installation & Setup (For Developers)

### 1. Prerequisites
- **Python 3.10** or higher installed.

### 2. Install Dependencies
Install the required GUI framework (PyQt6) via pip. Open your terminal or command prompt and run:
```bash
pip install -r requirements.txt
```
*(Note for Windows users: If the above command fails, try running `py -m pip install -r requirements.txt` or `python -m pip install -r requirements.txt` instead)*

### 3. Run from Source
```bash
python main.py
```
*(Note for Windows users: If `python` is not recognized, use `py main.py` instead)*

---

## 📦 Building a Standalone Executable (.exe)

You can easily package this application into a standalone `.exe` file for Windows (or a binary for Linux/Mac) so that end-users do not need Python installed.

### 1. Install PyInstaller
```bash
pip install pyinstaller
```
*(Windows alternative: `py -m pip install pyinstaller`)*

### 2. Run the Build Script
A convenience script `build.sh` is provided. Alternatively, run the command manually:
```bash
pyinstaller --noconsole --onefile --windowed --name="CustomCalendarEngine" main.py
```
- `--noconsole` and `--windowed` ensure no black command prompt window appears behind the GUI.
- `--onefile` packs everything into a single, clean executable.

### 3. Find your Executable
After the build finishes, your standalone application will be located in the newly created `dist/` folder as `CustomCalendarEngine.exe`.

---

## 💿 Creating a Windows Installer

If you want to distribute the app with a proper installation wizard (Next > Next > Install), you can use a free tool like **Inno Setup**.

1. Download and install [Inno Setup](https://jrsoftware.org/isinfo.php).
2. Open Inno Setup and select **Create a new script file using the Script Wizard**.
3. Set your Application Name to `Custom Calendar Engine`.
4. For the **Application main executable file**, browse and select the `CustomCalendarEngine.exe` from your `dist/` folder.
5. Finish the wizard and compile. It will output a professional `mysetup.exe` file that users can run to install your software to `C:\Program Files\`.
