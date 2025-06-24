import customtkinter as ctk
import os
import webbrowser
import threading
import time
import requests
import json
from datetime import datetime, timedelta
from plyer import notification
from welcome_page import WelcomeFrame
from login_page import LoginFrame
from preferences_page import PreferencesPage
from information_page import InformationFrame
from flight_info_page import FlightInfoPage

ctk.set_appearance_mode("Light")
ctk.set_default_color_theme("green")

class FlightNotificationService:
    def __init__(self, lat, lon, token, preferences=None, flight_info_callback=None):
        self.lat = float(lat)
        self.lon = float(lon)
        self.token = token
        self.running = False
        self.thread = None
        self.last_flights = set()
        self.flight_info_callback = flight_info_callback
        self.update_preferences(preferences or {})
        
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
        """Check for flights in the area using OpenSky API"""
        try:
            # Calculate bounding box for the radius
            lat_min = self.lat - (self.radius_km / 111.0)  # 1 degree ≈ 111 km
            lat_max = self.lat + (self.radius_km / 111.0)
            lon_min = self.lon - (self.radius_km / (111.0 * abs(self.lat)))
            lon_max = self.lon + (self.radius_km / (111.0 * abs(self.lat)))
            
            # OpenSky API endpoint for state vectors
            url = "https://opensky-network.org/api/states/all"
            params = {
                'lamin': lat_min,
                'lamax': lat_max,
                'lomin': lon_min,
                'lomax': lon_max
            }
            
            headers = {'Authorization': f'Bearer {self.token}'} if self.token else {}
                
            response = requests.get(url, params=params, headers=headers, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if 'states' in data and data['states']:
                    current_flights = set()
                    new_flights = []
                    
                    for state in data['states']:
                        if len(state) >= 17:  # Ensure we have enough data
                            icao24 = state[0]
                            callsign = state[1] if state[1] else "Unknown"
                            origin_country = state[2] if state[2] else "Unknown"
                            altitude = state[7] if state[7] else 0
                            category = state[17] if len(state) > 17 else None
                            
                            # Filter by altitude
                            try:
                                alt_val = float(altitude)
                            except:
                                alt_val = 0
                            if alt_val < self.min_altitude:
                                continue
                            
                            # Filter by flight type
                            if self.flight_type != "All":
                                if not self._match_flight_type(category, self.flight_type):
                                    continue
                            
                            current_flights.add(icao24)
                            
                            # Check if this is a new flight
                            if icao24 not in self.last_flights:
                                new_flights.append({
                                    'icao24': icao24,
                                    'callsign': callsign,
                                    'origin_country': origin_country,
                                    'altitude': altitude
                                })
                    
                    # Send notifications for new flights
                    for flight in new_flights:
                        self._send_notification(flight)
                        if self.flight_info_callback:
                            self.flight_info_callback(flight)
                    
                    self.last_flights = current_flights
                else:
                    print("No flights found in the area")
            else:
                print(f"API request failed with status code: {response.status_code}")
                
        except requests.exceptions.RequestException as e:
            print(f"Network error: {e}")
        except Exception as e:
            print(f"Error checking flights: {e}")
            
    def _send_notification(self, flight):
        """Send a notification for a new flight"""
        try:
            # Create notification message
            altitude_text = f"{flight['altitude']}m" if flight['altitude'] != "Unknown" else "Unknown altitude"
            title = f"✈️ New Flight: {flight['callsign']}"
            message = f"Country: {flight['origin_country']}\nAltitude: {altitude_text}\nTime: {datetime.now().strftime('%H:%M:%S')}"
            
            # Send desktop notification
            try:
                notification.notify(
                    title=title,
                    message=message,
                    app_icon=None,  # e.g. 'C:\\icon_32x32.ico'
                    timeout=10,  # seconds
                )
            except Exception as e:
                print(f"Desktop notification failed: {e}")
            
            # Also print to console for debugging
            print("\n" + "="*50)
            print("🚨 FLIGHT NOTIFICATION")
            print("="*50)
            print(f"Flight: {flight['callsign']}")
            print(f"Country: {flight['origin_country']}")
            print(f"Altitude: {altitude_text}")
            print(f"Time: {datetime.now().strftime('%H:%M:%S')}")
            print("="*50 + "\n")
            
        except Exception as e:
            print(f"Error sending notification: {e}")

    def update_preferences(self, preferences):
        self.radius_km = preferences.get('radius', 50)
        self.flight_type = preferences.get('flight_type', 'All')
        self.min_altitude = preferences.get('min_altitude', 0)
        self.check_interval = preferences.get('frequency', 30)

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
        
        # Initialize notification service and credentials
        self.notification_service = None
        self.client_id = None
        self.client_secret = None
        self.token = None
        self.user_lat = None
        self.user_lon = None
        
        self.preferences = {
            'radius': 50,
            'flight_type': 'All',
            'min_altitude': 0,
            'frequency': 30
        }
        
        self.frames = {}
        self.frames["welcome"] = WelcomeFrame(self, self.show_information)
        self.frames["information"] = InformationFrame(self, self.on_signup_clicked)
        self.frames["login"] = LoginFrame(self, self.on_next)
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
        self.frames["flight_info"].clear_flights()
        self.show_frame("flight_info")
        
    def on_preferences_save(self, radius=50, flight_type="All", min_altitude=0, frequency=30):
        print("Preferences saved!", radius, flight_type, min_altitude, frequency)
        self.preferences = {
            'radius': radius,
            'flight_type': flight_type,
            'min_altitude': min_altitude,
            'frequency': frequency
        }
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
        self.show_location_page()
        
    def on_location_next(self, lat=None, lon=None):
        if lat is not None and lon is not None:
            print(f"Location set: Latitude {lat}, Longitude {lon}")
            self.user_lat = lat
            self.user_lon = lon
            self.notification_service = FlightNotificationService(
                lat, lon, self.token, self.preferences,
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

if __name__ == "__main__":
    app = App()
    app.protocol("WM_DELETE_WINDOW", app.on_closing)
    app.mainloop()  