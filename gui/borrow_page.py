import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime, timedelta
import calendar
from utils.colors import COLORS
from utils.session import Session
from database.equipment_db import get_all_equipment
from database.borrower_db import get_or_create_borrower
from database.borrow_db import borrow_equipment
from utils.id_generator import generate_formatted_id

class CalendarPopup(tk.Toplevel):
    """A Custom, dependency-free Date Picker"""
    def __init__(self, parent, callback):
        super().__init__(parent)
        self.callback = callback
        self.title("Select Date")
        self.geometry("300x300")
        self.configure(bg="white")
        self.transient(parent)
        self.grab_set()
        
        self.current_date = datetime.now()
        self.year = self.current_date.year
        self.month = self.current_date.month
        
        self.build_ui()
        
    def build_ui(self):
        # Header
        header = tk.Frame(self, bg=COLORS["primary_green"])
        header.pack(fill="x")
        
        btn_prev = tk.Button(header, text="<", bg=COLORS["primary_green"], fg="white", 
                             relief="flat", command=self.prev_month)
        btn_prev.pack(side="left", padx=5, pady=5)
        
        self.lbl_month = tk.Label(header, text="", font=("Arial", 12, "bold"), 
                                  bg=COLORS["primary_green"], fg="white")
        self.lbl_month.pack(side="left", expand=True)
        
        btn_next = tk.Button(header, text=">", bg=COLORS["primary_green"], fg="white", 
                             relief="flat", command=self.next_month)
        btn_next.pack(side="right", padx=5, pady=5)
        
        # Calendar Grid
        self.grid_frame = tk.Frame(self, bg="white", padx=10, pady=10)
        self.grid_frame.pack(fill="both", expand=True)
        
        self.render_calendar()
        
    def render_calendar(self):
        # Clear old grid
        for widget in self.grid_frame.winfo_children(): widget.destroy()
        
        self.lbl_month.config(text=f"{calendar.month_name[self.month]} {self.year}")
        
        # Weekday Headers
        days = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"]
        for i, day in enumerate(days):
            tk.Label(self.grid_frame, text=day, bg="white", fg="#777", font=("Arial", 9, "bold")).grid(row=0, column=i, pady=(0,5))
            
        # Days
        month_cal = calendar.monthcalendar(self.year, self.month)
        now = datetime.now()
        today = now.day
        
        r = 1
        for week in month_cal:
            for c, day in enumerate(week):
                if day != 0:
                    # Logic: Disable past days
                    is_past = False
                    if self.year < now.year: is_past = True
                    elif self.year == now.year and self.month < now.month: is_past = True
                    elif self.year == now.year and self.month == now.month and day < today: is_past = True
                    
                    fg_color = "#333" if not is_past else "#CCC"
                    state = "normal" if not is_past else "disabled"
                    cursor = "hand2" if not is_past else ""
                    
                    btn = tk.Button(self.grid_frame, text=str(day), relief="flat", bg="white", fg=fg_color,
                                    state=state, cursor=cursor, width=4,
                                    command=lambda d=day: self.select_date(d))
                    btn.grid(row=r, column=c, padx=2, pady=2)
            r += 1

    def prev_month(self):
        # Allow viewing past months but buttons will be disabled by render logic
        self.month -= 1
        if self.month == 0:
            self.month = 12
            self.year -= 1
        self.render_calendar()

    def next_month(self):
        self.month += 1
        if self.month == 13:
            self.month = 1
            self.year += 1
        self.render_calendar()

    def select_date(self, day):
        # Format: YYYY-MM-DD
        selected = f"{self.year}-{str(self.month).zfill(2)}-{str(day).zfill(2)}"
        self.callback(selected)
        self.destroy()


