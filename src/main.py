import customtkinter as ctk
import os
import webbrowser
import threading
import time
import requests
import json
from datetime import datetime, timedelta, timezone
from plyer import notification
from welcome_page import WelcomeFrame
from login_page import LoginFrame
from preferences_page import PreferencesPage
from information_page import InformationFrame
from flight_info_page import FlightInfoPage
import math
from winotify import Notification, audio
import sys
import platform
try:
    from platformdirs import user_config_dir
except ImportError:
    user_config_dir = None

ctk.set_appearance_mode("Light")
ctk.set_default_color_theme("green")

# --- FR24 and OpenSky constants and helpers ---
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ASSETS_DIR = os.path.join(BASE_DIR, 'assets')
LOGOS_DIR = os.path.join(BASE_DIR, 'logos')
FLIGHT_SEARCH_HEAD = "https://data-cloud.flightradar24.com/zones/fcgi/feed.js?bounds="
FLIGHT_SEARCH_TAIL = "&faa=1&satellite=1&mlat=1&flarm=1&adsb=1&gnd=0&air=1&vehicles=0&estimated=0&maxage=14400&gliders=0&stats=0&ems=1&limit=3"
BOUNDS_BOX = "51.6,51.4,-0.3,-0.1"  # Default, can be customized
FLIGHT_SEARCH_URL = FLIGHT_SEARCH_HEAD + BOUNDS_BOX + FLIGHT_SEARCH_TAIL
FLIGHT_LONG_DETAILS_HEAD = "https://data-live.flightradar24.com/clickhandler/?flight="
OPENSKY_URL = "https://opensky-network.org/api/states/all?icao24="
OSKY_TOKEN_URL = "https://auth.opensky-network.org/auth/realms/opensky-network/protocol/openid-connect/token"
rheaders = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:106.0) Gecko/20100101 Firefox/106.0",
    "cache-control": "no-store, no-cache, must-revalidate, post-check=0, pre-check=0",
    "accept": "application/json"
}
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
        expires_in = resp.json().get("expires_in", 1800)
        cache["token"] = token
        cache["expires"] = now + timedelta(seconds=expires_in - 300)
        return token
    except Exception as e:
        print(f"[OpenSky] Failed to get OAuth2 token (client {which}): {e}")
        return None

def get_opensky_state(icao24, client_id, client_secret, client_id2=None, client_secret2=None):
    if not icao24:
        return None
    url = OPENSKY_URL + icao24.lower()
    print(f"Querying OpenSky: {url}")
    token1 = get_opensky_token(client_id, client_secret, which=1)
    headers1 = {"Authorization": f"Bearer {token1}"} if token1 else {}
    try:
        response = requests.get(url, timeout=5, headers=headers1)
        print(f"OpenSky response status: {response.status_code}")
        print(f"OpenSky response: {response.text}")
        if response.status_code == 429 or response.status_code == 401:
            if client_id2 and client_secret2:
                token2 = get_opensky_token(client_id2, client_secret2, which=2)
                headers2 = {"Authorization": f"Bearer {token2}"} if token2 else {}
                try:
                    response2 = requests.get(url, timeout=5, headers=headers2)
                    print(f"OpenSky response2 status: {response2.status_code}")
                    print(f"OpenSky response2: {response2.text}")
                    if response2.status_code == 429 or response2.status_code == 401:
                        pass
                    else:
                        response2.raise_for_status()
                        data2 = response2.json()
                        if data2 and data2.get("states"):
                            state2 = data2["states"][0]
                            altitude_m2 = state2[7]
                            speed_ms2 = state2[9]
                            if altitude_m2 is not None and speed_ms2 is not None:
                                return {"altitude_m": altitude_m2, "speed_ms": speed_ms2}
                except Exception as e2:
                    print(f"OpenSky client2 error: {e2}")
                    pass
        else:
            response.raise_for_status()
            data = response.json()
            if data and data.get("states"):
                state = data["states"][0]
                altitude_m = state[7]
                speed_ms = state[9]
                if altitude_m is not None and speed_ms is not None:
                    return {"altitude_m": altitude_m, "speed_ms": speed_ms}
    except Exception as e:
        print(f"OpenSky error: {e}")
        pass
    return None

