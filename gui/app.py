import tkinter as tk
from PIL import Image, ImageTk, ImageOps # Import PIL
import os # Import os to handle paths
from utils.colors import COLORS
# Import pages normally (this order is necessary for circular dependency fix)
from gui.landing_page import LandingPage
from gui.login_page import LoginPage
from gui.dashboard_page import DashboardPage
from gui.borrow_page import BorrowPage
from gui.reports_page import ReportsPage
from gui.equipment_page import EquipmentPage
from gui.profile_page import ProfilePage 

class TrackLabApp:
    def __init__(self, root):
        self.root = root
        self.root.title("TrackLab - Laboratory Equipment System")
        
        self.root.geometry("1280x850") 
        try: self.root.state('zoomed')
        except:
            width = self.root.winfo_screenwidth()
            height = self.root.winfo_screenheight()
            self.root.geometry(f"{width}x{height}")
        
        # Logo attribute (Accessed via self.controller.logo_image on child pages)
        self.logo_image = self.load_logo()
        
        self.container = tk.Frame(self.root, bg=COLORS["bg_light"])
        self.container.pack(fill="both", expand=True)

        self.show_landing_page()

    def load_logo(self):
        """Loads and prepares the tracklablogo.png from the utils folder.
        
        FIX: Uses os.getcwd() to anchor the path to the directory where python was executed,
        which is the most reliable way when running main.py from the root."""
        
        # Get the directory where the python script was executed (D:\MHAR IDE\LabTrack)
        root_dir = os.getcwd() 
        # Construct path: D:\MHAR IDE\LabTrack\utils\tracklablogo.png
        logo_path = os.path.join(root_dir, 'utils', 'tracklablogo.png')
        
        try:
            # --- Load image using the standardized path ---
            img = Image.open(logo_path)
            
            # --- Ensure strict aspect ratio calculation for quality ---
            new_height = 40
            aspect_ratio = img.width / img.height
            new_width = max(1, int(new_height * aspect_ratio))
            
            resized_img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
            print(f"✅ Logo loaded successfully from: {logo_path}")
            return ImageTk.PhotoImage(resized_img)
            
        except FileNotFoundError:
            print(f"❌ Error: Logo file not found. Expected path: {logo_path}. Using text fallback.")
            return None
        except Exception as e:
            print(f"❌ Error loading logo image: {e}. Using text fallback.")
            return None

    def clear_container(self):
        for widget in self.container.winfo_children():
            widget.destroy()

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

    def show_profile_page(self):
        self.clear_container()
        ProfilePage(self.container, self).pack(fill="both", expand=True)