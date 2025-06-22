import time
import requests
import json
import threading
from datetime import datetime
import os
from plyer import notification
import sys

# Get the absolute path of the project's root directory
# This is two levels up from the current script's location (src/desktop_notifier.py)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Add the root directory to the Python path to allow importing 'secrets'
sys.path.append(BASE_DIR)

# --- Define asset and logo paths based on the root directory ---
ASSETS_DIR = os.path.join(BASE_DIR, 'assets')
LOGOS_DIR = os.path.join(BASE_DIR, 'logos')
DEFAULT_ICON = os.path.join(ASSETS_DIR, 'flight_icon.ico')

# Configuration
QUERY_DELAY = 15  # How often to query FlightRadar24 (seconds)
BOUNDS_BOX = "51.6,51.4,-0.3,-0.1"  # Default to London area - will be overridden by secrets.py

# URLs
FLIGHT_SEARCH_HEAD = "https://data-cloud.flightradar24.com/zones/fcgi/feed.js?bounds="
FLIGHT_SEARCH_TAIL = "&faa=1&satellite=1&mlat=1&flarm=1&adsb=1&gnd=0&air=1&vehicles=0&estimated=0&maxage=14400&gliders=0&stats=0&ems=1&limit=1"
FLIGHT_SEARCH_URL = FLIGHT_SEARCH_HEAD + BOUNDS_BOX + FLIGHT_SEARCH_TAIL

# OpenSky Network API URL
OPENSKY_URL = "https://opensky-network.org/api/states/all?icao24="

# Used to get more flight details with a fr24 flight ID from the initial search
FLIGHT_LONG_DETAILS_HEAD = "https://data-live.flightradar24.com/clickhandler/?flight="

# Request headers
rheaders = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:106.0) Gecko/20100101 Firefox/106.0",
    "cache-control": "no-store, no-cache, must-revalidate, post-check=0, pre-check=0",
    "accept": "application/json"
}

# --- Load secrets if available ---
config_path = os.path.join(BASE_DIR, 'config.py')
print(f"Attempting to load config from: {config_path}")

if os.path.exists(config_path):
    try:
        from config import secrets
        BOUNDS_BOX = secrets.get("bounds_box", BOUNDS_BOX)
        FLIGHT_SEARCH_URL = FLIGHT_SEARCH_HEAD + BOUNDS_BOX + FLIGHT_SEARCH_TAIL
        print("✅ Successfully loaded bounds_box from config.py.")
    except Exception as e:
        print(f"❌ Found config.py, but failed to load it. Reason: {e}")
        print("Using default bounds box.")
else:
    print("⚠️ No config.py found. Using default bounds box.")
    print("   To set a precise location, run: python tools/get_precise_location.py")

# Ensure the final URL is set
FLIGHT_SEARCH_URL = FLIGHT_SEARCH_HEAD + BOUNDS_BOX + FLIGHT_SEARCH_TAIL

def get_opensky_state(icao24):
    """Fetch live altitude and speed from OpenSky Network."""
    if not icao24:
        return None
    try:
        url = OPENSKY_URL + icao24.lower()
        response = requests.get(url, timeout=5)
        response.raise_for_status()
        data = response.json()
        if data and data.get("states"):
            state = data["states"][0]
            # state[7] is barometric altitude in meters
            # state[9] is velocity (ground speed) in m/s
            altitude_m = state[7]
            speed_ms = state[9]
            if altitude_m is not None and speed_ms is not None:
                return {"altitude_m": altitude_m, "speed_ms": speed_ms}
    except Exception:
        # Silently fail; we'll fall back to FR24 data
        pass
    return None

def get_flight_details(flight_id):
    """Fetch detailed flight information from FlightRadar24"""
    try:
        url = FLIGHT_LONG_DETAILS_HEAD + flight_id
        response = requests.get(url, headers=rheaders, timeout=10)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"Error fetching flight details: {e}")
        return None

def parse_flight_details(flight_data, icao24=None):
    """Parse FR24 details and enrich with live OpenSky data if available."""
    try:
        # Extract flight information
        flight_number = flight_data.get("identification", {}).get("number", {}).get("default", "")
        flight_callsign = flight_data.get("identification", {}).get("callsign", "")
        aircraft_code = flight_data.get("aircraft", {}).get("model", {}).get("code", "")
        aircraft_model = flight_data.get("aircraft", {}).get("model", {}).get("text", "")
        airline_name = flight_data.get("airline", {}).get("name", "")
        airline_icao = flight_data.get("airline", {}).get("code", {}).get("icao", "")
        
        # Airport information
        origin = flight_data.get("airport", {}).get("origin", {})
        destination = flight_data.get("airport", {}).get("destination", {})
        
        origin_name = origin.get("name", "").replace(" Airport", "")
        origin_code = origin.get("code", {}).get("iata", "")
        dest_name = destination.get("name", "").replace(" Airport", "")
        dest_code = destination.get("code", {}).get("iata", "")
        
        # Flight identification
        flight_id = flight_number if flight_number else flight_callsign
        
        # Get altitude and speed
        altitude_ft = None
        speed_kts = None
        
        # Try to get live data from OpenSky first
        opensky_data = get_opensky_state(icao24)
        
        if opensky_data:
            print(f"Got live data from OpenSky for {icao24}")
            alt_m = opensky_data.get("altitude_m")
            spd_ms = opensky_data.get("speed_ms")
            if alt_m is not None:
                altitude_ft = int(alt_m * 3.28084)
            if spd_ms is not None:
                speed_kts = int(spd_ms * 1.94384) # m/s to knots
        
        # Fallback to FR24 data if OpenSky fails or has no data
        if altitude_ft is None:
            print(f"Falling back to FR24 data for flight {flight_id}")
            trail = flight_data.get("trail", [])
            if trail and len(trail) > 0:
                # Search from the end for the last nonzero alt/spd
                for entry in reversed(trail):
                    altitude_m = entry.get("alt")
                    speed_kmh = entry.get("spd")
                    if altitude_m not in (None, 0) and speed_kmh not in (None, 0):
                        altitude_ft = int(altitude_m * 3.28084)
                        speed_kts = int(speed_kmh * 0.539957)
                        break
        
        return {
            "flight_id": flight_id,
            "airline": airline_name,
            "airline_icao": airline_icao,
            "origin": f"{origin_code} - {origin_name}",
            "destination": f"{dest_code} - {dest_name}",
            "aircraft": f"{aircraft_code} - {aircraft_model}",
            "altitude_ft": altitude_ft,
            "speed_kts": speed_kts
        }
    except Exception as e:
        print(f"Error parsing flight details: {e}")
        return None