def get_flight_details(flight_id):
    try:
        url = FLIGHT_LONG_DETAILS_HEAD + flight_id
        response = requests.get(url, headers=rheaders, timeout=10)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"Error fetching flight details: {e}")
        return None

def parse_flight_details(flight_data, icao24=None, client_id=None, client_secret=None, client_id2=None, client_secret2=None):
    try:
        flight_number = flight_data.get("identification", {}).get("number", {}).get("default", "")
        flight_callsign = flight_data.get("identification", {}).get("callsign", "")
        aircraft_code = flight_data.get("aircraft", {}).get("model", {}).get("code", "")
        aircraft_model = flight_data.get("aircraft", {}).get("model", {}).get("text", "")
        airline_name = flight_data.get("airline", {}).get("name", "")
        airline_icao = flight_data.get("airline", {}).get("code", {}).get("icao", "")
        origin = flight_data.get("airport", {}).get("origin", {})
        destination = flight_data.get("airport", {}).get("destination", {})
        origin_code = origin.get("code", {}).get("iata", "")
        dest_code = destination.get("code", {}).get("iata", "")
        livery = flight_data.get("aircraft", {}).get("livery", {}).get("name", None)
        flight_id_val = flight_number if flight_number else flight_callsign
        altitude_ft = None
        speed_kts = None
        opensky_data = get_opensky_state(icao24, client_id, client_secret, client_id2, client_secret2)
        opensky_category = None
        if opensky_data and 'category' in opensky_data:
            opensky_category = opensky_data['category']
        if opensky_data:
            alt_m = opensky_data.get("altitude_m")
            spd_ms = opensky_data.get("speed_ms")
            print(f"[DEBUG] OpenSky altitude_m: {alt_m}")
            if alt_m is not None:
                altitude_ft = int(alt_m * 3.28084)
            if spd_ms is not None:
                speed_kts = int(spd_ms * 1.94384)
        if altitude_ft is None:
            trail = flight_data.get("trail", [])
            if trail and len(trail) > 0:
                for entry in reversed(trail):
                    altitude_m = entry.get("alt")
                    speed_kmh = entry.get("spd")
                    print(f"[DEBUG] FR24 trail altitude: {altitude_m}")
                    if altitude_m not in (None, 0) and speed_kmh not in (None, 0):
                        if altitude_m > 1000:
                            altitude_ft = int(altitude_m * 3.28084)
                        else:
                            altitude_ft = int(altitude_m)
                        speed_kts = int(speed_kmh * 0.539957)
                        break
        # --- Heuristic flight type detection ---
        flight_type = "Unknown"
        # 1. OpenSky category if available
        if opensky_category is not None:
            try:
                cat = int(opensky_category)
                if cat in [3, 4, 5]:
                    flight_type = "Commercial"
                elif cat in [1, 2, 7, 8, 9, 10, 11]:
                    flight_type = "Private"
                elif cat == 16:
                    flight_type = "Military"
            except Exception:
                pass
        # 2. FR24/General heuristics if category not set
        if flight_type == "Unknown":
            if airline_name and flight_number:
                flight_type = "Commercial"
            elif airline_name and ("air force" in airline_name.lower() or "navy" in airline_name.lower() or "army" in airline_name.lower()):
                flight_type = "Military"
            elif flight_callsign and any(flight_callsign.startswith(prefix) for prefix in ["RCH", "MC", "QID", "BAF", "LAGR", "SHELL", "HOBO", "REACH", "PAT", "SNAKE", "MAF"]):
                flight_type = "Military"
            elif flight_callsign and any(flight_callsign.startswith(prefix) for prefix in ["N", "G-", "D-", "F-H", "HB-"]):
                flight_type = "Private"
        return {
            "flight_id": flight_id_val,
            "callsign": flight_callsign,
            "airline": airline_name,
            "airline_icao": airline_icao,
            "origin": origin_code,
            "destination": dest_code,
            "aircraft_type": aircraft_code,
            "aircraft_model": aircraft_model,
            "altitude": altitude_ft,
            "speed": speed_kts,
            "icao24": icao24,
            "livery": livery,
            "flight_type": flight_type
        }
    except Exception as e:
        print(f"Error parsing flight details: {e}")
        return None

def resource_path(relative_path):
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)

