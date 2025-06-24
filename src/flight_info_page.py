import customtkinter as ctk

class FlightInfoPage(ctk.CTkFrame):
    def __init__(self, master, on_edit_coords=None, on_edit_prefs=None, **kwargs):
        super().__init__(master, fg_color="#232946", **kwargs)
        self.on_edit_coords = on_edit_coords
        self.on_edit_prefs = on_edit_prefs
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)
        card = ctk.CTkFrame(self, fg_color="#fff", corner_radius=24, width=500, height=600, border_color="#d0d0d0", border_width=1)
        card.grid(row=0, column=0, padx=32, pady=32, sticky="nsew")
        card.grid_propagate(False)
        card.grid_rowconfigure(2, weight=1)
        card.grid_columnconfigure(0, weight=1)
        title = ctk.CTkLabel(card, text="Live Flights Overhead", font=("Segoe UI", 24, "bold"), text_color="#232946")
        title.grid(row=0, column=0, pady=(32, 8), padx=32, sticky="n")
        btn_row = ctk.CTkFrame(card, fg_color="transparent")
        btn_row.grid(row=1, column=0, pady=(0, 16), padx=32, sticky="ew")
        btn_row.grid_columnconfigure((0,1), weight=1)
        btn_radius = 20
        edit_coords_btn = ctk.CTkButton(
            btn_row, text="Edit Coords", fg_color="#e0e3eb", hover_color="#3f8efc", text_color="#232946",
            font=("Segoe UI", 14, "bold"), width=140, height=38, corner_radius=btn_radius,
            command=self._edit_coords
        )
        edit_coords_btn.grid(row=0, column=0, padx=(0,8), sticky="ew")
        edit_prefs_btn = ctk.CTkButton(
            btn_row, text="Edit Preferences", fg_color="#e0e3eb", hover_color="#3f8efc", text_color="#232946",
            font=("Segoe UI", 14, "bold"), width=160, height=38, corner_radius=btn_radius,
            command=self._edit_prefs
        )
        edit_prefs_btn.grid(row=0, column=1, padx=(8,0), sticky="ew")
        self.flight_list = ctk.CTkTextbox(card, width=0, height=480, font=("Segoe UI", 15), fg_color="#f5f6fa", border_color="#e0e0e0", border_width=2, corner_radius=18, text_color="#232946", state="disabled")
        self.flight_list.grid(row=2, column=0, padx=32, pady=(0, 32), sticky="nsew")
        self.clear_flights()
    def _edit_coords(self):
        if self.on_edit_coords:
            self.on_edit_coords()
    def _edit_prefs(self):
        if self.on_edit_prefs:
            self.on_edit_prefs()
    def add_flight(self, flight):
        self.flight_list.configure(state="normal")
        livery = flight.get('livery', None)
        msg = (
            f"Callsign: {flight.get('callsign', 'Unknown')}\n"
            f"Route: {flight.get('origin', '???')} → {flight.get('destination', '???')}\n"
            f"Altitude: {flight.get('altitude', '???')} ft | Speed: {flight.get('speed', '???')} kt\n"
            f"Aircraft: {flight.get('aircraft_type', '???')} - {flight.get('aircraft_model', '???')}\n"
        )
        if livery:
            msg += f"Livery: {livery}\n"
        msg += "--------------------------------\n"
        self.flight_list.insert("end", msg)
        self.flight_list.see("end")
        self.flight_list.configure(state="disabled")
    def clear_flights(self):
        self.flight_list.configure(state="normal")
        self.flight_list.delete("1.0", "end")
        self.flight_list.configure(state="disabled") 