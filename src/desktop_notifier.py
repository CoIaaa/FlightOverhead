import time
import requests
import json
import threading
from datetime import datetime, timedelta, timezone
import os
from plyer import notification
import sys
import platform
import contextlib

# Add this block for pync fallback on macOS 
if platform.system() == "Darwin": 
    try:
        import pync
    except ImportError:
        pync = None

# Get the absolute path of the project's root directory
# This is two levels up from the current script's location (src/desktop_notifier.py)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Add the root directory to the Python path to allow importing 'secrets'
sys.path.append(BASE_DIR)

# --- Define asset and logo paths based on the root directory ---
ASSETS_DIR = os.path.join(BASE_DIR, 'assets')
LOGOS_DIR = os.path.join(BASE_DIR, 'logos')

# Cross-platform icon handling
if platform.system() == "Darwin":  # macOS
    DEFAULT_ICON = os.path.join(ASSETS_DIR, 'flight_icon.png')
    ICON_EXTENSION = '.png'
else:  # Windows and Linux
    DEFAULT_ICON = os.path.join(ASSETS_DIR, 'flight_icon.ico')
    ICON_EXTENSION = '.ico'

# Configuration
QUERY_DELAY = 15  # How often to query FlightRadar24 (seconds)
BOUNDS_BOX = "51.6,51.4,-0.3,-0.1"  # Default to London area - will be overridden by secrets.py

# URLs
FLIGHT_SEARCH_HEAD = "https://data-cloud.flightradar24.com/zones/fcgi/feed.js?bounds="
FLIGHT_SEARCH_TAIL = "&faa=1&satellite=1&mlat=1&flarm=1&adsb=1&gnd=0&air=1&vehicles=0&estimated=0&maxage=14400&gliders=0&stats=0&ems=1&limit=3"
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
        # Try to import OpenSky OAuth2 credentials
        try:
            from config import (
                opensky_client_id_1, opensky_client_secret_1,
                opensky_client_id_2, opensky_client_secret_2
            )
        except ImportError:
            opensky_client_id_1 = None
            opensky_client_secret_1 = None
            opensky_client_id_2 = None
            opensky_client_secret_2 = None
    except Exception as e:
        print(f"❌ Found config.py, but failed to load it. Reason: {e}")
        print("Using default bounds box.")
        opensky_client_id_1 = None
        opensky_client_secret_1 = None
        opensky_client_id_2 = None
        opensky_client_secret_2 = None
else:
    print("⚠️ No config.py found. Using default bounds box.")
    print("   To set a precise location, run: python tools/get_precise_location.py")
    opensky_client_id_1 = None
    opensky_client_secret_1 = None
    opensky_client_id_2 = None
    opensky_client_secret_2 = None

# Ensure the final URL is set
FLIGHT_SEARCH_URL = FLIGHT_SEARCH_HEAD + BOUNDS_BOX + FLIGHT_SEARCH_TAIL

# --- OpenSky OAuth2 Token Management ---
OSKY_TOKEN_URL = "https://auth.opensky-network.org/auth/realms/opensky-network/protocol/openid-connect/token"
_osky_token_cache = {
    1: {"token": None, "expires": datetime.min},
    2: {"token": None, "expires": datetime.min},
}

def get_opensky_token(client_id, client_secret, which=1):
    now = datetime.now(timezone.utc)
    cache = _osky_token_cache[which]
    if cache["token"] and now < cache["expires"]:
        return cache["token"]
    data = {
        "grant_type": "client_credentials",
        "client_id": client_id,
        "client_secret": client_secret
    }
    try:
        resp = requests.post(OSKY_TOKEN_URL, data=data)
        resp.raise_for_status()
        token = resp.json()["access_token"]
        # Token expires in 30 min, but set to refresh 5 min before expiry
        expires_in = resp.json().get("expires_in", 1800)
        cache["token"] = token
        cache["expires"] = now + timedelta(seconds=expires_in - 300)
        return token
    except Exception as e:
        print(f"[OpenSky] Failed to get OAuth2 token (client {which}): {e}")
        return None