class FlightNotificationService:
    def __init__(self, lat, lon, token, client_id=None, client_secret=None, preferences=None, flight_info_callback=None):
        self.lat = float(lat)
        self.lon = float(lon)
        self.token = token
        self.running = False
        self.thread = None
        self.last_flights = set()
        self.flight_info_callback = flight_info_callback
        self.preferences = preferences or {'alt_unit': 'ft', 'speed_unit': 'kt'}
        self.update_preferences(preferences or {})
        self.client_id = client_id
        self.client_secret = client_secret
        self._update_bounding_box()
        
    def start_monitoring(self):
        if self.running:
            return
        self.running = True
        self.thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self.thread.start()
        print(f"Started flight monitoring for coordinates: {self.lat}, {self.lon}")
        
    def stop_monitoring(self):
        self.running = False
        if self.thread:
            self.thread.join(timeout=1)
        print("Stopped flight monitoring")
        
    def _monitor_loop(self):
        while self.running:
            try:
                self._check_flights()
                time.sleep(self.check_interval)
            except Exception as e:
                print(f"Error in flight monitoring: {e}")
                time.sleep(self.check_interval)
                
    def _check_flights(self):
        """Check for flights in the area using FR24 and OpenSky for enrichment"""
        try:
            response = requests.get(self.fr24_url, headers=rheaders, timeout=10)
            if response.status_code == 200:
                data = response.json()
                current_flights = set()
                new_flights = []
                for flight_id, flight_info_list in data.items():
                    if flight_id in ("version", "full_count"):
                        continue
                    if len(flight_info_list) > 13:
                        icao24 = flight_info_list[0]
                        current_flights.add(icao24)
                        if icao24 not in self.last_flights:
                            fr24_details = get_flight_details(flight_id)
                            if fr24_details:
                                enriched = parse_flight_details(
                                    fr24_details, icao24,
                                    client_id=self.client_id,
                                    client_secret=self.client_secret
                                )
                                if enriched:
                                    # --- Filter by user-selected flight type ---
                                    user_type = self.preferences.get('flight_type', 'All')
                                    if user_type == 'All' or enriched.get('flight_type', 'Unknown') == user_type:
                                        new_flights.append(enriched)
                for flight in new_flights:
                    self._send_notification(flight)
                    if self.flight_info_callback:
                        self.flight_info_callback(flight)
                self.last_flights = current_flights
            else:
                print(f"FR24 API request failed with status code: {response.status_code}")
        except Exception as e:
            print(f"Error checking flights: {e}")
            
    def _send_notification(self, flight):
        print("Sending notification for", flight)
        try:
            airline_code = flight.get('airline_icao', '').upper()
            logo_png = resource_path(os.path.join("logos", f"{airline_code}.png"))
            logo_ico = resource_path(os.path.join("logos", f"{airline_code}.ico"))
            logo_path = logo_png if os.path.exists(logo_png) else (logo_ico if os.path.exists(logo_ico) else None)
            callsign = flight.get('callsign', 'Unknown')

            altitude_val = flight.get('altitude', None)
            speed_val = flight.get('speed', None)
            app = None
            try:
                import tkinter
                app = tkinter._default_root
            except Exception:
                pass
            # Always use conversion helpers for both value and unit
            if altitude_val is not None and hasattr(app, 'convert_altitude'):
                if self.preferences.get('alt_unit', 'ft') == 'm':
                    alt_disp, alt_unit = app.convert_altitude(altitude_val / 3.28084)
                else:
                    alt_disp, alt_unit = app.convert_altitude(altitude_val)
            else:
                alt_disp, alt_unit = '???', self.preferences.get('alt_unit', 'ft')
            if speed_val is not None and hasattr(app, 'convert_speed'):
                spd_disp, spd_unit = app.convert_speed(speed_val)
            else:
                spd_disp, spd_unit = '???', self.preferences.get('speed_unit', 'kt')
            print(f"Notification speed: {spd_disp} {spd_unit} (user selected: {self.preferences.get('speed_unit', 'kt')})")

            message_lines = [
                f"{flight.get('airline', 'Unknown Airline')} | {flight.get('aircraft_type', '')} - {flight.get('aircraft_model', '')}",
                f"{flight.get('origin', '???')} → {flight.get('destination', '???')} | "
                f"{alt_disp} {alt_unit} | {spd_disp} {spd_unit}",
                f"{datetime.now().strftime('%H:%M:%S')}"
            ]
            message = "\n".join(message_lines)

            toast = Notification(
                app_id="Flights Overhead",
                title=f"✈️ Flight Overhead: {callsign}",
                msg=message,
                icon=logo_path
            )
            toast.set_audio(audio.Default, loop=False)
            toast.show()
        except Exception as e:
            print(f"Error sending notification: {e}")

    def update_preferences(self, preferences):
        self.radius_km = preferences.get('radius', 50)
        self.flight_type = preferences.get('flight_type', 'All')
        self.min_altitude = preferences.get('min_altitude', 0)
        self.check_interval = preferences.get('frequency', 30)
        self._update_bounding_box()

    def _update_bounding_box(self):
        # Calculate bounding box for the radius (in km)
        lat_min = self.lat - (self.radius_km / 111.0)
        lat_max = self.lat + (self.radius_km / 111.0)
        lon_min = self.lon - (self.radius_km / (111.0 * math.cos(math.radians(self.lat))))
        lon_max = self.lon + (self.radius_km / (111.0 * math.cos(math.radians(self.lat))))
        self.bounding_box = f"{lat_max},{lat_min},{lon_min},{lon_max}"
        self.fr24_url = FLIGHT_SEARCH_HEAD + self.bounding_box + FLIGHT_SEARCH_TAIL

    def _match_flight_type(self, category, flight_type):
        # OpenSky category mapping: 0=No info, 1=Light, 2=Small, 3=Large, 4=High Vortex, 5=Heavy, 6=Highly, 7=Rotorcraft, 8=Glider, 9=Lighter-than-air, 10=Parachutist, 11=Ultralight, 12=Reserved, 13=Unmanned, 14=Space, 15=Surface, 16=Military
        if flight_type == "Commercial":
            return category in [3, 4, 5]
        elif flight_type == "Private":
            return category in [1, 2, 7, 8, 9, 10, 11]
        elif flight_type == "Military":
            return category == 16
        return True

    def set_flight_info_callback(self, callback):
        self.flight_info_callback = callback

