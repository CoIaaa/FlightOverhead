import customtkinter as ctk
import os
import webbrowser
from welcome_page import WelcomeFrame
from login_page import LoginFrame
from preferences_page import PreferencesPage
from information_page import InformationFrame

ctk.set_appearance_mode("Light")
ctk.set_default_color_theme("green")

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
        self.frames = {}
        self.frames["welcome"] = WelcomeFrame(self, self.show_information)
        self.frames["information"] = InformationFrame(self, self.on_signup_clicked)
        self.frames["login"] = LoginFrame(self, self.on_next)
        self.frames["location"] = LocationFrame(self, self.on_location_next)
        self.frames["preferences"] = PreferencesPage(self, self.on_preferences_save, self.on_preferences_back)
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
    def on_preferences_save(self):
        print("Preferences saved!")
        # Add navigation to next page if needed
    def on_preferences_back(self):
        self.show_location_page()
    def on_next(self, client_id, client_secret, token=None):
        print(f"OpenSky Client ID: {client_id}")
        print(f"OpenSky Client Secret: {client_secret}")
        if token:
            print(f"OAuth2 Access Token: {token}")
        self.show_location_page()
    def on_location_next(self, lat=None, lon=None):
        if lat is not None and lon is not None:
            print(f"Location set: Latitude {lat}, Longitude {lon}")
            self.show_preferences_page()
        else:
            # fallback for direct call
            self.show_preferences_page()

if __name__ == "__main__":
    app = App()
    app.mainloop()  