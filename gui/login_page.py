# gui/login_page.py
import tkinter as tk
from tkinter import ttk, messagebox
from utils.colors import COLORS

class LoginPage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg=COLORS["bg_light"])
        self.controller = controller
        self.selected_role = "Student" # Default
        self.build_ui()

    def build_ui(self):
        # Center the content
        self.place_card_center()

    def place_card_center(self):
        # Container to center everything
        container = tk.Frame(self, bg=COLORS["bg_light"])
        container.place(relx=0.5, rely=0.5, anchor="center")

        # --- HEADER ---
        tk.Label(container, text="TRACKLAB", font=("Arial", 32, "bold"), 
                 fg=COLORS["primary_green"], bg=COLORS["bg_light"]).pack(pady=(0, 10))
        
        tk.Label(container, text="Sign in to your account", font=("Arial", 12), 
                 fg="#777", bg=COLORS["bg_light"]).pack(pady=(0, 30))

        # --- LOGIN CARD ---
        card = tk.Frame(container, bg="white", padx=40, pady=40)
        card.pack()
        # Shadow border effect
        card.config(highlightbackground="#D1D5DB", highlightthickness=1)

        # 1. Role Selection (Custom Toggle Look)
        role_label = tk.Label(card, text="I am a...", font=("Arial", 10, "bold"), bg="white", fg="#555")
        role_label.pack(anchor="w", pady=(0, 10))

        role_frame = tk.Frame(card, bg="white")
        role_frame.pack(fill="x", pady=(0, 20))

        self.btn_student = tk.Button(role_frame, text="Student", relief="flat", font=("Arial", 10),
                                     command=lambda: self.set_role("Student"))
        self.btn_student.pack(side="left", fill="x", expand=True, padx=(0, 5))

        self.btn_staff = tk.Button(role_frame, text="Staff", relief="flat", font=("Arial", 10),
                                   command=lambda: self.set_role("Staff"))
        self.btn_staff.pack(side="left", fill="x", expand=True, padx=(5, 0))

        # Initialize buttons
        self.update_role_buttons()

        # 2. Username/Email
        tk.Label(card, text="Username / Email", font=("Arial", 10, "bold"), bg="white", fg="#555").pack(anchor="w")
        self.user_entry = tk.Entry(card, relief="solid", bd=1, font=("Arial", 11), bg="#FAFAFA")
        self.user_entry.pack(fill="x", ipady=8, pady=(5, 15))

        # 3. Password
        tk.Label(card, text="Password", font=("Arial", 10, "bold"), bg="white", fg="#555").pack(anchor="w")
        self.pass_entry = tk.Entry(card, relief="solid", bd=1, font=("Arial", 11), bg="#FAFAFA", show="•")
        self.pass_entry.pack(fill="x", ipady=8, pady=(5, 5))

        # 4. Forgot Password
        forgot_btn = tk.Label(card, text="Forgot Password?", font=("Arial", 9), bg="white", fg=COLORS["primary_green"], cursor="hand2")
        forgot_btn.pack(anchor="e", pady=(0, 20))
        forgot_btn.bind("<Button-1>", lambda e: messagebox.showinfo("Info", "Reset password feature coming soon."))

        # 5. Login Button
        login_btn = tk.Button(card, text="Login", bg=COLORS["primary_green"], fg="white", 
                              font=("Arial", 12, "bold"), relief="flat", pady=10, cursor="hand2",
                              command=self.handle_login)
        login_btn.pack(fill="x")

        # --- FOOTER ---
        tk.Label(container, text="© 2025 Batangas State University", font=("Arial", 9), 
                 fg="#999", bg=COLORS["bg_light"]).pack(pady=30)

    def set_role(self, role):
        self.selected_role = role
        self.update_role_buttons()

    def update_role_buttons(self):
        """Updates the visual style of role buttons based on selection"""
        active_bg = COLORS["primary_green"]
        active_fg = "white"
        inactive_bg = "#F3F4F6"
        inactive_fg = "#555"

        if self.selected_role == "Student":
            self.btn_student.config(bg=active_bg, fg=active_fg)
            self.btn_staff.config(bg=inactive_bg, fg=inactive_fg)
        else:
            self.btn_student.config(bg=inactive_bg, fg=inactive_fg)
            self.btn_staff.config(bg=active_bg, fg=active_fg)

    def handle_login(self):
        username = self.user_entry.get()
        password = self.pass_entry.get()

        # --- MOCK AUTHENTICATION ---
        if username == "" or password == "":
            messagebox.showerror("Login Failed", "Please enter username and password.")
        else:
            # Success: Navigate to Dashboard
            # In real app, check DB here
            print(f"Logging in as {self.selected_role}: {username}")
            self.controller.show_dashboard()