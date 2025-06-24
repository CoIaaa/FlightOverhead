import customtkinter as ctk

class PreferencesPage(ctk.CTkFrame):
    def __init__(self, master, on_save, on_back, **kwargs):
        super().__init__(master, fg_color="#232946", **kwargs)
        self.on_save = on_save
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)
        card = ctk.CTkFrame(self, fg_color="#fff", corner_radius=24, width=440, height=600, border_color="#d0d0d0", border_width=1)
        card.grid(row=0, column=0, padx=32, pady=32)
        card.grid_propagate(False)
        card.grid_rowconfigure((0,1,2,3,4,5,6,7,8,9,10,11,12,13), weight=0)
        card.grid_columnconfigure(0, weight=1)
        self.title = ctk.CTkLabel(card, text="Preferences", font=("Segoe UI", 26, "bold"), text_color="#232946")
        self.title.grid(row=0, column=0, pady=(36, 18), padx=32, sticky="n")
        # Notification Radius
        notif_label = ctk.CTkLabel(card, text="Notification Radius (km)", font=("Segoe UI", 16, "bold"), text_color="#232946")
        notif_label.grid(row=1, column=0, pady=(0, 6), padx=48, sticky="w")
        self.radius_var = ctk.StringVar(value="50")
        def validate_numeric(new_value):
            return new_value.isdigit() or new_value == ""
        vcmd = (self.register(validate_numeric), '%P')
        radius_entry = ctk.CTkEntry(card, textvariable=self.radius_var, placeholder_text="e.g. 50", font=("Segoe UI", 15), fg_color="#f5f6fa", border_color="#e0e0e0", border_width=2, corner_radius=18, text_color="#232946", width=0, validate="key", validatecommand=vcmd)
        radius_entry.grid(row=2, column=0, padx=48, pady=(0, 16), sticky="ew")
        # Flight Type (grouped in a frame for tight spacing)
        flight_type_frame = ctk.CTkFrame(card, fg_color="transparent")
        flight_type_frame.grid(row=3, column=0, padx=48, pady=(0, 8), sticky="ew")
        flight_type_frame.grid_columnconfigure(0, weight=1)
        type_label = ctk.CTkLabel(flight_type_frame, text="Flight Type", font=("Segoe UI", 16, "bold"), text_color="#232946")
        type_label.pack(anchor="w", pady=(0, 6))
        self.type_dropdown = ctk.CTkOptionMenu(flight_type_frame, values=["All", "Commercial", "Private", "Military"], fg_color="#e0e3eb", button_color="#3f8efc", corner_radius=18, font=("Segoe UI", 15), text_color="#232946", width=0)
        self.type_dropdown.pack(fill="x", pady=(0, 0))
        self.type_dropdown.set("All")
        # Minimum Altitude (grouped in a frame for tight spacing)
        altitude_frame = ctk.CTkFrame(card, fg_color="transparent")
        altitude_frame.grid(row=4, column=0, padx=48, pady=(0, 8), sticky="ew")
        altitude_frame.grid_columnconfigure(0, weight=1)
        alt_label = ctk.CTkLabel(altitude_frame, text="Minimum Altitude (m)", font=("Segoe UI", 16, "bold"), text_color="#232946")
        alt_label.pack(anchor="w", pady=(0, 6))
        self.alt_var = ctk.StringVar(value="0")
        def validate_numeric(new_value):
            return new_value.isdigit() or new_value == ""
        vcmd = (self.register(validate_numeric), '%P')
        alt_entry = ctk.CTkEntry(altitude_frame, textvariable=self.alt_var, placeholder_text="e.g. 1000", font=("Segoe UI", 15), fg_color="#f5f6fa", border_color="#e0e0e0", border_width=2, corner_radius=18, text_color="#232946", width=0, validate="key", validatecommand=vcmd)
        alt_entry.pack(fill="x", pady=(0, 0))
        # Notification Frequency
        freq_label = ctk.CTkLabel(card, text="Notification Frequency (s)", font=("Segoe UI", 16, "bold"), text_color="#232946")
        freq_label.grid(row=7, column=0, pady=(0, 6), padx=48, sticky="w")
        self.freq_var = ctk.StringVar(value="30")
        freq_entry = ctk.CTkEntry(card, textvariable=self.freq_var, placeholder_text="e.g. 30", font=("Segoe UI", 15), fg_color="#f5f6fa", border_color="#e0e0e0", border_width=2, corner_radius=18, text_color="#232946", width=0, validate="key", validatecommand=vcmd)
        freq_entry.grid(row=8, column=0, padx=48, pady=(0, 16), sticky="ew")
        # Save and Back Buttons
        btn_row = ctk.CTkFrame(card, fg_color="transparent")
        btn_row.grid(row=9, column=0, padx=48, pady=(24, 24), sticky="ew")
        btn_row.grid_columnconfigure((0,1), weight=1)
        btn_height = 44
        btn_radius = 24
        def on_enter_save(e):
            save_btn.configure(fg_color="#5fa8ff")
        def on_leave_save(e):
            save_btn.configure(fg_color="#3f8efc")
        def save_preferences():
            radius = float(self.radius_var.get() or 50)
            flight_type = self.type_dropdown.get()
            min_altitude = float(self.alt_var.get() or 0)
            frequency = float(self.freq_var.get() or 30)
            self.on_save(radius, flight_type, min_altitude, frequency)
        save_btn = ctk.CTkButton(
            btn_row, text="Save", fg_color="#3f8efc", hover_color="#5fa8ff",
            font=("Segoe UI", 16, "bold"), width=140, height=btn_height, corner_radius=btn_radius,
            text_color="#fff", command=save_preferences
        )
        save_btn.grid(row=0, column=1, padx=(8,0), sticky="e")
        save_btn.bind("<Enter>", on_enter_save)
        save_btn.bind("<Leave>", on_leave_save)
        def on_enter_back(e):
            back_btn.configure(fg_color="#e0e3eb", text_color="#232946")
        def on_leave_back(e):
            back_btn.configure(fg_color="#cccccc", text_color="#232946")
        back_btn = ctk.CTkButton(
            btn_row, text="Back", fg_color="#cccccc", hover_color="#e0e3eb",
            font=("Segoe UI", 15), width=100, height=btn_height, corner_radius=btn_radius,
            text_color="#232946", command=on_back
        )
        back_btn.grid(row=0, column=0, padx=(0,8), sticky="w")
        back_btn.bind("<Enter>", on_enter_back)
        back_btn.bind("<Leave>", on_leave_back)
        card.grid_rowconfigure(5, weight=1)
        card.grid_columnconfigure(0, weight=1) 