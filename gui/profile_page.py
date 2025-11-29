# gui/profile_page.py
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from utils.colors import COLORS

class ProfilePage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg=COLORS["bg_light"])
        self.controller = controller
        self.is_editing = False
        self.build_ui()

    def build_ui(self):
        # NAV BAR
        nav_bar = tk.Frame(self, bg="white", height=60, padx=20)
        nav_bar.pack(side="top", fill="x", pady=(0, 2))

        tk.Label(nav_bar, text="TRACKLAB", font=("Arial", 16, "bold"), 
                 fg=COLORS["primary_green"], bg="white").pack(side="left", pady=15)
        
        nav_items = ["Dashboard", "Equipment", "Borrow", "Reports", "Profile"]
        for item in nav_items:
            if item == "Profile":
                cmd = None
            elif item == "Dashboard":
                cmd = self.controller.show_dashboard
            elif item == "Equipment":
                cmd = self.controller.show_equipment_page
            elif item == "Borrow":
                cmd = self.controller.show_borrow_page
            elif item == "Reports":
                cmd = self.controller.show_reports
            else:
                cmd = None

            color = COLORS["primary_green"] if item == "Profile" else "#555"
            font_style = ("Arial", 10, "bold") if item == "Profile" else ("Arial", 10)

            tk.Button(nav_bar, text=item, bg="white", fg=color, relief="flat", 
                      font=font_style, command=cmd).pack(side="right", padx=10, pady=15)

        # MAIN CONTENT
        main = tk.Frame(self, bg=COLORS["bg_light"])
        main.pack(fill="both", expand=True, padx=40, pady=20)

        tk.Label(main, text="My Profile", font=("Arial", 22, "bold"), 
                 bg=COLORS["bg_light"], fg=COLORS["text_dark"]).pack(anchor="w", pady=(0, 20))

        split = tk.Frame(main, bg=COLORS["bg_light"])
        split.pack(fill="both", expand=True)
        split.columnconfigure(0, weight=1)
        split.columnconfigure(1, weight=3)

        # LEFT CARD
        left_card = tk.Frame(split, bg="white", padx=20, pady=30)
        left_card.grid(row=0, column=0, sticky="n", padx=(0, 20))
        
        self.avatar_canvas = tk.Canvas(left_card, width=120, height=120, bg="white", highlightthickness=0)
        self.avatar_canvas.pack()
        self.avatar_canvas.create_oval(10, 10, 110, 110, fill="#E0E0E0", outline="")
        self.avatar_canvas.create_text(60, 60, text="Photo", font=("Arial", 10, "bold"), fill="#777")

        tk.Button(left_card, text="📷 Change Photo", bg="white", fg="#1976D2", 
                  relief="flat", font=("Arial", 9, "bold"), cursor="hand2",
                  command=self.upload_photo).pack(pady=(10, 20))

        tk.Label(left_card, text="Juan Dela Cruz", font=("Arial", 14, "bold"), bg="white").pack()
        tk.Label(left_card, text="Student", font=("Arial", 10), bg="#E8F5E9", fg="#2E7D32", padx=10, pady=2).pack(pady=5)

        ttk.Separator(left_card, orient="horizontal").pack(fill="x", pady=20)

        tk.Button(left_card, text="Log Out", bg="#FFEBEE", fg="#D32F2F", 
                  relief="flat", font=("Arial", 10, "bold"), pady=8, cursor="hand2", width=20,
                  command=self.logout_action).pack(side="bottom")

        # RIGHT CARD
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
        self.create_field(right_card, "Full Name", "Juan Dela Cruz")
        self.create_field(right_card, "Student / Staff ID", "21-01234")
        self.create_field(right_card, "Email Address", "juan@batstate-u.edu.ph")
        self.create_field(right_card, "Department", "CICS - Batangas")
        self.create_field(right_card, "Contact Number", "0912-345-6789")

        self.save_btn = tk.Button(right_card, text="Save Changes", bg=COLORS["primary_green"], fg="white",
                                  relief="flat", font=("Arial", 10, "bold"), padx=20, pady=10, cursor="hand2",
                                  command=self.save_profile)

    def create_field(self, parent, label, value):
        container = tk.Frame(parent, bg="white")
        container.pack(fill="x", pady=10)
        tk.Label(container, text=label, bg="white", font=("Arial", 9, "bold"), fg="#555").pack(anchor="w")
        entry = tk.Entry(container, relief="solid", bd=1, font=("Arial", 11), disabledbackground="#FAFAFA", disabledforeground="#333")
        entry.insert(0, value)
        entry.config(state="disabled")
        entry.pack(fill="x", ipady=8, pady=(5, 0))
        self.entries[label] = entry

    def toggle_edit(self):
        if not self.is_editing:
            self.is_editing = True
            self.edit_btn.config(text="Cancel", bg="#FFEBEE", fg="#D32F2F")
            self.save_btn.pack(pady=20, anchor="e")
            for e in self.entries.values(): e.config(state="normal", bg="white")
        else:
            self.is_editing = False
            self.edit_btn.config(text="✎ Edit Profile", bg="#E3F2FD", fg="#1976D2")
            self.save_btn.pack_forget()
            for e in self.entries.values(): e.config(state="disabled", bg="#FAFAFA")

    def save_profile(self):
        messagebox.showinfo("Success", "Profile updated successfully!")
        self.toggle_edit()

    def upload_photo(self):
        filedialog.askopenfilename(filetypes=[("Images", "*.png;*.jpg")])

    def logout_action(self):
        if messagebox.askyesno("Log Out", "Are you sure you want to log out?"):
            self.controller.show_login_page()