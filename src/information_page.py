import customtkinter as ctk

class InformationFrame(ctk.CTkFrame):
    def __init__(self, master, on_signup_callback):
        super().__init__(master)
        self.configure(fg_color="#232946")  # Modern dark slate blue background
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # Card with shadow effect
        card = ctk.CTkFrame(self, fg_color="#fff", corner_radius=24, width=480, height=420)
        card.grid(row=0, column=0, pady=0, padx=0)
        card.grid_propagate(False)
        card.grid_rowconfigure((0,1,2,3,4), weight=0)
        card.grid_columnconfigure(0, weight=1)

        info_label = ctk.CTkLabel(card, text="OpenSky Account Required", font=("Segoe UI", 24, "bold"), text_color="#232946")
        info_label.grid(row=0, column=0, pady=(40, 10), padx=20, sticky="n")
        info_text = (
            "To use Flights Overhead, you need an OpenSky account.\n"
            "You will need to sign up and create an API application to get your Client ID and Secret.\n\n"
            "Click below to sign up at OpenSky and then come back to enter the details."
        )
        info_message = ctk.CTkLabel(card, text=info_text, font=("Segoe UI", 15), text_color="#555", wraplength=400, justify="center")
        info_message.grid(row=1, column=0, pady=(0, 10), padx=40, sticky="n")
        def on_enter(e):
            signup_btn.configure(fg_color="#5fa8ff")
        def on_leave(e):
            signup_btn.configure(fg_color="#3f8efc")
        signup_btn = ctk.CTkButton(card, text="Sign up", width=220, height=48, font=("Segoe UI", 18, "bold"), fg_color="#3f8efc", text_color="#ffffff", hover_color="#5fa8ff", corner_radius=24, command=on_signup_callback)
        signup_btn.grid(row=2, column=0, pady=(10, 10), sticky="n")
        signup_btn.bind("<Enter>", on_enter)
        signup_btn.bind("<Leave>", on_leave)
        def go_to_login(event=None):
            master.show_login()
        container = ctk.CTkFrame(card, fg_color="transparent")
        container.grid(row=3, column=0, sticky="n", pady=(0, 40))
        already_label = ctk.CTkLabel(container, text="Already have an account? ", font=("Segoe UI", 13, "bold"), text_color="#64748b", anchor="e", justify="right", fg_color="transparent")
        already_label.pack(side="left")
        clickable = ctk.CTkLabel(container, text="Click to login", font=("Segoe UI", 13, "underline"), text_color="#3f8efc", cursor="hand2", fg_color="transparent")
        clickable.pack(side="left")
        clickable.bind("<Button-1>", go_to_login)
        clickable.bind("<Enter>", lambda e: clickable.configure(text_color="#232946"))
        clickable.bind("<Leave>", lambda e: clickable.configure(text_color="#3f8efc")) 