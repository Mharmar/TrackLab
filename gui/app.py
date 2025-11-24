# gui/app.py
import tkinter as tk
from utils.colors import COLORS
from gui.landing_page import LandingPage
from gui.dashboard_page import DashboardPage
from gui.borrow_page import BorrowPage  # <--- Import this

class TrackLabApp:
    def __init__(self, root):
        self.root = root
        self.root.title("TrackLab - Laboratory Equipment System")
        self.root.geometry("1100x750") # Made it slightly bigger
        
        self.container = tk.Frame(self.root, bg=COLORS["bg_light"])
        self.container.pack(fill="both", expand=True)

        self.show_landing_page()

    def clear_container(self):
        for widget in self.container.winfo_children():
            widget.destroy()

    def show_landing_page(self):
        self.clear_container()
        LandingPage(self.container, self).pack(fill="both", expand=True)

    def show_dashboard(self):
        self.clear_container()
        DashboardPage(self.container, self).pack(fill="both", expand=True)

    def show_borrow_page(self):
        self.clear_container()
        BorrowPage(self.container, self).pack(fill="both", expand=True)