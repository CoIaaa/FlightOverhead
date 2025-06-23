# ✈️ Flight Overhead Desktop Notifier

A Python application that monitors the sky above you for air traffic and sends you a desktop notification when a flight is directly overhead. It can even show the airline's logo in the notification!

## Prerequisites

- **Python 3.8+**: Make sure you have Python installed on your system. You can get it from [python.org](https://www.python.org/).

## How to Set Up and Run

Follow these steps to get the application running on your computer.

### Step 1: Install Required Packages

First, install all the necessary Python libraries. Open a terminal or command prompt in this project folder and run:
```bash
pip install -r requirements.txt
```

### Step 2: Start the GUI Application

To launch the Flights Overhead GUI, run:
```bash
python src/main.py
```
This will open a modern desktop app where you can log in, set your preferences, and manage your location.

### Step 3: (Optional) Run the Notifier

If you want to run the background notifier (for desktop notifications), you can still use:
```bash
python src/desktop_notifier.py
```
But most users will use the GUI (`src/main.py`) for all setup and interaction.

---

## (Optional) Advanced Features

### Managing Airline Logos

The application can show airline logos in the notifications. The logos are stored in the `/logos` folder.

- **To add more logos:** You can use the helper script `tools/organize_logos.py` to extract logos from a downloaded zip file (you will need to edit the script to point to your file).
- **To convert PNGs to ICOs:** If you add new `.png` logos, you must convert them to the `.ico` format that Windows requires. Run the conversion script:
  ```bash
  python tools/convert_logos.py
  ```

### Building the `.exe` File

If you want to create a standalone executable file that you can run without needing Python installed (useful for sharing with others), you can use PyInstaller.

1.  **Install PyInstaller:**
    ```bash
    pip install pyinstaller
    ```

2.  **Build the `.exe`:**
    Run this command from the main project folder. It includes the necessary assets.
    ```bash
    pyinstaller --onefile --windowed --add-data "assets;assets" --add-data "logos;logos" --icon "assets/fo.ico" src/main.py
    ```
    Your final `FlightPortal.exe` (or similar) will be inside the `dist` folder.