class BorrowPage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg=COLORS["bg_light"])
        self.controller = controller
        self.user = Session.get_user()
        self.selected_item_data = None
        self.build_ui()

    def build_ui(self):
        # --- NAV BAR ---
        nav_bar = tk.Frame(self, bg="white", height=60, padx=20)
        nav_bar.pack(side="top", fill="x")

        tk.Label(nav_bar, text="TRACKLAB", font=("Arial", 16, "bold"), 
                 fg=COLORS["primary_green"], bg="white").pack(side="left", pady=15)

        nav_items = ["Dashboard", "Equipment", "Borrow", "Reports", "Profile"]
        for item in nav_items:
            cmd = None
            if item == "Dashboard": cmd = self.controller.show_dashboard
            elif item == "Equipment": cmd = self.controller.show_equipment_page
            elif item == "Reports": cmd = self.controller.show_reports
            elif item == "Profile": cmd = self.controller.show_profile_page
            
            color = COLORS["primary_green"] if item == "Borrow" else "#555"
            font = ("Arial", 10, "bold") if item == "Borrow" else ("Arial", 10)
            tk.Button(nav_bar, text=item, bg="white", fg=color, relief="flat", 
                      font=font, command=cmd).pack(side="right", padx=10)

        # --- CONTENT ---
        main = tk.Frame(self, bg=COLORS["bg_light"])
        main.pack(fill="both", expand=True, padx=40, pady=20)

        tk.Label(main, text="Borrow Equipment", font=("Arial", 22, "bold"), 
                 bg=COLORS["bg_light"]).pack(anchor="w", pady=(0, 20))

        split = tk.Frame(main, bg=COLORS["bg_light"])
        split.pack(fill="both", expand=True)
        split.columnconfigure(0, weight=3)
        split.columnconfigure(1, weight=2)

        # ==========================
        # LEFT: BORROW FORM
        # ==========================
        form_card = tk.Frame(split, bg="white", padx=30, pady=30)
        form_card.grid(row=0, column=0, sticky="nsew", padx=(0, 20))
        
        tk.Label(form_card, text="Borrower Information", font=("Arial", 14, "bold"), 
                 bg="white", fg=COLORS["primary_green"]).pack(anchor="w", pady=(0, 15))

        # Auto-fill
        uname = self.user.get('username', '')
        role = self.user.get('role', 'Student')
        u_id_fmt = generate_formatted_id(role, self.user.get('user_id', 0))
        dept = self.user.get('department', '')
        contact = self.user.get('contact', '')

        self.create_entry(form_card, "Full Name", val=uname, readonly=True)
        self.stu_id_ent = self.create_entry(form_card, "Student / Staff ID (Auto)", val=u_id_fmt, readonly=True)
        self.dept_ent = self.create_entry(form_card, "Department / Section", val=dept, readonly=False)
        self.contact_ent = self.create_entry(form_card, "Contact Number", val=contact, readonly=False)

        # --- EQUIPMENT SECTION ---
        tk.Label(form_card, text="Equipment Details", font=("Arial", 14, "bold"), 
                 bg="white", fg=COLORS["primary_green"]).pack(anchor="w", pady=(20, 15))

        tk.Label(form_card, text="Select Item", bg="white", font=("Arial", 9, "bold"), fg="#555").pack(anchor="w")
        self.inventory_map = {}
        try:
            all_items = get_all_equipment()
            item_names = []
            for i in all_items:
                if i['quantity'] > 0 and i['condition'] != 'Broken':
                    self.inventory_map[i['name']] = i
                    item_names.append(i['name'])
        except: item_names = []

        self.item_cb = ttk.Combobox(form_card, values=item_names, state="readonly", font=("Arial", 10))
        self.item_cb.pack(fill="x", pady=(5, 10), ipady=4)
        self.item_cb.bind("<<ComboboxSelected>>", self.on_item_select)

        # ID Row
        self.eq_id_entry = self.create_entry(form_card, "Equipment ID (Auto)", readonly=True)

        # --- TIME LIMIT SECTION (NEW) ---
        tk.Label(form_card, text="Expected Return Time", bg="white", font=("Arial", 9, "bold"), fg="#555").pack(anchor="w", pady=(10, 0))
        
        time_frame = tk.Frame(form_card, bg="white")
        time_frame.pack(fill="x", pady=5)
        
        # 1. Date Picker (Readonly Entry + Button)
        self.date_var = tk.StringVar()
        self.date_var.set(datetime.now().strftime("%Y-%m-%d")) # Default Today
        
        date_ent = tk.Entry(time_frame, textvariable=self.date_var, width=15, state="readonly", 
                            font=("Arial", 10), relief="solid", bd=1)
        date_ent.pack(side="left", ipady=4)
        
        tk.Button(time_frame, text="📅", width=3, bg="#E0E0E0", relief="flat",
                  command=self.open_calendar).pack(side="left", padx=(2, 10))
        
        # 2. Time Picker
        tk.Label(time_frame, text="at", bg="white").pack(side="left", padx=5)
        
        self.hour_spin = ttk.Spinbox(time_frame, from_=1, to=12, width=3, font=("Arial", 10))
        self.hour_spin.set("5")
        self.hour_spin.pack(side="left")
        
        tk.Label(time_frame, text=":", bg="white").pack(side="left")
        
        self.min_spin = ttk.Spinbox(time_frame, from_=0, to=59, width=3, format="%02.0f", font=("Arial", 10))
        self.min_spin.set("00")
        self.min_spin.pack(side="left")
        
        self.ampm_cb = ttk.Combobox(time_frame, values=["AM", "PM"], width=3, state="readonly", font=("Arial", 10))
        self.ampm_cb.set("PM")
        self.ampm_cb.pack(side="left", padx=5)

        # Quantity
        tk.Label(form_card, text="Quantity", bg="white", font=("Arial", 9, "bold"), fg="#555").pack(anchor="w", pady=(10, 0))
        qty_frame = tk.Frame(form_card, bg="white")
        qty_frame.pack(fill="x", pady=5)
        
        self.qty_spin = ttk.Spinbox(qty_frame, from_=1, to=1, width=10, font=("Arial", 10))
        self.qty_spin.pack(side="left")
        self.max_lbl = tk.Label(qty_frame, text="(Max: -)", bg="white", fg="#999")
        self.max_lbl.pack(side="left", padx=10)

        tk.Button(form_card, text="Confirm Borrow", bg=COLORS["primary_green"], fg="white", 
                  font=("Arial", 11, "bold"), relief="flat", padx=20, pady=10,
                  command=self.confirm).pack(side="bottom", pady=20, anchor="e")

        # ==========================
        # RIGHT: LIST (Accordion)
        # ==========================
        list_card = tk.Frame(split, bg="white")
        list_card.grid(row=0, column=1, sticky="nsew", padx=(0, 0))
        
        canvas = tk.Canvas(list_card, bg="white", highlightthickness=0)
        sb = ttk.Scrollbar(list_card, orient="vertical", command=canvas.yview)
        self.scroll_content = tk.Frame(canvas, bg="white", padx=20, pady=20)
        self.scroll_content.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=self.scroll_content, anchor="nw", width=400) 
        canvas.configure(yscrollcommand=sb.set)
        canvas.pack(side="left", fill="both", expand=True)
        sb.pack(side="right", fill="y")

        tk.Label(self.scroll_content, text="Available Items", font=("Arial", 12, "bold"), 
                 bg="white", fg="#333").pack(anchor="w", pady=(0, 15))

        cat_map = {}
        for name, data in self.inventory_map.items():
            c = data['category']
            if c not in cat_map: cat_map[c] = []
            cat_map[c].append(data)

        for cat, items in cat_map.items():
            self.create_accordion(self.scroll_content, cat, items)

    def open_calendar(self):
        CalendarPopup(self.winfo_toplevel(), lambda date: self.date_var.set(date))

    def create_entry(self, parent, label, val="", readonly=False, side=None):
        container = tk.Frame(parent, bg="white")
        container.pack(fill="x", pady=(0, 10))
        tk.Label(container, text=label, bg="white", font=("Arial", 9, "bold"), fg="#555").pack(anchor="w")
        e = tk.Entry(container, relief="solid", bd=1, font=("Arial", 10), bg="#FAFAFA" if readonly else "white")
        e.pack(fill="x", pady=(5, 0), ipady=5)
        if val: e.insert(0, val)
        if readonly: e.config(state="readonly")
        return e

    def create_accordion(self, parent, title, items):
        wrapper = tk.Frame(parent, bg="white", pady=2)
        wrapper.pack(fill="x")
        content = tk.Frame(wrapper, bg="#F9F9F9", padx=10)
        
        def toggle():
            if content.winfo_ismapped():
                content.pack_forget()
                btn.config(text=f"▶ {title}")
            else:
                content.pack(fill="x")
                btn.config(text=f"▼ {title}")

        btn = tk.Button(wrapper, text=f"▶ {title}", bg="#F0F0F0", relief="flat", anchor="w", command=toggle, font=("Arial", 10, "bold"))
        btn.pack(fill="x", ipady=5)

        for i in items:
            row = tk.Frame(content, bg="#F9F9F9", pady=2)
            row.pack(fill="x")
            tk.Label(row, text=i['name'], bg="#F9F9F9", width=20, anchor="w").pack(side="left")
            tk.Label(row, text=f"Qty: {i['quantity']}", bg="#F9F9F9", fg=COLORS["primary_green"], font=("Arial", 9, "bold")).pack(side="right")

    def on_item_select(self, event):
        name = self.item_cb.get()
        if name in self.inventory_map:
            self.selected_item_data = self.inventory_map[name]
            self.eq_id_entry.config(state="normal")
            self.eq_id_entry.delete(0, tk.END)
            self.eq_id_entry.insert(0, self.selected_item_data['code'])
            self.eq_id_entry.config(state="readonly")
            max_q = self.selected_item_data['quantity']
            self.max_lbl.config(text=f"(Max: {max_q})")
            self.qty_spin.config(to=max_q)
            self.qty_spin.set(1)

    def confirm(self):
        if not self.selected_item_data:
            messagebox.showerror("Error", "Please select an item.")
            return

        # 1. VALIDATE TIME LIMIT
        try:
            date_str = self.date_var.get() # YYYY-MM-DD
            hour = int(self.hour_spin.get())
            minute = int(self.min_spin.get())
            ampm = self.ampm_cb.get()

            # Convert 12h to 24h
            if ampm == "PM" and hour != 12: hour += 12
            if ampm == "AM" and hour == 12: hour = 0
            
            return_datetime_str = f"{date_str} {hour:02}:{minute:02}:00"
            return_dt = datetime.strptime(return_datetime_str, "%Y-%m-%d %H:%M:%S")
            
            if return_dt <= datetime.now():
                messagebox.showerror("Error", "Return time must be in the future.")
                return

        except ValueError:
            messagebox.showerror("Error", "Invalid Date or Time.")
            return

        # 2. PROCEED
        try:
            qty = int(self.qty_spin.get())
            if qty > self.selected_item_data['quantity']:
                messagebox.showerror("Error", "Not enough stock.")
                return
            
            uname = self.user.get('username', 'Guest')
            contact = self.contact_ent.get()
            dept = self.dept_ent.get()
            stu_id = self.stu_id_ent.get() 

            b_id = get_or_create_borrower(stu_id, uname, contact, dept)
            
            # PASS THE RETURN DATE TO DB
            if borrow_equipment(self.selected_item_data['equipment_id'], b_id, datetime.now(), return_dt, "Standard Borrow"):
                messagebox.showinfo("Success", f"Successfully borrowed. Due: {return_dt.strftime('%b %d, %I:%M %p')}")
                self.controller.show_dashboard()
            else:
                messagebox.showerror("Error", "Transaction Failed.")

        except ValueError:
            messagebox.showerror("Error", "Invalid Quantity")