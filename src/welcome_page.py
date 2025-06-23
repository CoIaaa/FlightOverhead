import customtkinter as ctk
from PIL import Image
import os
import webbrowser

class WelcomeFrame(ctk.CTkFrame):
    def __init__(self, master, start_callback):
        super().__init__(master)
        self.configure(fg_color="#232946")  # Modern dark slate blue background
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        assets_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'assets')
        img_path = os.path.join(assets_dir, 'welcome.png')
        img = Image.open(img_path)
        img = img.transpose(Image.FLIP_LEFT_RIGHT)
        img = img.resize((180, 180), Image.LANCZOS)
        self.welcome_img = ctk.CTkImage(light_image=img, dark_image=img, size=(180, 180))

        # Main card with shadow and rounded corners
        card = ctk.CTkFrame(self, fg_color="#fff", corner_radius=24, width=400, height=520)
        card.grid(row=0, column=0, padx=0, pady=0)
        card.grid_propagate(False)
        card.grid_rowconfigure((0,1,2,3,4,5,6,7), weight=0)
        card.grid_columnconfigure(0, weight=1)

        # Welcome image with drop shadow effect (simulate with a frame)
        img_shadow = ctk.CTkFrame(card, fg_color="#e0e3eb", corner_radius=90, width=120, height=120)
        img_shadow.grid(row=0, column=0, pady=(36, 0), sticky="n")
        img_shadow.grid_propagate(False)
        img_label = ctk.CTkLabel(img_shadow, image=self.welcome_img, text="", fg_color="transparent")
        img_label.place(relx=0.5, rely=0.5, anchor="center")

        # Title
        welcome_label = ctk.CTkLabel(card, text="Flights Overhead", font=("Segoe UI", 30, "bold"), text_color="#232946")
        welcome_label.grid(row=1, column=0, pady=(24, 0), padx=32, sticky="n")
        # Tagline
        tagline = ctk.CTkLabel(card, text="Track flights above you in real time", font=("Segoe UI", 16, "normal"), text_color="#3f8efc")
        tagline.grid(row=2, column=0, pady=(8, 0), padx=32, sticky="n")
        # Description
        desc = ctk.CTkLabel(card, text="Get instant notifications for flights overhead. Powered by OpenSky.", font=("Segoe UI", 13), text_color="#555", wraplength=340, justify="center")
        desc.grid(row=3, column=0, pady=(8, 0), padx=32, sticky="n")

        # Get Started button with vibrant color, pill shape, shadow, and hover effect
        def on_enter(e):
            start_btn.configure(fg_color="#5fa8ff")
        def on_leave(e):
            start_btn.configure(fg_color="#3f8efc")
        start_btn = ctk.CTkButton(
            card,
            text="Get Started",
            command=start_callback,
            width=240,
            height=48,
            font=("Segoe UI", 18, "bold"),
            fg_color="#3f8efc",
            hover_color="#5fa8ff",
            text_color="#fff",
            corner_radius=24,
        )
        start_btn.grid(row=5, column=0, pady=(32, 8), sticky="n")
        start_btn.bind("<Enter>", on_enter)
        start_btn.bind("<Leave>", on_leave)