# gui/landing_page.py
import tkinter as tk
from utils.colors import COLORS

class LandingPage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg=COLORS["primary_green"])
        self.controller = controller
        self.build_ui()

    def build_ui(self):
        # Center Content Wrapper
        center_frame = tk.Frame(self, bg=COLORS["primary_green"])
        center_frame.place(relx=0.5, rely=0.5, anchor="center")

        # Icon
        tk.Label(center_frame, text="⚙️\n⏱️", font=("Segoe UI Emoji", 48), 
                 bg=COLORS["primary_green"], fg="white").pack(pady=10)

        # Title
        tk.Label(center_frame, text="TRACKLAB", font=("Arial", 48, "bold"), 
                 bg=COLORS["primary_green"], fg="white").pack()

        # Subtitle
        tk.Label(center_frame, 
                 text="A system that records and tracks lab equipment usage.", 
                 font=("Arial", 12), bg=COLORS["primary_green"], fg="#E8F5E9").pack(pady=10)

        # Open Button -> NOW GOES TO LOGIN PAGE
        tk.Button(center_frame, text="➜  Open", font=("Arial", 14, "bold"),
                  bg="#388E3C", fg="white", relief="flat", padx=30, pady=10,
                  command=self.controller.show_login_page).pack(pady=30)

        # Footer
        tk.Label(self, text="About us   |   Contact: 09613989802", 
                 bg=COLORS["primary_green"], fg="#C8E6C9", font=("Arial", 9)).pack(side="bottom", pady=20)