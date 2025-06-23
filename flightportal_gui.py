import customtkinter as ctk
from PIL import Image, ImageTk
import os
import webbrowser
import tkinter as tk
import requests

ctk.set_appearance_mode("System")  # Modes: "System", "Dark", "Light"
ctk.set_default_color_theme("green")  # Use green for the button

class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Flights Overhead")
        self.geometry("600x650")
        self.resizable(False, False)
        icon_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "flight_icon.ico")
        if os.path.exists(icon_path):
            try:
                self.iconbitmap(icon_path)
            except Exception as e:
                print(f"Could not set window icon: {e}")
        else:
            print(f"Icon file not found: {icon_path}")
        # Set the main window background to OpenSky's background color
        self.configure(fg_color="#f4f8fb")

        # Center the card using grid
        self.grid_rowconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

        self.welcome_frame = WelcomeFrame(self, self.show_login)
        self.login_frame = LoginFrame(self, self.on_next)

        self.welcome_frame.grid(row=0, column=0, rowspan=2, columnspan=2, sticky="nsew")

    def show_login(self):
        self.welcome_frame.grid_forget()
        self.login_frame.grid(row=0, column=0, rowspan=2, columnspan=2, sticky="nsew")
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

    def show_welcome(self):
        self.login_frame.grid_forget()
        self.welcome_frame.grid(row=0, column=0, rowspan=2, columnspan=2, sticky="nsew")

    def show_location_page(self):
        self.configure(fg_color="#dbeafe")
        # Destroy or hide the login card
        for widget in self.winfo_children():
            widget.destroy()
        # Main card (no shadow, match login card style)
        card = ctk.CTkFrame(self, fg_color="#ffffff", corner_radius=18, width=340)
        card.place(relx=0.5, rely=0.5, anchor="c")
        card.grid_columnconfigure(0, weight=1)
        row = 0
        title = ctk.CTkLabel(card, text="Set Your Location", font=("Arial", 20, "bold"), text_color="#222831")
        title.grid(row=row, column=0, pady=(28, 8), padx=32, sticky="ew"); row += 1
        subtitle = ctk.CTkLabel(card, text="Enter your coordinates to receive flight notifications for your area.", font=("Arial", 12), text_color="#555")
        subtitle.grid(row=row, column=0, pady=(0, 18), padx=32, sticky="ew"); row += 1
        # Latitude
        def validate_coord_input(new_value):
            # Allow empty, digits, one dot, and one leading minus
            if new_value == "":
                return True
            import re
            return bool(re.fullmatch(r'-?\d*\.?\d*', new_value))
        vcmd = (self.register(validate_coord_input), '%P')
        lat_label = ctk.CTkLabel(card, text="Latitude (e.g. 37.7749)", font=("Arial", 12), text_color="#222831", anchor="w")
        lat_label.grid(row=row, column=0, pady=(0, 0), padx=32, sticky="w"); row += 1
        self.lat_var = tk.StringVar()
        lat_frame = ctk.CTkFrame(card, fg_color="white", border_color="#b0b3b8", border_width=2, corner_radius=8, width=240, height=48)
        lat_frame.grid(row=row, column=0, pady=(2, 10), padx=32, sticky="ew"); row += 1
        lat_frame.grid_propagate(False)
        lat_entry = ctk.CTkEntry(lat_frame, textvariable=self.lat_var, placeholder_text="e.g. 37.7749", font=("Arial", 14), fg_color="transparent", border_width=0, text_color="#222831", validate="key", validatecommand=vcmd)
        lat_entry.pack(fill="both", expand=True, padx=8, pady=2)
        # Longitude
        lon_label = ctk.CTkLabel(card, text="Longitude (e.g. -122.4194)", font=("Arial", 12), text_color="#222831", anchor="w")
        lon_label.grid(row=row, column=0, pady=(0, 0), padx=32, sticky="w"); row += 1
        self.lon_var = tk.StringVar()
        lon_frame = ctk.CTkFrame(card, fg_color="white", border_color="#b0b3b8", border_width=2, corner_radius=8, width=240, height=48)
        lon_frame.grid(row=row, column=0, pady=(2, 4), padx=32, sticky="ew"); row += 1
        lon_frame.grid_propagate(False)
        lon_entry = ctk.CTkEntry(lon_frame, textvariable=self.lon_var, placeholder_text="e.g. -122.4194", font=("Arial", 14), fg_color="transparent", border_width=0, text_color="#222831", validate="key", validatecommand=vcmd)
        lon_entry.pack(fill="both", expand=True, padx=8, pady=2)
        # Error label
        self.coord_error = ctk.CTkLabel(card, text="", text_color="#e74c3c", font=("Arial", 13, "bold"), anchor="center", justify="center")
        self.coord_error.grid(row=row, column=0, padx=32, pady=(0, 8), sticky="ew"); row += 1
        # Save button (styled like Sign in)
        sign_btn_style = {
            'width': 240,
            'height': 38,
            'font': ("Arial", 15, "bold"),
            'fg_color': "#000040",
            'text_color': "#ffffff",
            'hover_color': "#222266",
            'corner_radius': 8
        }
        save_btn = ctk.CTkButton(card, text="Save", command=self.on_location_next, **sign_btn_style)
        save_btn.grid(row=row, column=0, columnspan=2, pady=(0, 20), padx=(24,24), sticky="ew")

    def on_next(self, client_id, client_secret, token=None):
        print(f"OpenSky Client ID: {client_id}")
        print(f"OpenSky Client Secret: {client_secret}")
        if token:
            print(f"OAuth2 Access Token: {token}")
        self.show_location_page()

    def on_location_next(self):
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
        print(f"Location set: Latitude {lat}, Longitude {lon}")
        # Proceed to next step (e.g., notification settings)

