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

### Step 2: Set Your Precise Location

This is the most important step! To make the notifier monitor the area above *you* (instead of the default London), you need to set your location.

Run the setup script from your terminal:
```bash
python tools/get_precise_location.py
```
The script will guide you through getting your GPS coordinates and will create a `config.py` file for you.

### Step 3: Run the Notifier

You're all set! To start monitoring for flights, run the main application:
```bash
python src/desktop_notifier.py
```
Now, just leave the script running in the background. It will check for flights every 15 seconds and send a notification when one is detected overhead.

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
    pyinstaller --onefile --windowed --add-data "assets;assets" --add-data "logos;logos" --icon "assets/fo.ico" src/desktop_notifier.py
    ```
    Your final `FlightPortal.exe` (or similar) will be inside the `dist` folder.
