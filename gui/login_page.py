# gui/login_page.py
import tkinter as tk
from tkinter import ttk, messagebox
from utils.colors import COLORS
from database.users_db import login_user, register_user

class LoginPage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg=COLORS["bg_light"])
        self.controller = controller
        self.selected_role = "Student"
        self.is_registering = False # Track state
        self.build_ui()

    def build_ui(self):
        self.place_card_center()

    def place_card_center(self):
        # Main Container
        self.container = tk.Frame(self, bg=COLORS["bg_light"])
        self.container.place(relx=0.5, rely=0.5, anchor="center")

        # Header
        tk.Label(self.container, text="TRACKLAB", font=("Arial", 32, "bold"), 
                 fg=COLORS["primary_green"], bg=COLORS["bg_light"]).pack(pady=(0, 10))
        
        self.subtitle = tk.Label(self.container, text="Sign in to your account", font=("Arial", 12), 
                 fg="#777", bg=COLORS["bg_light"])
        self.subtitle.pack(pady=(0, 30))

        # Card
        self.card = tk.Frame(self.container, bg="white", padx=40, pady=40)
        self.card.pack()
        self.card.config(highlightbackground="#D1D5DB", highlightthickness=1)

        # 1. Role Selection
        tk.Label(self.card, text="I am a...", font=("Arial", 10, "bold"), bg="white", fg="#555").pack(anchor="w", pady=(0, 10))
        role_frame = tk.Frame(self.card, bg="white")
        role_frame.pack(fill="x", pady=(0, 20))

        self.btn_student = tk.Button(role_frame, text="Student", relief="flat", font=("Arial", 10),
                                     command=lambda: self.set_role("Student"))
        self.btn_student.pack(side="left", fill="x", expand=True, padx=(0, 5))

        self.btn_staff = tk.Button(role_frame, text="Staff", relief="flat", font=("Arial", 10),
                                   command=lambda: self.set_role("Staff"))
        self.btn_staff.pack(side="left", fill="x", expand=True, padx=(5, 0))
        self.update_role_buttons()

        # 2. Standard Inputs (Always Visible)
        tk.Label(self.card, text="Username", font=("Arial", 10, "bold"), bg="white", fg="#555").pack(anchor="w")
        self.user_entry = tk.Entry(self.card, relief="solid", bd=1, font=("Arial", 11), bg="#FAFAFA")
        self.user_entry.pack(fill="x", ipady=8, pady=(5, 15))

        tk.Label(self.card, text="Password", font=("Arial", 10, "bold"), bg="white", fg="#555").pack(anchor="w")
        self.pass_entry = tk.Entry(self.card, relief="solid", bd=1, font=("Arial", 11), bg="#FAFAFA", show="•")
        self.pass_entry.pack(fill="x", ipady=8, pady=(5, 5))

        # 3. Dynamic Area (Changes based on Login/Register)
        self.dynamic_frame = tk.Frame(self.card, bg="white")
        self.dynamic_frame.pack(fill="x")

        # Create widgets for the dynamic area (but don't pack them yet)
        
        # -- For Register --
        self.confirm_lbl = tk.Label(self.dynamic_frame, text="Confirm Password", font=("Arial", 10, "bold"), bg="white", fg="#555")
        self.confirm_entry = tk.Entry(self.dynamic_frame, relief="solid", bd=1, font=("Arial", 11), bg="#FAFAFA", show="•")
        
        # -- For Login --
        self.forgot_btn = tk.Label(self.dynamic_frame, text="Forgot Password?", font=("Arial", 9), bg="white", fg=COLORS["primary_green"], cursor="hand2")
        self.forgot_btn.bind("<Button-1>", lambda e: messagebox.showinfo("Info", "Contact Admin to reset password."))

        # -- Footer Area --
        self.action_btn = tk.Button(self.card, text="Login", bg=COLORS["primary_green"], fg="white", 
                              font=("Arial", 12, "bold"), relief="flat", pady=10, cursor="hand2",
                              command=self.handle_action)
        self.action_btn.pack(fill="x", pady=(20, 0))

        self.toggle_lbl = tk.Label(self.card, text="Don't have an account? Register", font=("Arial", 9), bg="white", fg="#1976D2", cursor="hand2")
        self.toggle_lbl.pack(pady=(15, 0))
        self.toggle_lbl.bind("<Button-1>", lambda e: self.toggle_mode())

        # Initialize in Login Mode
        self.refresh_dynamic_area()

        # Footer
        tk.Label(self.container, text="© 2025 Batangas State University", font=("Arial", 9), 
                 fg="#999", bg=COLORS["bg_light"]).pack(pady=30)

    def set_role(self, role):
        self.selected_role = role
        self.update_role_buttons()

    def update_role_buttons(self):
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

    def toggle_mode(self):
        """Switches state and refreshes UI"""
        self.is_registering = not self.is_registering
        self.refresh_dynamic_area()

    def refresh_dynamic_area(self):
        """
        Clears the dynamic area and repacks widgets in the correct order
        to avoid TclErrors.
        """
        # 1. Unpack everything in dynamic frame
        for widget in self.dynamic_frame.winfo_children():
            widget.pack_forget()

        if self.is_registering:
            # === REGISTER MODE ===
            self.subtitle.config(text="Create a new account")
            self.action_btn.config(text="Register")
            self.toggle_lbl.config(text="Already have an account? Login")
            
            # Pack Confirm Password fields
            self.confirm_lbl.pack(anchor="w", pady=(10, 0))
            self.confirm_entry.pack(fill="x", ipady=8, pady=(5, 5))
            
        else:
            # === LOGIN MODE ===
            self.subtitle.config(text="Sign in to your account")
            self.action_btn.config(text="Login")
            self.toggle_lbl.config(text="Don't have an account? Register")
            
            # Pack Forgot Password
            self.forgot_btn.pack(anchor="e", pady=(5, 10))

    def handle_action(self):
        username = self.user_entry.get().strip()
        password = self.pass_entry.get().strip()

        if not username or not password:
            messagebox.showerror("Error", "Please fill in all fields.")
            return

        if self.is_registering:
            # --- REGISTER LOGIC ---
            confirm = self.confirm_entry.get().strip()
            
            if password != confirm:
                messagebox.showerror("Error", "Passwords do not match.")
                return
            
            # Call Database
            success, msg = register_user(username, password, self.selected_role)
            if success:
                messagebox.showinfo("Success", msg)
                self.toggle_mode() # Go back to login
                self.user_entry.delete(0, tk.END)
                self.pass_entry.delete(0, tk.END)
                self.confirm_entry.delete(0, tk.END)
            else:
                messagebox.showerror("Registration Failed", msg)

        else:
            # --- LOGIN LOGIC ---
            user = login_user(username, password)
            if user:
                # Optional: Check Role Match
                if user['role'].lower() != self.selected_role.lower():
                    confirm = messagebox.askyesno("Role Mismatch", f"This account is registered as {user['role']}. Continue anyway?")
                    if not confirm: return

                print(f"✅ Login Successful: {user['username']}")
                self.controller.show_dashboard()
            else:
                messagebox.showerror("Login Failed", "Invalid Username or Password.")