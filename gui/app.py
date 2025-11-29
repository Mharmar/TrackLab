# gui/app.py
import tkinter as tk
from utils.colors import COLORS
from gui.landing_page import LandingPage
from gui.login_page import LoginPage
from gui.dashboard_page import DashboardPage
from gui.borrow_page import BorrowPage
from gui.reports_page import ReportsPage
from gui.equipment_page import EquipmentPage
from gui.profile_page import ProfilePage # <--- 1. Import this

class TrackLabApp:
    def __init__(self, root):
        self.root = root
        self.root.title("TrackLab - Laboratory Equipment System")
        self.root.geometry("1100x750")
        
        self.container = tk.Frame(self.root, bg=COLORS["bg_light"])
        self.container.pack(fill="both", expand=True)

        self.show_landing_page()

    def clear_container(self):
        for widget in self.container.winfo_children():
            widget.destroy()

    # --- Navigation Functions ---
    def show_landing_page(self):
        self.clear_container()
        LandingPage(self.container, self).pack(fill="both", expand=True)

    def show_login_page(self):
        self.clear_container()
        LoginPage(self.container, self).pack(fill="both", expand=True)

    def show_dashboard(self):
        self.clear_container()
        DashboardPage(self.container, self).pack(fill="both", expand=True)

    def show_borrow_page(self):
        self.clear_container()
        BorrowPage(self.container, self).pack(fill="both", expand=True)

    def show_reports(self):
        self.clear_container()
        ReportsPage(self.container, self).pack(fill="both", expand=True)

    def show_equipment_page(self):
        self.clear_container()
        EquipmentPage(self.container, self).pack(fill="both", expand=True)

    # --- 2. Add this function ---
    def show_profile_page(self):
        self.clear_container()
        ProfilePage(self.container, self).pack(fill="both", expand=True)