class WelcomeFrame(ctk.CTkFrame):
    def __init__(self, master, start_callback):
        super().__init__(master)
        self.configure(fg_color="#dbeafe")
        self.grid_rowconfigure((0,1,2,3,4,5,6), weight=1)
        self.grid_columnconfigure(0, weight=1)

        # Load and display the welcome image
        assets_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'assets')
        img_path = os.path.join(assets_dir, 'welcome.png')
        img = Image.open(img_path)
        img = img.transpose(Image.FLIP_LEFT_RIGHT)  # Flip horizontally
        img.thumbnail((180, 180), Image.LANCZOS)  # Maintain aspect ratio
        self.welcome_img = ImageTk.PhotoImage(img)
        img_label = ctk.CTkLabel(self, image=self.welcome_img, text="")
        img_label.grid(row=1, column=0, pady=(30, 0), sticky="nsew")

        # Welcome headline
        welcome_label = ctk.CTkLabel(self, text="Welcome to Flights Overhead!", font=("Arial", 28, "bold"), text_color="#222831")
        welcome_label.grid(row=2, column=0, pady=(10, 0), sticky="n")
        subtitle = ctk.CTkLabel(self, text="Click below to get started!", font=("Arial", 16), text_color="#555")
        subtitle.grid(row=3, column=0, pady=(5, 0), padx=20, sticky="n")
        # Down arrow image
        down_arrow_path = os.path.join(assets_dir, 'down_arrow.png')
        arrow_img = Image.open(down_arrow_path)
        arrow_img.thumbnail((80, 80), Image.LANCZOS)
        self.arrow_img = ImageTk.PhotoImage(arrow_img)
        arrow_label = ctk.CTkLabel(self, image=self.arrow_img, text="")
        arrow_label.grid(row=4, column=0, pady=(10, 0), padx=0, sticky="nsew")
        # Green Get Started button
        start_btn = ctk.CTkButton(self, text="Get Started", command=start_callback, width=220, height=48, font=("Arial", 18, "bold"), fg_color="#22c55e", hover_color="#16a34a")
        start_btn.grid(row=5, column=0, pady=(20, 40), sticky="n")

