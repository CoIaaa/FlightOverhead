import customtkinter as ctk

class PreferencesPage(ctk.CTkFrame):
    def __init__(self, master, on_save, on_back, **kwargs):
        super().__init__(master, fg_color="#232946", **kwargs)  # Modern dark slate blue background
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # Card for preferences
        card = ctk.CTkFrame(self, fg_color="#fff", corner_radius=24, width=440, height=600)
        card.grid(row=0, column=0, padx=0, pady=0)
        card.grid_propagate(False)
        card.grid_rowconfigure((0,1,2,3,4,5,6,7,8,9,10), weight=0)
        card.grid_columnconfigure(0, weight=1)

        # Title
        self.title = ctk.CTkLabel(card, text="Preferences", font=("Segoe UI", 26, "bold"), text_color="#232946")
        self.title.grid(row=0, column=0, pady=(36, 18), padx=32, sticky="n")

        # Notification Radius
        notif_label = ctk.CTkLabel(card, text="Notification Radius (km)", font=("Segoe UI", 15, "bold"), text_color="#232946")
        notif_label.grid(row=1, column=0, pady=(0, 0), padx=48, sticky="w")
        self.notif_slider = ctk.CTkSlider(card, from_=0, to=2, number_of_steps=2, button_color="#3f8efc", progress_color="#232946")
        self.notif_slider.set(1)
        self.notif_slider.grid(row=2, column=0, padx=48, pady=(2, 0), sticky="ew")
        slider_value = ctk.CTkLabel(card, text="2", font=("Segoe UI", 13), text_color="#3f8efc")
        slider_value.grid(row=3, column=0, padx=48, pady=(0, 12), sticky="w")
        def update_slider_value(val):
            if float(val) == 0:
                slider_value.configure(text="1")
            elif float(val) == 1:
                slider_value.configure(text="2")
            else:
                slider_value.configure(text="5")
        self.notif_slider.configure(command=update_slider_value)

        # Unit Selection
        unit_label = ctk.CTkLabel(card, text="Unit Selection", font=("Segoe UI", 15, "bold"), text_color="#232946")
        unit_label.grid(row=4, column=0, pady=(8, 0), padx=48, sticky="w")
        unit_row = ctk.CTkFrame(card, fg_color="transparent")
        unit_row.grid(row=5, column=0, padx=48, pady=(2, 0), sticky="ew")
        unit_row.grid_columnconfigure((0,1), weight=1)
        self.alt_unit_dropdown = ctk.CTkOptionMenu(
            unit_row, values=["ft", "m"], width=180,
            fg_color="#e0e3eb", button_color="#3f8efc",
            corner_radius=14, font=("Segoe UI", 13),
            text_color="#232946"
        )
        self.alt_unit_dropdown.grid(row=0, column=0, padx=(0, 12), pady=0, sticky="ew")
        self.alt_unit_dropdown.set("ft")

        self.speed_unit_dropdown = ctk.CTkOptionMenu(
            unit_row, values=["kt", "km/h", "mph"], width=180,
            fg_color="#e0e3eb", button_color="#3f8efc",
            corner_radius=14, font=("Segoe UI", 13),
            text_color="#232946"
        )
        self.speed_unit_dropdown.grid(row=0, column=1, padx=(12, 0), pady=0, sticky="ew")
        self.speed_unit_dropdown.set("kt")

        # Flight Type
        type_label = ctk.CTkLabel(card, text="Flight Type", font=("Segoe UI", 15, "bold"), text_color="#232946")
        type_label.grid(row=6, column=0, pady=(16, 0), padx=48, sticky="w")
        self.type_dropdown = ctk.CTkOptionMenu(
            card, values=["All", "Commercial", "Private", "Military"], width=240,
            fg_color="#e0e3eb", button_color="#3f8efc",
            corner_radius=18, font=("Segoe UI", 13),
            text_color="#232946"
        )
        self.type_dropdown.grid(row=7, column=0, padx=48, pady=(2, 0), sticky="ew")
        self.type_dropdown.set("All")

        # Altitude Filter
        alt_label = ctk.CTkLabel(card, text="Altitude Filter (ft)", font=("Segoe UI", 15, "bold"), text_color="#232946")
        alt_label.grid(row=8, column=0, pady=(16, 0), padx=48, sticky="w")
        # Numeric-only entry for altitude
        self.alt_var = ctk.StringVar()
        def validate_altitude(new_value):
            return new_value.isdigit() or new_value == ""
        vcmd = (self.register(validate_altitude), '%P')
        alt_entry = ctk.CTkEntry(card, textvariable=self.alt_var, placeholder_text="e.g. 10000", font=("Segoe UI", 14), fg_color="#f5f6fa", border_color="#e0e0e0", border_width=2, corner_radius=18, text_color="#232946", validate="key", validatecommand=vcmd)
        alt_entry.grid(row=9, column=0, padx=48, pady=(2, 0), sticky="ew")
        # Error label for altitude
        self.alt_error = ctk.CTkLabel(card, text="", text_color="#e74c3c", font=("Segoe UI", 11, "bold"))
        self.alt_error.grid(row=10, column=0, padx=48, pady=(0, 0), sticky="w")

        # Flight Info Box
        info_label = ctk.CTkLabel(card, text="Flight Info", font=("Segoe UI", 13, "bold"), text_color="#3f8efc")
        info_label.grid(row=11, column=0, padx=48, pady=(0, 0), sticky="w")
        info_box = ctk.CTkTextbox(card, width=320, height=60, state="disabled", fg_color="#f5f6fa", border_color="#e0e0e0", border_width=2, corner_radius=18, font=("Segoe UI", 12))
        info_box.grid(row=12, column=0, padx=48, pady=(2, 0), sticky="ew")

        # Save and Back Buttons
        btn_row = ctk.CTkFrame(card, fg_color="transparent")
        btn_row.grid(row=13, column=0, padx=48, pady=(24, 24), sticky="ew")
        btn_row.grid_columnconfigure((0,1), weight=1)
        btn_height = 44
        btn_radius = 22
        def on_enter_save(e):
            save_btn.configure(fg_color="#5fa8ff")
        def on_leave_save(e):
            save_btn.configure(fg_color="#3f8efc")
        save_btn = ctk.CTkButton(
            btn_row, text="Save", fg_color="#3f8efc", hover_color="#5fa8ff",
            font=("Segoe UI", 16, "bold"), width=140, height=btn_height, corner_radius=btn_radius,
            text_color="#fff", command=on_save
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

        # Configure grid weights
        card.grid_rowconfigure(5, weight=1)
        card.grid_columnconfigure(0, weight=1) 