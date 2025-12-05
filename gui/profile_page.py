# gui/profile_page.py
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from PIL import Image, ImageTk, ImageDraw, ImageOps 
import os
from utils.colors import COLORS
from utils.session import Session
from utils.id_generator import format_contact_number, generate_formatted_id
from database.users_db import update_user_profile, update_profile_image
# FIX: Removed circular import here

class ProfilePage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg=COLORS["bg_light"])
        self.controller = controller
        self.is_editing = False
        
        self.user_data = Session.get_user()
        if not self.user_data:
            self.user_data = {"username": "Guest", "role": "Student", "user_id": 0}

        self.build_ui()

    def build_ui(self):
        # --- NAV BAR ---
        nav_bar = tk.Frame(self, bg="white", height=60, padx=20)
        nav_bar.pack(side="top", fill="x", pady=(0, 2))

        # --- LOGO INTEGRATION ---
        if self.controller.logo_image:
            tk.Label(nav_bar, image=self.controller.logo_image, bg="white").pack(side="left", pady=10, padx=5)
        else:
            tk.Label(nav_bar, text="TRACKLAB", font=("Arial", 16, "bold"), 
                     fg=COLORS["primary_green"], bg="white").pack(side="left", pady=15)
        # ------------------------
        
        nav_items = ["Dashboard", "Equipment", "Borrow", "Reports", "Profile"]
        for item in nav_items:
            cmd = None
            if item == "Dashboard": cmd = self.controller.show_dashboard
            elif item == "Equipment": cmd = self.controller.show_equipment_page
            elif item == "Borrow": cmd = self.controller.show_borrow_page
            elif item == "Reports": cmd = self.controller.show_reports

            color = COLORS["primary_green"] if item == "Profile" else "#555"
            font_style = ("Arial", 10, "bold") if item == "Profile" else ("Arial", 10)
            tk.Button(nav_bar, text=item, bg="white", fg=color, relief="flat", 
                      font=font_style, command=cmd).pack(side="right", padx=10, pady=15)

        # --- MAIN CONTENT ---
        main = tk.Frame(self, bg=COLORS["bg_light"])
        main.pack(fill="both", expand=True, padx=40, pady=20)

        tk.Label(main, text="My Profile", font=("Arial", 22, "bold"), 
                 bg=COLORS["bg_light"], fg=COLORS["text_dark"]).pack(anchor="w", pady=(0, 20))

        split = tk.Frame(main, bg=COLORS["bg_light"])
        split.pack(fill="both", expand=True)
        split.columnconfigure(0, weight=1)
        split.columnconfigure(1, weight=3)

        # --- LEFT CARD ---
        left_card = tk.Frame(split, bg="white", padx=20, pady=30)
        left_card.grid(row=0, column=0, sticky="n", padx=(0, 20))
        
        # Avatar Area (Canvas)
        self.avatar_size = 120
        self.avatar_canvas = tk.Canvas(left_card, width=self.avatar_size, height=self.avatar_size, 
                                       bg="white", highlightthickness=0)
        self.avatar_canvas.pack(pady=(0, 10))
        
        self.load_current_avatar()

        tk.Button(left_card, text="📷 Upload Picture", bg="white", fg="#1976D2", 
                  relief="flat", font=("Arial", 9, "bold"), cursor="hand2",
                  command=self.upload_photo).pack(pady=(0, 20))

        name_display = self.user_data.get('username', 'User')
        role_display = self.user_data.get('role', 'Member')
        
        tk.Label(left_card, text=name_display, font=("Arial", 14, "bold"), bg="white").pack()
        tk.Label(left_card, text=role_display, font=("Arial", 10), bg="#E8F5E9", fg="#2E7D32", padx=10, pady=2).pack(pady=5)

        ttk.Separator(left_card, orient="horizontal").pack(fill="x", pady=20)

        tk.Button(left_card, text="Log Out", bg="#FFEBEE", fg="#D32F2F", 
                  relief="flat", font=("Arial", 10, "bold"), pady=8, cursor="hand2", width=20,
                  command=self.logout_action).pack(side="bottom")

        # --- RIGHT CARD ---
        right_card = tk.Frame(split, bg="white", padx=40, pady=40)
        right_card.grid(row=0, column=1, sticky="nsew")

        header_row = tk.Frame(right_card, bg="white")
        header_row.pack(fill="x", pady=(0, 20))
        tk.Label(header_row, text="Account Details", font=("Arial", 14, "bold"), bg="white", fg=COLORS["primary_green"]).pack(side="left")
        
        self.edit_btn = tk.Button(header_row, text="✎ Edit Profile", bg="#E3F2FD", fg="#1976D2", 
                                  relief="flat", font=("Arial", 9, "bold"), padx=15, cursor="hand2",
                                  command=self.toggle_edit)
        self.edit_btn.pack(side="right")

        self.entries = {}
        
        raw_id = self.user_data.get('user_id', 0)
        role = self.user_data.get('role', 'Student')
        formatted_id = generate_formatted_id(role, raw_id)

        self.create_field(right_card, "Username", self.user_data.get('username', ''), locked=True)
        self.create_field(right_card, "System ID", formatted_id, locked=True)
        self.create_field(right_card, "Email Address", self.user_data.get('email', ''), locked=False)
        self.create_field(right_card, "Department", self.user_data.get('department', ''), locked=False)
        
        formatted_contact = format_contact_number(self.user_data.get('contact', ''))
        self.create_field(right_card, "Contact Number", formatted_contact, locked=False, is_number=True)

        self.save_btn = tk.Button(right_card, text="Save Changes", bg=COLORS["primary_green"], fg="white",
                                  relief="flat", font=("Arial", 10, "bold"), padx=20, pady=10, cursor="hand2",
                                  command=self.save_profile)

    def create_field(self, parent, label, value, locked=False, is_number=False):
        container = tk.Frame(parent, bg="white")
        container.pack(fill="x", pady=10)
        tk.Label(container, text=label, bg="white", font=("Arial", 9, "bold"), fg="#555").pack(anchor="w")
        vcmd = (self.register(self.validate_input), '%P', str(is_number))
        entry = tk.Entry(container, relief="solid", bd=1, font=("Arial", 11), 
                         disabledbackground="#FAFAFA", disabledforeground="#333",
                         validate="key", validatecommand=vcmd)
        if value is None: value = ""
        entry.insert(0, value)
        entry.config(state="disabled")
        entry.pack(fill="x", ipady=8, pady=(5, 0))
        self.entries[label] = {"widget": entry, "locked": locked}

    def validate_input(self, new_text, is_number_str):
        if len(new_text) > 50: return False
        if is_number_str == "True":
            if not all(c.isdigit() or c == '-' for c in new_text): return False
        return True

    def toggle_edit(self):
        if not self.is_editing:
            self.is_editing = True
            self.edit_btn.config(text="Cancel", bg="#FFEBEE", fg="#D32F2F")
            self.save_btn.pack(pady=20, anchor="e")
            for data in self.entries.values():
                if not data["locked"]: data["widget"].config(state="normal", bg="white")
        else:
            self.is_editing = False
            self.edit_btn.config(text="✎ Edit Profile", bg="#E3F2FD", fg="#1976D2")
            self.save_btn.pack_forget()
            for data in self.entries.values():
                data["widget"].config(state="disabled", bg="#FAFAFA")

    def save_profile(self):
        email = self.entries["Email Address"]["widget"].get().strip()
        dept = self.entries["Department"]["widget"].get().strip()
        contact = self.entries["Contact Number"]["widget"].get().strip()

        if email and "@" not in email:
            messagebox.showerror("Error", "Invalid Email Address.")
            return
        
        clean_contact = contact.replace("-", "")
        if clean_contact and not clean_contact.isdigit():
             messagebox.showerror("Error", "Contact must be numbers.")
             return

        user_id = self.user_data.get('user_id')
        if update_user_profile(user_id, email, clean_contact, dept):
            messagebox.showinfo("Success", "Profile Updated!")
            self.user_data.update({'email': email, 'department': dept, 'contact': clean_contact})
            Session.set_user(self.user_data)
            
            formatted = format_contact_number(clean_contact)
            w = self.entries["Contact Number"]["widget"]
            w.config(state="normal")
            w.delete(0, tk.END)
            w.insert(0, formatted)
            w.config(state="disabled")
            self.toggle_edit()
        else:
            messagebox.showerror("Error", "Database Update Failed.")

    def load_current_avatar(self):
        self.avatar_canvas.delete("all")
        path = self.user_data.get("profile_image")
        size = self.avatar_size
        
        initials = "".join([n[0] for n in self.user_data.get('username', 'U').split()[:2]]).upper()
        
        try:
            if path and os.path.exists(path):
                img = Image.open(path)
                img = ImageOps.fit(img, (size, size), method=Image.Resampling.LANCZOS)
                
                mask = Image.new('L', (size, size), 0)
                draw = ImageDraw.Draw(mask)
                draw.ellipse((0, 0, size, size), fill=255)
                
                output = Image.new('RGBA', (size, size), (0,0,0,0))
                output.paste(img, (0, 0), mask)
                
                self.tk_image = ImageTk.PhotoImage(output)
                self.avatar_canvas.create_image(size//2, size//2, image=self.tk_image)
                return
        except Exception as e:
            print(f"Image Load Error: {e}")

        self.avatar_canvas.create_oval(5, 5, size-5, size-5, fill="#E0E0E0", outline="")
        self.avatar_canvas.create_text(size//2, size//2, 
                                       text=initials, font=("Arial", 32, "bold"), fill="#777")

    def upload_photo(self):
        file_path = filedialog.askopenfilename(filetypes=[("Images", "*.png;*.jpg;*.jpeg")])
        if file_path:
            user_id = self.user_data.get('user_id')
            if update_profile_image(user_id, file_path):
                self.user_data['profile_image'] = file_path
                Session.set_user(self.user_data)
                self.load_current_avatar() 
                messagebox.showinfo("Success", "Picture Updated!")
            else:
                messagebox.showerror("Error", "Failed to save image path.")

    def logout_action(self):
        if messagebox.askyesno("Log Out", "Are you sure?"):
            Session.clear()
            self.controller.show_login_page()