# Chronix

A complete, standalone Python desktop GUI application designed for worldbuilders, fantasy authors, and sci-fi writers. **Chronix** allows you to create completely custom, hierarchical calendar and time systems from scratch, and track story events across multiple synchronized planets.

---

## 📖 The Core Philosophy: Universal Ticks

Unlike traditional calendar apps, CCE does **not** assume that a day has 24 hours, or that an hour has 60 minutes.

The entire engine is built on a concept called the **Universal Tick**.
A "Tick" is just a mathematical counter (1, 2, 3...). As the author, **you** define what a Tick represents in your world, and every other unit of time is built by multiplying that Tick.

### Example: Standard Earth Time
- **Base Tick:** `Second`
- **Time Units:**
  - `Minute` = 60 Ticks
  - `Hour` = 3600 Ticks
- **Planet Day Length:** 86,400 Ticks (which equals 24 hours).

### Example: Abstract Fantasy Time
- **Base Tick:** `Breath`
- **Time Units:**
  - `Bell Strike` = 100 Ticks
  - `Watch` = 5000 Ticks
- **Planet Day Length:** 20,000 Ticks (which equals exactly 4 Watches).

By using Ticks as the foundation, CCE can calculate exact moments in time across entirely different planetary systems seamlessly.

---

## 🌍 Features & User Manual

### 1. Multi-Planet Synchronization
Your story might take place across a solar system. In the **Planets & Orbit** tab, you can create multiple planets.
- **Day Length:** Defined in Ticks. (e.g. Planet A takes 100,000 ticks to rotate, Planet B takes 50,000).
- **Year Length:** Defined in local Days.
- **The Magic:** In the Calendar Viewer, if you click on an event on Planet A, you can use the **Sync Dropdown** to instantly see what the exact date and time it is on Planet B at that very moment.

### 2. Earth Synchronization (Real-World Mapping)
Often, authors want to celebrate fantasy events (like a character's birthday) in the real world. CCE includes a robust **Earth Sync** feature.
- **Enable Earth Sync** in the World Tab.
- **Earth Date at Tick 0:** Set the real-world Gregorian date that corresponds to the very beginning of your fantasy calendar (e.g., `2011-09-13T00:00:00`).
- **Real Seconds per Tick:** Define how fast your world moves compared to reality. If 1 Tick = 1 Real Second, put `1.0`. If time in your fantasy world moves twice as fast as the real world, put `0.5`.
- **Result:** When you view a day in the Calendar Viewer, a bright green label will show you exactly what day that is on Earth!

### 3. Eras, Months, and Weekdays
In the **Eras, Months & Weekdays** tab, you have total freedom:
- Create **Eras** (e.g., "Third Age", "Before the Fall") and define what year they start.
- Create **Months or Seasons**. Give them custom names, custom day lengths, and assign them a specific color that will be used to render them in the visual calendar grid.
- Create **Weekdays**. You can have a 3-day week, a 10-day week, or none at all.

### 4. Holidays & Complex Leap Rules
- **Holidays:** You can place holidays on specific days of specific months. Or, you can leave the Month field blank to create an **Intercalary Day**—a special day that exists outside the normal month structure (like a New Year's festival between Winter and Spring).
- **Leap Rules:** Define rules like "Every 4 years, add 1 day to the month of Sun's Height, but skip this rule every 100 years."

### 5. Astronomy: Suns and Moons
- Track binary or trinary sun systems by defining their Dawn and Dusk ticks.
- Add as many **Moons** as you want. Define their lunar cycle in days, and set an offset. The Calendar Viewer will mathematically calculate and display the exact Phase (e.g., "Waxing Crescent") and Illumination percentage of every moon for any given day.

### 6. Visual Calendar & Story Event Tracker
Once your world is built, click **Generate Calendar**.
- You get a visual, color-coded grid of your months.
- Click any day to see its details (Eras, Astronomy, Earth Sync Date).
- Create **Story Events** for that day. Give them a title, start/end ticks, locations, and characters.
- **Live Search:** Use the search bar at the top to search for a character's name or a location. The calendar grid will instantly highlight (in yellow) all days where that character appears!

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

### Windows (Automated)
Just double-click the **`build.bat`** file in the folder!
It automatically uses `py -m pip` to install dependencies and PyInstaller, and then generates the `.exe` for you without any path issues.

### Mac/Linux (Automated)
Run the shell script in your terminal:
```bash
./build.sh
```

### Manual Build
If you want to run it manually:
```bash
pyinstaller --noconsole --onefile --windowed --name="CustomCalendarEngine" main.py
```

### Finding your Executable
After the build finishes, your standalone application will be located in the newly created `dist/` folder as `CustomCalendarEngine.exe`.

---

## 💿 Creating a Windows Installer

If you want to distribute the app with a proper installation wizard (Next > Next > Install), you can use a free tool like **Inno Setup**.

1. Download and install [Inno Setup](https://jrsoftware.org/isinfo.php).
2. Open Inno Setup and select **Create a new script file using the Script Wizard**.
3. Set your Application Name to `Chronix`.
4. For the **Application main executable file**, browse and select the `Chronix.exe` from your `dist/` folder.
5. Finish the wizard and compile. It will output a professional `mysetup.exe` file that users can run to install your software to `C:\Program Files\`.
