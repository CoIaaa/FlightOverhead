import customtkinter as ctk
from PIL import Image
import os
import webbrowser
import requests
import tkinter as tk

class LoginFrame(ctk.CTkFrame):
    def __init__(self, master, on_next_callback, *args, **kwargs):
        super().__init__(master, *args, **kwargs)
        self.on_next_callback = on_next_callback
        self.configure(fg_color="#232946")  # Modern dark slate blue background
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        assets_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'assets')
        eye_img_path = os.path.join(assets_dir, 'eye.png')
        eye_slash_img_path = os.path.join(assets_dir, 'eye_slash.png')
        eye_img = Image.open(eye_img_path).resize((24, 24), Image.LANCZOS)
        eye_slash_img = Image.open(eye_slash_img_path).resize((24, 24), Image.LANCZOS)
        self.eye_icon = ctk.CTkImage(light_image=eye_img, dark_image=eye_img, size=(24, 24))
        self.eye_slash_icon = ctk.CTkImage(light_image=eye_slash_img, dark_image=eye_slash_img, size=(24, 24))

        # Card with shadow effect
        card = ctk.CTkFrame(self, fg_color="#fff", corner_radius=24, width=400, height=520)
        card.grid(row=0, column=0, padx=0, pady=0)
        card.grid_propagate(False)
        card.grid_rowconfigure((0,1,2,3,4,5,6,7,8,9,10,11), weight=0)
        card.grid_columnconfigure(0, weight=1)
        card.grid_columnconfigure(1, weight=1)

        title = ctk.CTkLabel(card, text="Connect to OpenSky", font=("Segoe UI", 22, "bold"), text_color="#232946", anchor="w", justify="left")
        title.grid(row=0, column=0, columnspan=2, pady=(36, 0), padx=(32,0), sticky="w")
        subtitle = ctk.CTkLabel(card, text="Please enter your details", font=("Segoe UI", 14), text_color="#3f8efc", anchor="w", justify="left")
        subtitle.grid(row=1, column=0, columnspan=2, pady=(2, 18), padx=(32,0), sticky="w")

        email_label_frame = ctk.CTkFrame(card, fg_color="transparent")
        email_label_frame.grid(row=2, column=0, columnspan=2, pady=(0, 0), padx=(32,0), sticky="w")
        email_label = ctk.CTkLabel(email_label_frame, text="Client ID", font=("Segoe UI", 12), text_color="#232946", anchor="w", justify="left")
        email_label.pack(side="left")
        self.username_var = ctk.StringVar()
        email_frame = ctk.CTkFrame(card, fg_color="#f5f6fa", border_color="#e0e0e0", border_width=2, corner_radius=12, width=240, height=48)
        email_frame.grid(row=3, column=0, columnspan=2, pady=(2, 0), padx=(32,32), sticky="ew")
        email_frame.grid_propagate(False)
        user_entry = ctk.CTkEntry(email_frame, textvariable=self.username_var, width=220, height=44, font=("Segoe UI", 14), placeholder_text="E-mail", border_width=0, fg_color="transparent", text_color="#232946")
        user_entry.pack(fill="both", expand=True, padx=8, pady=2)
        email_error = ctk.CTkLabel(card, text="Please enter a valid email address.", font=("Segoe UI", 10), text_color="#ef4444")
        email_error.grid(row=4, column=0, columnspan=2, pady=(2, 8), padx=(32,0), sticky="w")
        email_error.grid_remove()

        pass_label = ctk.CTkLabel(card, text="Client Secret", font=("Segoe UI", 12), text_color="#232946", anchor="w", justify="left")
        pass_label.grid(row=5, column=0, columnspan=2, pady=(0, 0), padx=(32,0), sticky="w")
        self.password_var = ctk.StringVar()
        self.show_password = False
        pass_frame_outer = ctk.CTkFrame(card, fg_color="#f5f6fa", border_color="#e0e0e0", border_width=2, corner_radius=12, width=240, height=48)
        pass_frame_outer.grid(row=6, column=0, columnspan=2, pady=(2, 0), padx=(32,32), sticky="ew")
        pass_frame_outer.grid_propagate(False)
        pass_frame_outer.grid_columnconfigure(0, weight=1)
        pass_frame_outer.grid_columnconfigure(1, weight=0)
        self.pass_entry = ctk.CTkEntry(pass_frame_outer, textvariable=self.password_var, show="*", width=1, height=44, font=("Segoe UI", 14), placeholder_text="Password", border_width=0, fg_color="transparent", text_color="#232946")
        self.pass_entry.grid(row=0, column=0, sticky="ew", padx=(8,0), pady=2)
        show_btn = ctk.CTkButton(pass_frame_outer, image=self.eye_icon, text="", width=48, height=24, command=self.toggle_password, fg_color="#e0e3eb", hover_color="#cbd5e1", corner_radius=12)
        show_btn.grid(row=0, column=1, padx=(6,8), pady=2, sticky="e")
        self.show_btn = show_btn
        pass_error = ctk.CTkLabel(card, text="Your password must contain only numbers", font=("Segoe UI", 10), text_color="#ef4444")
        pass_error.grid(row=7, column=0, columnspan=2, pady=(2, 8), padx=(32,0), sticky="w")
        pass_error.grid_remove()

        # Move error label just above Connect button
        self.login_error = ctk.CTkLabel(card, text="", text_color="#e74c3c", font=("Segoe UI", 12, "bold"), anchor="center", justify="center")
        self.login_error.grid(row=8, column=0, columnspan=2, padx=32, pady=(0, 8), sticky="ew")

        sign_btn_style = {
            'width': 240,
            'height': 48,
            'font': ("Segoe UI", 16, "bold"),
            'fg_color': "#3f8efc",
            'text_color': "#fff",
            'hover_color': "#5fa8ff",
            'corner_radius': 24
        }
        def on_enter(e):
            login_btn.configure(fg_color="#5fa8ff")
        def on_leave(e):
            login_btn.configure(fg_color="#3f8efc")
        login_btn = ctk.CTkButton(card, text="Connect", command=self.try_login, **sign_btn_style)
        login_btn.grid(row=9, column=0, columnspan=2, pady=(28, 8), padx=(32,32), sticky="ew")
        self.login_btn = login_btn
        login_btn.bind("<Enter>", on_enter)
        login_btn.bind("<Leave>", on_leave)

        def go_to_opensky(event=None):
            webbrowser.open_new_tab("https://opensky-network.org/")
        container = ctk.CTkFrame(card, fg_color="transparent")
        container.grid(row=10, column=0, columnspan=2, pady=(0, 18), padx=(32,32), sticky="ew")
        no_account_label = ctk.CTkLabel(container, text="Don't have an account? ", font=("Segoe UI", 12), text_color="#555", anchor="e", justify="right", fg_color="transparent")
        no_account_label.pack(side="left")
        opensky_link = ctk.CTkLabel(container, text="Click to go to OpenSky", font=("Segoe UI", 12, "underline"), text_color="#3f8efc", cursor="hand2", fg_color="transparent")
        opensky_link.pack(side="left")
        opensky_link.bind("<Button-1>", go_to_opensky)
        opensky_link.bind("<Enter>", lambda e: opensky_link.configure(text_color="#232946"))
        opensky_link.bind("<Leave>", lambda e: opensky_link.configure(text_color="#3f8efc"))

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
        if not client_id or not client_secret:
            self.login_error.configure(text="Please fill out both fields.", text_color="#e74c3c")
            return
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