class LoginFrame(ctk.CTkFrame):
    def __init__(self, master, on_next_callback, *args, **kwargs):
        super().__init__(master, *args, **kwargs)
        self.on_next_callback = on_next_callback
        self.configure(fg_color="#dbeafe")
        # Use a 3x3 grid for perfect centering
        for i in range(3):
            self.grid_rowconfigure(i, weight=1)
            self.grid_columnconfigure(i, weight=1)

        # Load eye icons
        assets_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'assets')
        eye_img_path = os.path.join(assets_dir, 'eye.png')
        eye_slash_img_path = os.path.join(assets_dir, 'eye_slash.png')
        self.eye_icon = ctk.CTkImage(light_image=Image.open(eye_img_path), dark_image=Image.open(eye_img_path), size=(24, 24))
        self.eye_slash_icon = ctk.CTkImage(light_image=Image.open(eye_slash_img_path), dark_image=Image.open(eye_slash_img_path), size=(24, 24))

        # Centered card frame (fixed size, perfectly centered)
        card = ctk.CTkFrame(self, fg_color="white", corner_radius=18, width=340, height=410)
        card.grid(row=1, column=1, padx=0, pady=0)
        card.grid_propagate(False)
        card.grid_rowconfigure((0,1,2,3,4,5,6,7,8,9,10,11), weight=0)
        card.grid_columnconfigure(0, weight=1)
        card.grid_columnconfigure(1, weight=1)

        # Title and subtitle (left-aligned)
        title = ctk.CTkLabel(card, text="Connect to OpenSky", font=("Arial", 20, "bold"), text_color="#222831", anchor="w", justify="left")
        title.grid(row=0, column=0, columnspan=2, pady=(24, 0), padx=(24,0), sticky="w")
        subtitle = ctk.CTkLabel(card, text="Please enter your details", font=("Arial", 13), text_color="#555", anchor="w", justify="left")
        subtitle.grid(row=1, column=0, columnspan=2, pady=(2, 12), padx=(24,0), sticky="w")

        # Email label and entry (left-aligned, styled)
        email_label_frame = ctk.CTkFrame(card, fg_color="transparent")
        email_label_frame.grid(row=2, column=0, columnspan=2, pady=(0, 0), padx=(24,0), sticky="w")
        email_label = ctk.CTkLabel(email_label_frame, text="Client ID", font=("Arial", 12), text_color="#222831", anchor="w", justify="left")
        email_label.pack(side="left")
        self.username_var = ctk.StringVar()
        email_frame = ctk.CTkFrame(card, fg_color="white", border_color="#b0b3b8", border_width=2, corner_radius=8, width=240, height=48)
        email_frame.grid(row=3, column=0, columnspan=2, pady=(2, 0), padx=(24,24), sticky="ew")
        email_frame.grid_propagate(False)
        user_entry = ctk.CTkEntry(email_frame, textvariable=self.username_var, width=220, height=44, font=("Arial", 14), placeholder_text="E-mail", border_width=0, fg_color="transparent", text_color="#222831")
        user_entry.pack(fill="both", expand=True, padx=8, pady=2)
        # Email error message (placeholder)
        email_error = ctk.CTkLabel(card, text="Please enter a valid email address.", font=("Arial", 10), text_color="#ef4444")
        email_error.grid(row=4, column=0, columnspan=2, pady=(2, 8), padx=(24,0), sticky="w")
        email_error.grid_remove()  # Hide by default

        # Password label and entry (left-aligned, styled)
        pass_label = ctk.CTkLabel(card, text="Client Secret", font=("Arial", 12), text_color="#222831", anchor="w", justify="left")
        pass_label.grid(row=5, column=0, columnspan=2, pady=(0, 0), padx=(24,0), sticky="w")
        self.password_var = ctk.StringVar()
        self.show_password = False
        pass_frame_outer = ctk.CTkFrame(card, fg_color="white", border_color="#b0b3b8", border_width=2, corner_radius=8, width=240, height=48)
        pass_frame_outer.grid(row=6, column=0, columnspan=2, pady=(2, 0), padx=(24,24), sticky="ew")
        pass_frame_outer.grid_propagate(False)
        pass_frame_outer.grid_columnconfigure(0, weight=1)
        pass_frame_outer.grid_columnconfigure(1, weight=0)
        self.pass_entry = ctk.CTkEntry(pass_frame_outer, textvariable=self.password_var, show="*", width=1, height=44, font=("Arial", 14), placeholder_text="Password", border_width=0, fg_color="transparent", text_color="#222831")
        self.pass_entry.grid(row=0, column=0, sticky="ew", padx=(8,0), pady=2)
        show_btn = ctk.CTkButton(pass_frame_outer, image=self.eye_icon, text="", width=48, height=24, command=self.toggle_password, fg_color="#e5e7eb", hover_color="#cbd5e1")
        show_btn.grid(row=0, column=1, padx=(6,8), pady=2, sticky="e")
        self.show_btn = show_btn
        # Password error message (placeholder)
        pass_error = ctk.CTkLabel(card, text="Your password must contain only numbers", font=("Arial", 10), text_color="#ef4444")
        pass_error.grid(row=7, column=0, columnspan=2, pady=(2, 8), padx=(24,0), sticky="w")
        pass_error.grid_remove()  # Hide by default

        # Add Guide.png icon at the bottom left of the card
        guide_img_path = os.path.join(assets_dir, 'Guide.png')
        self.guide_icon = ctk.CTkImage(light_image=Image.open(guide_img_path), dark_image=Image.open(guide_img_path), size=(28, 28))
        guide_icon_label = ctk.CTkLabel(card, image=self.guide_icon, text="", cursor="hand2")
        guide_icon_label.place(relx=0.0, rely=1.0, anchor="sw", x=12, y=-12)
        # Create a text bubble frame for the tooltip (closer to icon, no white square)
        self.info_bubble = ctk.CTkFrame(card, fg_color="#e6f7ff", border_color="#e6f7ff", border_width=0, corner_radius=22)
        self.info_bubble.place(relx=0.0, rely=1.0, anchor="sw", x=38, y=-8)
        self.info_bubble.lower()  # Hide by default
        self.info_label = ctk.CTkLabel(
            self.info_bubble,
            text="1. Log in to your OpenSky account at opensky-network.org\n2. Go to your user page\n3. Click 'Create API' to generate your Client ID and Client Secret",
            font=("Arial", 10),
            text_color="#555",
            justify="left",
            wraplength=180,
            fg_color="#e6f7ff"
        )
        self.info_label.pack(padx=16, pady=(14, 18))
        def show_info(event):
            self.info_bubble.lift()
        def hide_info(event):
            self.info_bubble.lower()
        guide_icon_label.bind("<Enter>", show_info)
        guide_icon_label.bind("<Leave>", hide_info)

        # Sign up to OpenSky button (styled like Sign in, above it)
        signup_btn = ctk.CTkButton(card, text="Sign up to OpenSky", width=240, height=38, font=("Arial", 15, "bold"), fg_color="#000040", text_color="#ffffff", hover_color="#222266", corner_radius=8, command=self.open_opensky_signup)
        signup_btn.grid(row=8, column=0, columnspan=2, pady=(24, 12), padx=(24,24), sticky="ew")

        # Login error message
        self.login_error = ctk.CTkLabel(card, text="", text_color="#e74c3c", font=("Arial", 12, "bold"), anchor="center", justify="center")
        self.login_error.grid(row=10, column=0, columnspan=2, padx=32, pady=(0, 8), sticky="ew")

        # Sign in button (full width, cyan, bold black text)
        sign_btn_style = {
            'width': 240,
            'height': 38,
            'font': ("Arial", 15, "bold"),
            'fg_color': "#000040",
            'text_color': "#ffffff",
            'hover_color': "#222266",
            'corner_radius': 8
        }
        login_btn = ctk.CTkButton(card, text="Continue", command=self.try_login, **sign_btn_style)
        login_btn.grid(row=9, column=0, columnspan=2, pady=(0, 16), padx=(24,24), sticky="ew")
        self.login_btn = login_btn

    def toggle_password(self):
        self.show_password = not self.show_password
        if self.show_password:
            self.pass_entry.configure(show="")
            self.show_btn.configure(image=self.eye_slash_icon)
        else:
            self.pass_entry.configure(show="*")
            self.show_btn.configure(image=self.eye_icon)

    def open_opensky_signup(self):
        webbrowser.open_new_tab("https://opensky-network.org/")

    def try_login(self):
        client_id = self.username_var.get()
        client_secret = self.password_var.get()
        self.login_error.configure(text="Connecting to OpenSky OAuth2...", text_color="#555")
        self.login_btn.configure(state="disabled")
        self.after(100, lambda: self._do_opensky_oauth2(client_id, client_secret))

    def _do_opensky_oauth2(self, client_id, client_secret):
        token_url = "https://auth.opensky-network.org/auth/realms/opensky-network/protocol/openid-connect/token"
        data = {
            "grant_type": "client_credentials",
            "client_id": client_id,
            "client_secret": client_secret
        }
        try:
            resp = requests.post(token_url, data=data, timeout=10)
            if resp.status_code == 200:
                token = resp.json().get("access_token")
                if token:
                    self.login_error.configure(text="OAuth2 login successful!", text_color="#22c55e")
                    self.login_btn.configure(state="normal")
                    self.after(600, lambda: self.on_next_callback(client_id, client_secret, token))
                else:
                    self.login_error.configure(text="No access token received.", text_color="#e74c3c")
                    self.login_btn.configure(state="normal")
            elif resp.status_code == 401:
                self.login_error.configure(text="Invalid Client ID or Secret.", text_color="#e74c3c")
                self.login_btn.configure(state="normal")
            else:
                self.login_error.configure(text=f"OpenSky OAuth2 error: {resp.status_code}", text_color="#e74c3c")
                self.login_btn.configure(state="normal")
        except Exception as e:
            self.login_error.configure(text="Could not connect to OpenSky OAuth2.", text_color="#e74c3c")
            self.login_btn.configure(state="normal")

if __name__ == "__main__":
    app = App()
    app.mainloop() 