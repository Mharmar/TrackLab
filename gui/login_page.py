import tkinter as tk
from tkinter import ttk, messagebox
from utils.colors import COLORS
from database.users_db import login_user, register_user
from utils.session import Session 

class LoginPage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg=COLORS["bg_light"])
        self.controller = controller
        self.selected_role = "Student"
        self.is_registering = False 
        self.is_admin_login = False # New flag for Admin Login mode
        self.build_ui()

    def build_ui(self):
        self.place_card_center()

    def place_card_center(self):
        self.container = tk.Frame(self, bg=COLORS["bg_light"])
        self.container.place(relx=0.5, rely=0.5, anchor="center")

        tk.Label(self.container, text="TRACKLAB", font=("Arial", 32, "bold"), 
                 fg=COLORS["primary_green"], bg=COLORS["bg_light"]).pack(pady=(0, 10))
        
        self.subtitle = tk.Label(self.container, text="Sign in to your account", font=("Arial", 12), 
                 fg="#777", bg=COLORS["bg_light"])
        self.subtitle.pack(pady=(0, 30))

        self.card = tk.Frame(self.container, bg="white", padx=40, pady=40)
        self.card.pack()
        self.card.config(highlightbackground="#D1D5DB", highlightthickness=1)

        # --- ROLE SELECTION (Visible ONLY for Register) ---
        self.role_frame = tk.Frame(self.card, bg="white")
        
        tk.Label(self.role_frame, text="I am a...", font=("Arial", 10, "bold"), bg="white", fg="#555").pack(anchor="w", pady=(0, 10))
        
        btn_row = tk.Frame(self.role_frame, bg="white")
        btn_row.pack(fill="x", pady=(0, 10))

        # Role Buttons (NO ADMIN HERE)
        self.btn_student = tk.Button(btn_row, text="Student", relief="flat", font=("Arial", 9), width=10,
                                     command=lambda: self.set_role("Student"))
        self.btn_student.pack(side="left", padx=(0, 5))

        self.btn_staff = tk.Button(btn_row, text="Staff", relief="flat", font=("Arial", 9), width=10,
                                   command=lambda: self.set_role("Staff"))
        self.btn_staff.pack(side="left", padx=5)

        self.update_role_buttons()

        # --- INPUTS ---
        tk.Label(self.card, text="Username", font=("Arial", 10, "bold"), bg="white", fg="#555").pack(anchor="w")
        self.user_entry = tk.Entry(self.card, relief="solid", bd=1, font=("Arial", 11), bg="#FAFAFA")
        self.user_entry.pack(fill="x", ipady=8, pady=(5, 15))

        tk.Label(self.card, text="Password", font=("Arial", 10, "bold"), bg="white", fg="#555").pack(anchor="w")
        self.pass_entry = tk.Entry(self.card, relief="solid", bd=1, font=("Arial", 11), bg="#FAFAFA", show="•")
        self.pass_entry.pack(fill="x", ipady=8, pady=(5, 5))

        # Dynamic Area
        self.dynamic_frame = tk.Frame(self.card, bg="white")
        self.dynamic_frame.pack(fill="x")

        # Hidden widgets
        self.confirm_lbl = tk.Label(self.dynamic_frame, text="Confirm Password", font=("Arial", 10, "bold"), bg="white", fg="#555")
        self.confirm_entry = tk.Entry(self.dynamic_frame, relief="solid", bd=1, font=("Arial", 11), bg="#FAFAFA", show="•")
        
        self.forgot_btn = tk.Label(self.dynamic_frame, text="Forgot Password?", font=("Arial", 9), bg="white", fg=COLORS["primary_green"], cursor="hand2")
        self.forgot_btn.bind("<Button-1>", lambda e: messagebox.showinfo("Info", "Contact Admin to reset password."))

        self.action_btn = tk.Button(self.card, text="Login", bg=COLORS["primary_green"], fg="white", 
                              font=("Arial", 12, "bold"), relief="flat", pady=10, cursor="hand2",
                              command=self.handle_action)
        self.action_btn.pack(fill="x", pady=(20, 0))

        # Bottom Links
        self.toggle_lbl = tk.Label(self.card, text="Don't have an account? Register", font=("Arial", 9), bg="white", fg="#1976D2", cursor="hand2")
        self.toggle_lbl.pack(pady=(15, 5))
        self.toggle_lbl.bind("<Button-1>", lambda e: self.toggle_mode())

        # Admin Login Link (Separate)
        self.admin_lbl = tk.Label(self.card, text="Admin Login", font=("Arial", 9, "bold"), bg="white", fg="#555", cursor="hand2")
        self.admin_lbl.pack(pady=(5, 0))
        self.admin_lbl.bind("<Button-1>", lambda e: self.toggle_admin_mode())

        self.refresh_dynamic_area()

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
        self.is_registering = not self.is_registering
        self.is_admin_login = False # Reset admin mode if switching to reg
        self.refresh_dynamic_area()

    def toggle_admin_mode(self):
        # Toggle between Admin Login and Regular Login
        self.is_admin_login = not self.is_admin_login
        self.is_registering = False # Ensure not in register mode
        self.refresh_dynamic_area()

    def refresh_dynamic_area(self):
        # Clear dynamic widgets
        for widget in self.dynamic_frame.winfo_children():
            widget.pack_forget()
        
        self.role_frame.pack_forget() 

        # 1. ADMIN LOGIN MODE
        if self.is_admin_login:
            self.subtitle.config(text="Administrator Access", fg="#D32F2F")
            self.action_btn.config(text="Login as Admin", bg="#D32F2F")
            self.toggle_lbl.pack_forget() # Hide Register link in Admin mode
            self.admin_lbl.config(text="← Back to User Login", fg="#1976D2")
            self.forgot_btn.pack_forget()

        # 2. REGISTRATION MODE
        elif self.is_registering:
            self.subtitle.config(text="Create a new account", fg="#777")
            self.action_btn.config(text="Register", bg=COLORS["primary_green"])
            self.toggle_lbl.config(text="Already have an account? Login")
            self.toggle_lbl.pack(pady=(15, 5))
            self.admin_lbl.pack_forget() # Hide Admin link during Register
            
            # Show Role Selection
            self.role_frame.pack(before=self.dynamic_frame, fill="x", pady=(0, 10))
            self.role_frame.lift() 

            self.confirm_lbl.pack(anchor="w", pady=(10, 0))
            self.confirm_entry.pack(fill="x", ipady=8, pady=(5, 5))

        # 3. NORMAL LOGIN MODE
        else:
            self.subtitle.config(text="Sign in to your account", fg="#777")
            self.action_btn.config(text="Login", bg=COLORS["primary_green"])
            self.toggle_lbl.config(text="Don't have an account? Register")
            self.toggle_lbl.pack(pady=(15, 5))
            self.admin_lbl.config(text="Admin Login", fg="#555")
            self.admin_lbl.pack(pady=(5, 0))
            self.forgot_btn.pack(anchor="e", pady=(5, 10))

    def handle_action(self):
        username = self.user_entry.get().strip()
        password = self.pass_entry.get().strip()

        if not username or not password:
            messagebox.showerror("Error", "Please fill in all fields.")
            return

        if self.is_registering:
            confirm = self.confirm_entry.get().strip()
            if password != confirm:
                messagebox.showerror("Error", "Passwords do not match.")
                return
            
            # Use selected role (Student/Staff only)
            success, msg = register_user(username, password, self.selected_role)
            if success:
                messagebox.showinfo("Success", msg)
                self.toggle_mode() 
                self.user_entry.delete(0, tk.END)
                self.pass_entry.delete(0, tk.END)
                self.confirm_entry.delete(0, tk.END)
            else:
                messagebox.showerror("Registration Failed", msg)

        else:
            # Login Logic
            user = login_user(username, password)
            if user:
                role = user.get('role', 'Student')
                
                # STRICT ADMIN CHECK
                if self.is_admin_login:
                    if role != "Admin":
                        messagebox.showerror("Access Denied", "This account is not an Administrator.")
                        return
                else:
                    # Prevent Admin from logging in via standard portal? 
                    # Optional: Typically Admins can use standard, but better to separate.
                    pass 

                Session.set_user(user)
                print(f"✅ Login Successful: {user['username']} ({role})")
                self.controller.show_dashboard()
            else:
                messagebox.showerror("Login Failed", "Invalid Username or Password.")