def get_opensky_state(icao24):
    """Fetch live altitude and speed from OpenSky Network using OAuth2. Tries two clients if rate-limited or unauthorized."""
    if not icao24:
        # print("[OpenSky] No ICAO24 provided.")
        return None
    url = OPENSKY_URL + icao24.lower()
    # Try client 1
    # print(f"[OpenSky] Requesting: {url} (Client 1)")
    token1 = get_opensky_token(opensky_client_id_1, opensky_client_secret_1, which=1)
    headers1 = {"Authorization": f"Bearer {token1}"} if token1 else {}
    try:
        response = requests.get(url, timeout=5, headers=headers1)
        if response.status_code == 429 or response.status_code == 401:
            # print(f"[OpenSky] Client 1 rate-limited or unauthorized (status {response.status_code}). Trying Client 2...")
            # Try client 2
            token2 = get_opensky_token(opensky_client_id_2, opensky_client_secret_2, which=2)
            headers2 = {"Authorization": f"Bearer {token2}"} if token2 else {}
            try:
                response2 = requests.get(url, timeout=5, headers=headers2)
                if response2.status_code == 429 or response2.status_code == 401:
                    # print(f"[OpenSky] Client 2 also rate-limited or unauthorized (status {response2.status_code}).")
                    pass
                else:
                    response2.raise_for_status()
                    data2 = response2.json()
                    # print(f"[OpenSky] Response (Client 2): {data2}")
                    if data2 and data2.get("states"):
                        state2 = data2["states"][0]
                        altitude_m2 = state2[7]
                        speed_ms2 = state2[9]
                        if altitude_m2 is not None and speed_ms2 is not None:
                            return {"altitude_m": altitude_m2, "speed_ms": speed_ms2}
            except Exception as e2:
                # print(f"[OpenSky] Error with Client 2: {e2}")
                pass
        else:
            response.raise_for_status()
            data = response.json()
            # print(f"[OpenSky] Response (Client 1): {data}")
            if data and data.get("states"):
                state = data["states"][0]
                altitude_m = state[7]
                speed_ms = state[9]
                if altitude_m is not None and speed_ms is not None:
                    return {"altitude_m": altitude_m, "speed_ms": speed_ms}
    except Exception as e:
        # print(f"[OpenSky] Error: {e}")
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
            # print(f"Got live data from OpenSky for {icao24}")
            alt_m = opensky_data.get("altitude_m")
            spd_ms = opensky_data.get("speed_ms")
            if alt_m is not None:
                altitude_ft = int(alt_m * 3.28084)
            if spd_ms is not None:
                speed_kts = int(spd_ms * 1.94384) # m/s to knots
        
        # Fallback to FR24 data if OpenSky fails or has no data
        if altitude_ft is None:
            # print(f"Falling back to FR24 data for flight {flight_id}")
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
        # print(f"Error parsing flight details: {e}")
        return None

@contextlib.contextmanager
def suppress_stderr():
    with open(os.devnull, 'w') as devnull:
        old_stderr = sys.stderr
        sys.stderr = devnull
        try:
            yield
        finally:
            sys.stderr = old_stderr

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
    logo_filename = os.path.join(LOGOS_DIR, f"{airline_icao_code}{ICON_EXTENSION}")
    
    icon_path = DEFAULT_ICON # Default icon
    if os.path.exists(logo_filename):
        icon_path = logo_filename
        
    try:
        with suppress_stderr():
            notification.notify(
                title=title,
                message=message,
                app_icon=icon_path,
                timeout=10,  # seconds
            )
    except Exception as e:
        # Fallback for macOS using pync
        if platform.system() == "Darwin" and pync is not None:
            try:
                pync.notify(message, title=title)
            except Exception as e2:
                print(f"Error showing notification with pync: {e2}")
                print(f"\n{'='*50}")
                print(title)
                print(message)
                print(f"{'='*50}\n")
        else:
            print(f"Error showing notification: {e}")
            # Fallback to console output
            print(f"\n{'='*50}")
            print(title)
            print(message)
            print(f"{'='*50}\n")

def get_flights():
    """Look for flights overhead, return a list of up to 3 flights (dicts with flight_id and icao24)."""
    flights = []
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
                        flights.append({"flight_id": flight_id, "icao24": icao24})
                        if len(flights) >= 3:
                            break
        return flights if flights else None
    except Exception as e:
        print(f"Error fetching flights: {e}")
        return None

def main():
    """Main loop to monitor flights and show notifications"""
    print("Flight Overhead Desktop Notifier")
    print(f"Monitoring area: {BOUNDS_BOX}")
    print(f"Query interval: {QUERY_DELAY} seconds")
    print("Press Ctrl+C to stop\n")

    notified_flights = set()
    notification_count = 0

    try:
        while True:
            print(f"[{datetime.now().strftime('%H:%M:%S')}] Checking for flights...")
            flights = get_flights()
            current_flight_ids = set()
            if flights:
                for flight in flights:
                    flight_id = flight["flight_id"]
                    icao24 = flight["icao24"]
                    current_flight_ids.add(flight_id)
                    if flight_id not in notified_flights:
                        fr24_details = get_flight_details(flight_id)
                        if fr24_details:
                            enriched_info = parse_flight_details(fr24_details, icao24)
                            if enriched_info:
                                print(f"[{datetime.now().strftime('%H:%M:%S')}] New flight detected: {enriched_info['flight_id']} (ICAO24: {icao24})")
                                print(f"  Airline: {enriched_info['airline']} | Aircraft: {enriched_info['aircraft']}")
                                print(f"  Altitude: {enriched_info['altitude_ft']} ft | Speed: {enriched_info['speed_kts']} kt")
                                print(f"  Route: {enriched_info['origin'].split(' - ')[0]} → {enriched_info['destination'].split(' - ')[0]}")
                                show_flight_notification(enriched_info)
                                notification_count += 1
                                notified_flights.add(flight_id)
                            else:
                                print("Failed to parse flight details")
                        else:
                            print("Failed to fetch flight details from FR24")
                # Remove flights that are no longer overhead from notified_flights
                notified_flights.intersection_update(current_flight_ids)
            else:
                if notified_flights:
                    print("No flights currently overhead")
                    notified_flights.clear()
            print(f"Waiting {QUERY_DELAY} seconds before next check...\n")
            time.sleep(QUERY_DELAY)
    except KeyboardInterrupt:
        print(f"\nStopped. Total notifications sent: {notification_count}")
        print("Thanks for using Flight Overhead Desktop Notifier!")

if __name__ == "__main__":
    main() 