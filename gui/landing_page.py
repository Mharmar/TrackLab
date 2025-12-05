# gui/landing_page.py
import tkinter as tk
from PIL import Image, ImageTk 
import os # Import os for path construction
from utils.colors import COLORS
# REMOVED: from gui.app import TrackLabApp # FIX: Circular Import

class LandingPage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg=COLORS["primary_green"])
        self.controller = controller
        # Dedicated reference for the large logo on this page
        self.landing_logo = None 
        self.build_ui()

    def load_landing_logo(self):
        """Loads a larger version of the logo for the main screen, preserving aspect ratio."""
        
        # Determine the root of the project to find the file
        root_dir = os.getcwd() 
        logo_path = os.path.join(root_dir, 'utils', 'tracklablogo.png')
        
        try:
            img = Image.open(logo_path)
            
            # --- FIX: Calculate new size based on max dimension (150px) while maintaining aspect ratio ---
            max_size = 150
            original_width, original_height = img.size
            
            if original_width > original_height:
                # Scale by width
                new_width = max_size
                new_height = int(max_size * original_height / original_width)
            else:
                # Scale by height
                new_height = max_size
                new_width = int(max_size * original_width / original_height)

            # Ensure minimal size (max(1, ...))
            new_width = max(1, new_width)
            new_height = max(1, new_height)
            
            resized_img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
            self.landing_logo = ImageTk.PhotoImage(resized_img)
            return self.landing_logo
            
        except FileNotFoundError:
            # Print error from the core module (app.py handles the general error printing)
            return None
        except Exception as e:
            print(f"❌ Landing Page Logo Load Error: {e}")
            return None

    def build_ui(self):
        # Center Content Wrapper
        center_frame = tk.Frame(self, bg=COLORS["primary_green"])
        center_frame.place(relx=0.5, rely=0.5, anchor="center")

        # --- LOGO INTEGRATION ---
        logo_ref = self.load_landing_logo()
        
        if logo_ref:
            tk.Label(center_frame, image=logo_ref, 
                     bg=COLORS["primary_green"]).pack(pady=10)
        else:
             # Fallback if image fails (using old icon/text)
             tk.Label(center_frame, text="⚙️\n⏱️", font=("Segoe UI Emoji", 48), 
                      bg=COLORS["primary_green"], fg="white").pack(pady=10)
        # ------------------------


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