class LocationFrame(ctk.CTkFrame):
    def __init__(self, master, on_next_callback):
        super().__init__(master)
        self.on_next_callback = on_next_callback
        self.configure(fg_color="#232946")
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)
        card = ctk.CTkFrame(self, fg_color="#fff", corner_radius=24, width=400, height=340)
        card.place(relx=0.5, rely=0.5, anchor="c")
        card.grid_columnconfigure(0, weight=1)
        card.grid_rowconfigure((0,1,2,3,4,5,6), weight=0)
        title = ctk.CTkLabel(card, text="Set Your Location", font=("Segoe UI", 24, "bold"), text_color="#232946")
        title.grid(row=0, column=0, pady=(36, 8), padx=32, sticky="n")
        subtitle = ctk.CTkLabel(card, text="Enter your coordinates to receive flight notifications for your area.", font=("Segoe UI", 13), text_color="#555")
        subtitle.grid(row=1, column=0, pady=(0, 18), padx=32, sticky="n")
        lat_label = ctk.CTkLabel(card, text="Latitude (e.g. 37.7749)", font=("Segoe UI", 12), text_color="#232946", anchor="w")
        lat_label.grid(row=2, column=0, pady=(0, 0), padx=48, sticky="w")
        self.lat_var = ctk.StringVar()
        def validate_latlon(new_value):
            if new_value in ("", "-"): return True
            try:
                float(new_value)
                return True
            except ValueError:
                return False
        vcmd = (self.register(validate_latlon), '%P')
        lat_entry = ctk.CTkEntry(card, textvariable=self.lat_var, placeholder_text="e.g. 37.7749", font=("Segoe UI", 14), fg_color="#f5f6fa", border_color="#e0e0e0", border_width=2, corner_radius=12, text_color="#232946", validate="key", validatecommand=vcmd)
        lat_entry.grid(row=3, column=0, pady=(2, 12), padx=48, sticky="ew")
        lon_label = ctk.CTkLabel(card, text="Longitude (e.g. -122.4194)", font=("Segoe UI", 12), text_color="#232946", anchor="w")
        lon_label.grid(row=4, column=0, pady=(0, 0), padx=48, sticky="w")
        self.lon_var = ctk.StringVar()
        lon_entry = ctk.CTkEntry(card, textvariable=self.lon_var, placeholder_text="e.g. -122.4194", font=("Segoe UI", 14), fg_color="#f5f6fa", border_color="#e0e0e0", border_width=2, corner_radius=12, text_color="#232946", validate="key", validatecommand=vcmd)
        lon_entry.grid(row=5, column=0, pady=(2, 12), padx=48, sticky="ew")
        self.coord_error = ctk.CTkLabel(card, text="", text_color="#e74c3c", font=("Segoe UI", 13, "bold"), anchor="center", justify="center")
        self.coord_error.grid(row=6, column=0, padx=32, pady=(0, 8), sticky="ew")
        def on_enter(e):
            save_btn.configure(fg_color="#5fa8ff")
        def on_leave(e):
            save_btn.configure(fg_color="#3f8efc")
        save_btn = ctk.CTkButton(card, text="Save", command=self.on_save, width=180, height=44, font=("Segoe UI", 16, "bold"), fg_color="#3f8efc", hover_color="#5fa8ff", text_color="#fff", corner_radius=22)
        save_btn.grid(row=7, column=0, pady=(8, 24), padx=48, sticky="ew")
        save_btn.bind("<Enter>", on_enter)
        save_btn.bind("<Leave>", on_leave)
    def on_save(self):
        lat = self.lat_var.get()
        lon = self.lon_var.get()
        try:
            lat_val = float(lat)
            lon_val = float(lon)
            if not (-90 <= lat_val <= 90 and -180 <= lon_val <= 180):
                raise ValueError
        except ValueError:
            self.coord_error.configure(text="Please enter valid latitude and longitude values.")
            return
        self.coord_error.configure(text="")
        self.on_next_callback(lat, lon)