def show_flight_notification(flight_info):
    """Show a desktop notification for the flight"""
    title = f"✈️ Flight Overhead: {flight_info['flight_id']}"
    
    # Condensed message for Windows notification limits
    line2 = f"{flight_info['airline']} | {flight_info['aircraft']}"
    route = f"{flight_info['origin'].split(' - ')[0]} → {flight_info['destination'].split(' - ')[0]}"
    details = []
    if flight_info['altitude_ft'] is not None:
        details.append(f"{flight_info['altitude_ft']:,} ft")
    if flight_info['speed_kts'] is not None:
        details.append(f"{flight_info['speed_kts']} kt")
    line3 = f"{route}"
    if details:
        line3 += " | " + " | ".join(details)
    line4 = f"{datetime.now().strftime('%H:%M:%S')}"
    message = f"{line2}\n{line3}\n{line4}"
    
    # Dynamically select airline logo if it exists, otherwise use default
    airline_icao_code = flight_info.get('airline_icao', '').upper()
    logo_filename_ico = os.path.join(LOGOS_DIR, f"{airline_icao_code}.ico")
    
    icon_path = DEFAULT_ICON # Default icon
    if os.path.exists(logo_filename_ico):
        icon_path = logo_filename_ico
        
    try:
        notification.notify(
            title=title,
            message=message,
            app_icon=icon_path,
            timeout=10,  # seconds
        )
        print(f"Notification sent for flight: {flight_info['flight_id']}")
    except Exception as e:
        print(f"Error showing notification: {e}")
        # Fallback to console output
        print(f"\n{'='*50}")
        print(title)
        print(message)
        print(f"{'='*50}\n")

def get_flights():
    """Look for flights overhead, return flight_id and icao24."""
    try:
        response = requests.get(FLIGHT_SEARCH_URL, headers=rheaders, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        if len(data) == 3:  # Valid response with flights
            for flight_id, flight_info_list in data.items():
                # Skip metadata fields
                if not (flight_id == "version" or flight_id == "full_count"):
                    if len(flight_info_list) > 13:  # Valid flight data
                        icao24 = flight_info_list[0]
                        return {"flight_id": flight_id, "icao24": icao24}
        return None
    except Exception as e:
        print(f"Error fetching flights: {e}")
        return None

def main():
    """Main loop to monitor flights and show notifications"""
    print("Flight Portal Desktop Notifier")
    print(f"Monitoring area: {BOUNDS_BOX}")
    print(f"Query interval: {QUERY_DELAY} seconds")
    print("Press Ctrl+C to stop\n")
    
    last_flight_id = None
    notification_count = 0
    
    try:
        while True:
            print(f"[{datetime.now().strftime('%H:%M:%S')}] Checking for flights...")
            
            flight_data = get_flights()
            
            if flight_data:
                flight_id = flight_data["flight_id"]
                icao24 = flight_data["icao24"]
                
                if flight_id == last_flight_id:
                    print(f"Same flight {flight_id} still overhead")
                else:
                    print(f"New flight {flight_id} ({icao24}) detected!")
                    
                    # Get detailed flight information from FR24
                    fr24_details = get_flight_details(flight_id)
                    if fr24_details:
                        # Enrich with OpenSky data
                        enriched_info = parse_flight_details(fr24_details, icao24)
                        if enriched_info:
                            show_flight_notification(enriched_info)
                            notification_count += 1
                        else:
                            print("Failed to parse flight details")
                    else:
                        print("Failed to fetch flight details from FR24")
                    
                    last_flight_id = flight_id
            else:
                if last_flight_id:
                    print("No flights currently overhead")
                    last_flight_id = None
            
            print(f"Waiting {QUERY_DELAY} seconds before next check...\n")
            time.sleep(QUERY_DELAY)
            
    except KeyboardInterrupt:
        print(f"\nStopped. Total notifications sent: {notification_count}")
        print("Thanks for using Flight Portal Desktop Notifier!")

if __name__ == "__main__":
    main() 