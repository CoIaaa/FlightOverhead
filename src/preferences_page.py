import customtkinter as ctk
from tkinter import ttk

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
        # Filters & Units Section (grouped together for consistent sizing)
        filters_frame = ctk.CTkFrame(card, fg_color="transparent")
        filters_frame.grid(row=4, column=0, padx=48, pady=(0, 0), sticky="ew")
        filters_frame.grid_columnconfigure((0,1), weight=1)

        # Minimum Altitude
        alt_label = ctk.CTkLabel(filters_frame, text="Minimum Altitude (m)", font=("Segoe UI", 16, "bold"), text_color="#232946")
        alt_label.grid(row=0, column=0, columnspan=2, sticky="w", pady=(0, 2))
        self.alt_var = ctk.StringVar(value="0")
        def validate_numeric(new_value):
            return new_value.isdigit() or new_value == ""
        vcmd = (self.register(validate_numeric), '%P')
        alt_entry = ctk.CTkEntry(filters_frame, textvariable=self.alt_var, placeholder_text="e.g. 1000", font=("Segoe UI", 15), fg_color="#f5f6fa", border_color="#e0e0e0", border_width=2, corner_radius=18, text_color="#232946", width=0, validate="key", validatecommand=vcmd)
        alt_entry.grid(row=1, column=0, columnspan=2, sticky="ew", pady=(0, 8))

        # Unit Conversion
        unit_label = ctk.CTkLabel(filters_frame, text="Unit Conversion", font=("Segoe UI", 16, "bold"), text_color="#232946")
        unit_label.grid(row=2, column=0, columnspan=2, sticky="w", pady=(0, 2))
        self.alt_unit_var = ctk.StringVar(value="ft")
        alt_unit_dropdown = ctk.CTkOptionMenu(
            filters_frame, variable=self.alt_unit_var, values=["ft", "m"],
            fg_color="#e0e3eb", button_color="#3f8efc", corner_radius=18,
            font=("Segoe UI", 15), text_color="#232946", width=0, anchor="w"
        )
        alt_unit_dropdown.grid(row=3, column=0, padx=(0, 8), sticky="ew")
        self.speed_unit_var = ctk.StringVar(value="kt")
        speed_unit_dropdown = ctk.CTkOptionMenu(
            filters_frame, variable=self.speed_unit_var, values=["kt", "km/h", "mph"],
            fg_color="#e0e3eb", button_color="#3f8efc", corner_radius=18,
            font=("Segoe UI", 15), text_color="#232946", width=0, anchor="w"
        )
        speed_unit_dropdown.grid(row=3, column=1, padx=(8, 0), sticky="ew")

        # Airline/Plane Filter (seamless: only CTkOptionMenu for each, side by side)
        filter_label = ctk.CTkLabel(filters_frame, text="Airline/Plane Filter", font=("Segoe UI", 16, "bold"), text_color="#232946")
        filter_label.grid(row=6, column=0, columnspan=2, sticky="w", pady=(16, 2))
        filter_row = ctk.CTkFrame(filters_frame, fg_color="transparent")
        filter_row.grid(row=7, column=0, columnspan=2, sticky="ew")
        filter_row.grid_columnconfigure((0,1), weight=1)
        # Airline filter (dropdown only)
        airline_list = [
            "Major Airlines",
            "--------",
            "AA – American Airlines",
            "AC – Air Canada",
            "AF – Air France",
            "AI – Air India",
            "AM – Aeromexico",
            "AR – Aerolineas Argentinas",
            "AS – Alaska Airlines",
            "AV – Avianca",
            "AY – Finnair",
            "AZ – ITA Airways",
            "BA – British Airways",
            "BI – Royal Brunei Airlines",
            "BR – EVA Air",
            "CA – Air China",
            "CI – China Airlines",
            "CX – Cathay Pacific",
            "CZ – China Southern Airlines",
            "DL – Delta Air Lines",
            "EK – Emirates",
            "ET – Ethiopian Airlines",
            "EY – Etihad Airways",
            "FI – Icelandair",
            "FJ – Fiji Airways",
            "GA – Garuda Indonesia",
            "GF – Gulf Air",
            "HA – Hawaiian Airlines",
            "IB – Iberia",
            "JL – Japan Airlines",
            "KA – Cathay Dragon",
            "KE – Korean Air",
            "KL – KLM Royal Dutch Airlines",
            "LA – LATAM Airlines",
            "LH – Lufthansa",
            "LO – LOT Polish Airlines",
            "LX – Swiss International Air Lines",
            "LY – El Al Israel Airlines",
            "MH – Malaysia Airlines",
            "MS – Egyptair",
            "MU – China Eastern Airlines",
            "NH – All Nippon Airways",
            "NZ – Air New Zealand",
            "OK – Czech Airlines",
            "OS – Austrian Airlines",
            "OZ – Asiana Airlines",
            "PK – Pakistan International Airlines",
            "PR – Philippine Airlines",
            "QF – Qantas",
            "QR – Qatar Airways",
            "RJ – Royal Jordanian",
            "SA – South African Airways",
            "SK – Scandinavian Airlines",
            "SQ – Singapore Airlines",
            "SU – Aeroflot",
            "SV – Saudi Arabian Airlines",
            "TG – Thai Airways International",
            "TK – Turkish Airlines",
            "TP – TAP Air Portugal",
            "UA – United Airlines",
            "UX – Air Europa",
            "VA – Virgin Australia",
            "VS – Virgin Atlantic",
            "WN – Southwest Airlines",
            "WS – WestJet",
            "--------",
            "Low-Cost Airlines",
            "--------",
            "3K – Jetstar Asia Airways",
            "5J – Cebu Pacific",
            "6E – IndiGo",
            "7C – Jeju Air",
            "9C – Spring Airlines",
            "A3 – Aegean Airlines",
            "AD – Azul Brazilian Airlines",
            "AK – AirAsia",
            "AT – Royal Air Maroc",
            "BT – Air Baltic",
            "CM – Copa Airlines",
            "D7 – AirAsia X",
            "DY – Norwegian Air Shuttle",
            "EI – Aer Lingus",
            "EW – Eurowings",
            "FR – Ryanair",
            "G4 – Allegiant Air",
            "G9 – Air Arabia",
            "H9 – Pegasus Airlines",
            "I2 – Iberia Express",
            "JQ – Jetstar Airways",
            "JT – Lion Air",
            "JU – Air Serbia",
            "KM – Air Malta",
            "KX – Cayman Airways",
            "LG – Luxair",
            "LS – Jet2.com",
            "NK – Spirit Airlines",
            "OA – Olympic Air",
            "VN – Vietnam Airlines",
            "--------",
            "Regional Airlines",
            "--------",
            "AAL – American Eagle",
            "ACA – Air Canada Express",
            "ACH – Air One",
            "ACI – Air Caledonie",
            "ACL – Air Caledonia",
            "ACN – Air Canada Rouge",
            "ACO – Air Comet",
            "ADO – Air Do",
            "ADY – Air Dolomiti",
            "ADZ – Air Algerie",
            "AEA – Air Europa Express",
            "AEG – Air East",
            "AFG – Afghan Jet",
            "AGF – Air Gabon",
            "AGU – Air Guatemala",
            "AHK – Air Hong Kong",
            "AJA – Air Jamaica",
            "AJK – Air Japan",
            "AJM – Air Jamaica",
            "AJT – Air Jamaica",
            "AJX – Air Japan Express",
            "AKJ – Air Korea",
            "AKK – Air Korea",
            "AKL – Air Korea",
            "AKT – Air Korea",
            "AKX – Air Korea Express",
            "ALK – Air Lanka",
            "ALV – Air Liberia",
            "AMB – Air Madagascar",
            "AMC – Air Madagascar",
            "AMF – Air Madagascar",
            "AMM – Air Madagascar",
            "AMP – Air Madagascar",
            "AMS – Air Madagascar",
            "AMT – Air Madagascar",
            "AMU – Air Madagascar",
            "AMV – Air Madagascar",
            "AMW – Air Madagascar",
            "AMX – Air Madagascar",
            "ANE – Air New England",
            "ANG – Air New Guinea",
            "ANK – Air Nauru",
            "ANO – Air Nauru",
            "ANR – Air Nauru",
            "ANS – Air Nauru",
            "ANT – Air Nauru",
            "APC – Air Pacific",
            "APF – Air Pacific",
            "APG – Air Pacific",
            "APJ – Air Pacific",
            "APK – Air Pacific",
            "APZ – Air Pacific",
            "ARA – Air Arabia",
            "--------",
            "Cargo Airlines",
            "--------",
            "ABD – AirBridgeCargo",
            "ABX – ABX Air",
            "ACK – Air Cargo Germany",
            "ACY – Air Cargo Express",
            "AFF – Air France Cargo",
            "AFL – Aeroflot Cargo",
            "AFR – Air France Cargo",
            "AFW – Air France Cargo",
            "FDX – FedEx Express",
            "GTI – Atlas Air",
            "NCR – National Air Cargo",
            "PFT – Polar Air Cargo",
            "UPS – UPS Airlines",
            "--------",
            "Charter Airlines",
            "--------",
            "AAA – Air Charter",
            "ABJ – Air Charter",
            "ABL – Air Charter",
            "ABN – Air Charter",
            "ABP – Air Charter",
            "ABQ – Air Charter",
            "ABR – Air Charter",
            "ABS – Air Charter",
            "ABV – Air Charter",
            "ABW – Air Charter",
            "ABY – Air Charter",
            "ACJ – Air Charter",
            "ACP – Air Charter",
            "AEE – Air Express",
            "AEH – Air Express",
            "AEZ – Air Express",
            "AHW – Air Hong Kong",
            "AHX – Air Hong Kong",
            "AHY – Air Hong Kong",
            "--------",
            "Military/Government",
            "--------",
            "ATC – Air Traffic Control",
            "ATG – Air Traffic Control",
            "ATN – Air Traffic Control",
            "ATX – Air Traffic Control",
            "GAF – German Air Force",
            "RAF – Royal Air Force",
            "USAF – United States Air Force",
            "USN – United States Navy",
            "USMC – United States Marine Corps"
        ]
        self.airline_var = ctk.StringVar(value=airline_list[0])
        self.airline_dropdown = ttk.Combobox(
            filter_row, values=airline_list, textvariable=self.airline_var, state="readonly", width=28
        )
        self.airline_dropdown.grid(row=0, column=0, padx=(0, 16), sticky="ew")
        # Plane type filter (dropdown only)
        plane_list = [
            "Boeing",
            "--------",
            "B737 – Boeing 737",
            "B738 – Boeing 737-800",
            "B739 – Boeing 737-900",
            "B73H – Boeing 737 MAX 8",
            "B73J – Boeing 737 MAX 9",
            "B747 – Boeing 747",
            "B748 – Boeing 747-8",
            "B752 – Boeing 757-200",
            "B753 – Boeing 757-300",
            "B763 – Boeing 767-300",
            "B764 – Boeing 767-400",
            "B772 – Boeing 777-200",
            "B773 – Boeing 777-300",
            "B77L – Boeing 777-200LR",
            "B77W – Boeing 777-300ER",
            "B788 – Boeing 787-8",
            "B789 – Boeing 787-9",
            "B78X – Boeing 787-10",
            "--------",
            "Airbus",
            "--------",
            "A220 – Airbus A220",
            "A223 – Airbus A220-300",
            "A318 – Airbus A318",
            "A319 – Airbus A319",
            "A320 – Airbus A320",
            "A321 – Airbus A321",
            "A20N – Airbus A320neo",
            "A21N – Airbus A321neo",
            "A332 – Airbus A330-200",
            "A333 – Airbus A330-300",
            "A339 – Airbus A330-900neo",
            "A342 – Airbus A340-200",
            "A343 – Airbus A340-300",
            "A345 – Airbus A340-500",
            "A346 – Airbus A340-600",
            "A350 – Airbus A350",
            "A359 – Airbus A350-900",
            "A35K – Airbus A350-1000",
            "A380 – Airbus A380",
            "A388 – Airbus A380-800",
            "--------",
            "Embraer",
            "--------",
            "E135 – Embraer ERJ-135",
            "E145 – Embraer ERJ-145",
            "E170 – Embraer E170",
            "E175 – Embraer E175",
            "E190 – Embraer E190",
            "E195 – Embraer E195",
            "--------",
            "Bombardier",
            "--------",
            "CRJ1 – Bombardier CRJ-100",
            "CRJ2 – Bombardier CRJ-200",
            "CRJ7 – Bombardier CRJ-700",
            "CRJ9 – Bombardier CRJ-900",
            "CRJX – Bombardier CRJ-1000",
            "--------",
            "ATR",
            "--------",
            "AT42 – ATR 42",
            "AT43 – ATR 42-300",
            "AT45 – ATR 42-500",
            "AT46 – ATR 42-600",
            "AT72 – ATR 72",
            "AT73 – ATR 72-200",
            "AT75 – ATR 72-500",
            "AT76 – ATR 72-600",
            "--------",
            "Other",
            "--------",
            "AN24 – Antonov An-24",
            "AN26 – Antonov An-26",
            "AN32 – Antonov An-32",
            "AN72 – Antonov An-72",
            "AN74 – Antonov An-74",
            "AN124 – Antonov An-124",
            "AN225 – Antonov An-225",
            "IL62 – Ilyushin Il-62",
            "IL76 – Ilyushin Il-76",
            "IL86 – Ilyushin Il-86",
            "IL96 – Ilyushin Il-96",
            "TU134 – Tupolev Tu-134",
            "TU154 – Tupolev Tu-154",
            "TU204 – Tupolev Tu-204",
            "SU95 – Sukhoi Superjet 100",
            "MC21 – Irkut MC-21",
            "--------",
            "COMAC",
            "--------",
            "C919 – COMAC C919",
            "ARJ21 – COMAC ARJ21",
            "--------",
            "Regional",
            "--------",
            "SF34 – Saab 340",
            "SF50 – Saab 2000",
            "DHC6 – De Havilland DHC-6 Twin Otter",
            "DHC8 – De Havilland DHC-8 Dash 8",
            "DHC9 – De Havilland DHC-8-100",
            "DH8A – De Havilland DHC-8-200",
            "DH8B – De Havilland DHC-8-300",
            "DH8C – De Havilland DHC-8-400",
            "F50 – Fokker 50",
            "F70 – Fokker 70",
            "F100 – Fokker 100",
            "BAE1 – British Aerospace BAe 146",
            "BAE2 – British Aerospace BAe ATP",
            "J328 – Fairchild Dornier 328JET",
            "--------",
            "Military",
            "--------",
            "C130 – Lockheed C-130 Hercules",
            "C135 – Boeing C-135 Stratolifter",
            "C141 – Lockheed C-141 Starlifter",
            "C5M – Lockheed C-5M Super Galaxy",
            "KC10 – McDonnell Douglas KC-10 Extender",
            "KC135 – Boeing KC-135 Stratotanker",
            "E3 – Boeing E-3 Sentry",
            "E4 – Boeing E-4 Nightwatch",
            "P3 – Lockheed P-3 Orion",
            "P8 – Boeing P-8 Poseidon"
        ]
        self.plane_var = ctk.StringVar(value=plane_list[0])
        self.plane_dropdown = ttk.Combobox(
            filter_row, values=plane_list, textvariable=self.plane_var, state="readonly", width=28
        )
        self.plane_dropdown.grid(row=0, column=1, padx=(0, 0), sticky="ew")

        # Notification Frequency (now inside filters_frame)
        freq_label = ctk.CTkLabel(filters_frame, text="Notification Frequency (s)", font=("Segoe UI", 16, "bold"), text_color="#232946")
        freq_label.grid(row=8, column=0, columnspan=2, pady=(16, 2), sticky="w")
        self.freq_var = ctk.StringVar(value="30")
        freq_entry = ctk.CTkEntry(filters_frame, textvariable=self.freq_var, placeholder_text="e.g. 30", font=("Segoe UI", 15), fg_color="#f5f6fa", border_color="#e0e0e0", border_width=2, corner_radius=18, text_color="#232946", width=0, validate="key", validatecommand=vcmd)
        freq_entry.grid(row=9, column=0, columnspan=2, padx=(0, 0), pady=(0, 0), sticky="ew")

        # Save and Back Buttons
        btn_row = ctk.CTkFrame(card, fg_color="transparent")
        btn_row.grid(row=10, column=0, padx=48, pady=(24, 24), sticky="ew")
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
            alt_unit = self.alt_unit_var.get()
            speed_unit = self.speed_unit_var.get()
            self.on_save(radius, flight_type, min_altitude, frequency, alt_unit, speed_unit)
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

    def show_airline_menu(self):
        pass  # To be implemented

    def show_plane_menu(self):
        pass  # To be implemented 