class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Flights Overhead")
        self.geometry("600x650")
        self.resizable(False, False)
        icon_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "assets", "flight_icon.ico")
        if os.path.exists(icon_path):
            try:
                self.iconbitmap(icon_path)
            except Exception as e:
                print(f"Could not set window icon: {e}")
        else:
            print(f"Icon file not found: {icon_path}")
            self.configure(fg_color="#f4f8fb")
        self.grid_rowconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        
        # --- Credential persistence helpers ---
        def get_settings_path():
            if user_config_dir:
                config_dir = user_config_dir("FlightPortal")
            else:
                config_dir = os.path.expanduser("~/.flightportal")
            os.makedirs(config_dir, exist_ok=True)
            return os.path.join(config_dir, "settings.json")
        self._settings_path = get_settings_path()

        def load_credentials():
            try:
                with open(self._settings_path, "r") as f:
                    data = json.load(f)
                    return data.get("client_id", ""), data.get("client_secret", "")
            except Exception:
                return "", ""
        def save_credentials(client_id, client_secret):
            try:
                with open(self._settings_path, "w") as f:
                    json.dump({"client_id": client_id, "client_secret": client_secret}, f)
            except Exception as e:
                print(f"Error saving credentials: {e}")
        self.load_credentials = load_credentials
        self.save_credentials = save_credentials

        def load_unit_prefs():
            try:
                with open(self._settings_path, "r") as f:
                    data = json.load(f)
                    return data.get("alt_unit", "ft"), data.get("speed_unit", "kt")
            except Exception:
                return "ft", "kt"
        def save_unit_prefs(alt_unit, speed_unit):
            try:
                with open(self._settings_path, "r") as f:
                    data = json.load(f)
            except Exception:
                data = {}
            data["alt_unit"] = alt_unit
            data["speed_unit"] = speed_unit
            with open(self._settings_path, "w") as f:
                json.dump(data, f)
        self.load_unit_prefs = load_unit_prefs
        self.save_unit_prefs = save_unit_prefs

        # Initialize notification service and credentials
        self.notification_service = None
        self.client_id = None
        self.client_secret = None
        self.token = None
        self.user_lat = None
        self.user_lon = None
        
        alt_unit, speed_unit = self.load_unit_prefs()
        self.preferences = {
            'radius': 50,
            'flight_type': 'All',
            'min_altitude': 0,
            'frequency': 30,
            'alt_unit': alt_unit,
            'speed_unit': speed_unit
        }
        
        # --- Check for saved credentials and set initial page ---
        saved_client_id, saved_client_secret = self.load_credentials()
        self.frames = {}
        self.frames["welcome"] = WelcomeFrame(self, self.show_information)
        self.frames["information"] = InformationFrame(self, self.on_signup_clicked)
        self.frames["login"] = LoginFrame(self, self.on_next, prefill_client_id=saved_client_id, prefill_client_secret=saved_client_secret)
        self.frames["location"] = LocationFrame(self, self.on_location_next)
        self.frames["preferences"] = PreferencesPage(self, self.on_preferences_save, self.on_preferences_back)
        self.frames["flight_info"] = FlightInfoPage(
            self,
            on_edit_coords=self.show_location_page,
            on_edit_prefs=self.show_preferences_page
        )
        for frame in self.frames.values():
            frame.grid(row=0, column=0, rowspan=2, columnspan=2, sticky="nsew")
            frame.grid_remove()
        # Show login if credentials exist, else welcome
        if saved_client_id and saved_client_secret:
            self.show_frame("login")
        else:
            self.show_frame("welcome")
        
    def show_frame(self, name):
        for fname, frame in self.frames.items():
            frame.grid_remove()
        self.frames[name].grid()
        
    def show_information(self):
        self.show_frame("information")
        
    def on_signup_clicked(self):
        webbrowser.open_new_tab("https://opensky-network.org/")
        self.show_frame("login")
        
    def show_login(self):
        self.show_frame("login")
        
    def show_welcome(self):
        self.show_frame("welcome")
        
    def show_location_page(self):
        self.show_frame("location")
        
    def show_preferences_page(self):
        self.show_frame("preferences")
        
    def show_flight_info_page(self):
        self.show_frame("flight_info")
        
    def on_preferences_save(self, radius=50, flight_type="All", min_altitude=0, frequency=30, alt_unit="ft", speed_unit="kt"):
        print("Preferences saved!", radius, flight_type, min_altitude, frequency, alt_unit, speed_unit)
        self.preferences = {
            'radius': radius,
            'flight_type': flight_type,
            'min_altitude': min_altitude,
            'frequency': frequency,
            'alt_unit': alt_unit,
            'speed_unit': speed_unit
        }
        self.save_unit_prefs(alt_unit, speed_unit)
        if self.notification_service and self.user_lat and self.user_lon:
            self.notification_service.update_preferences(self.preferences)
            self.notification_service.start_monitoring()
            print("Flight monitoring started!")
        self.show_flight_info_page()
        
    def on_preferences_back(self):
        self.show_location_page()
        
    def on_next(self, client_id, client_secret, token=None):
        print(f"OpenSky Client ID: {client_id}")
        self.client_id = client_id
        self.client_secret = client_secret
        self.token = token
        self.save_credentials(client_id, client_secret)
        self.show_location_page()
        
    def on_location_next(self, lat=None, lon=None):
        if lat is not None and lon is not None:
            print(f"Location set: Latitude {lat}, Longitude {lon}")
            self.user_lat = lat
            self.user_lon = lon
            self.notification_service = FlightNotificationService(
                lat, lon, self.token, self.client_id, self.client_secret, self.preferences,
                flight_info_callback=self.frames["flight_info"].add_flight
            )
            self.show_preferences_page()
        else:
            self.show_preferences_page()
            
    def on_closing(self):
        """Clean up notification service when app closes"""
        if self.notification_service:
            self.notification_service.stop_monitoring()
        self.quit()

    # --- Conversion helpers ---
    def convert_altitude(self, value_m):
        unit = self.preferences.get('alt_unit', 'ft')
        if unit == 'ft':
            return int(round(value_m * 3.28084)), 'ft'
        else:
            return int(round(value_m)), 'm'
    def convert_speed(self, value_kt):
        unit = self.preferences.get('speed_unit', 'kt')
        if unit == 'kt':
            return int(round(value_kt)), 'kt'
        elif unit == 'km/h':
            return int(round(value_kt * 1.852)), 'km/h'
        elif unit == 'mph':
            return int(round(value_kt * 1.15078)), 'mph'
        else:
            return int(round(value_kt)), 'kt'

if __name__ == "__main__":
    app = App()
    app.protocol("WM_DELETE_WINDOW", app.on_closing)
    app.mainloop()  