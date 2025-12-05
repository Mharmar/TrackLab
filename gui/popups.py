import tkinter as tk
from tkinter import ttk, messagebox
import random
from datetime import datetime, timedelta
import calendar
from utils.colors import COLORS
from database.equipment_db import add_equipment, update_equipment, get_all_equipment
from database.borrower_db import get_or_create_borrower
from database.borrow_db import borrow_equipment
from database.return_db import return_equipment
from utils.session import Session
from utils.id_generator import generate_formatted_id

# --- HELPER: Calendar Widget (Same as BorrowPage) ---
class CalendarPopup(tk.Toplevel):
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
        header = tk.Frame(self, bg=COLORS["primary_green"])
        header.pack(fill="x")
        
        tk.Button(header, text="<", bg=COLORS["primary_green"], fg="white", relief="flat", 
                  command=self.prev_month).pack(side="left", padx=5, pady=5)
        
        self.lbl_month = tk.Label(header, text="", font=("Arial", 12, "bold"), 
                                  bg=COLORS["primary_green"], fg="white")
        self.lbl_month.pack(side="left", expand=True)
        
        tk.Button(header, text=">", bg=COLORS["primary_green"], fg="white", relief="flat", 
                  command=self.next_month).pack(side="right", padx=5, pady=5)
        
        self.grid_frame = tk.Frame(self, bg="white", padx=10, pady=10)
        self.grid_frame.pack(fill="both", expand=True)
        self.render_calendar()
        
    def render_calendar(self):
        for widget in self.grid_frame.winfo_children(): widget.destroy()
        self.lbl_month.config(text=f"{calendar.month_name[self.month]} {self.year}")
        days = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"]
        for i, day in enumerate(days):
            tk.Label(self.grid_frame, text=day, bg="white", fg="#777", font=("Arial", 9, "bold")).grid(row=0, column=i)
            
        month_cal = calendar.monthcalendar(self.year, self.month)
        now = datetime.now()
        r = 1
        for week in month_cal:
            for c, day in enumerate(week):
                if day != 0:
                    is_past = (self.year < now.year) or (self.year == now.year and self.month < now.month) or \
                              (self.year == now.year and self.month == now.month and day < now.day)
                    
                    state = "disabled" if is_past else "normal"
                    fg = "#CCC" if is_past else "#333"
                    
                    btn = tk.Button(self.grid_frame, text=str(day), relief="flat", bg="white", fg=fg,
                                    state=state, width=4, command=lambda d=day: self.select_date(d))
                    btn.grid(row=r, column=c, padx=2, pady=2)
            r += 1

    def prev_month(self):
        self.month -= 1
        if self.month == 0: self.month, self.year = 12, self.year - 1
        self.render_calendar()

    def next_month(self):
        self.month += 1
        if self.month == 13: self.month, self.year = 1, self.year + 1
        self.render_calendar()

    def select_date(self, day):
        selected = f"{self.year}-{str(self.month).zfill(2)}-{str(day).zfill(2)}"
        self.callback(selected)
        self.destroy()

# 1. ADD ITEM POPUP
class AddItemPopup:
    def __init__(self, parent_root, callback=None):
        self.top = tk.Toplevel(parent_root)
        self.top.title("Add New Equipment")
        self.top.geometry("400x450")
        self.top.configure(bg="white")
        self.callback = callback
        self.top.transient(parent_root); self.top.grab_set(); self.top.focus_force()
        self.build_ui()

    def build_ui(self):
        tk.Label(self.top, text="Add New Equipment", font=("Arial", 16, "bold"), 
                 bg="white", fg=COLORS["primary_green"]).pack(pady=(20, 10))

        form = tk.Frame(self.top, bg="white", padx=30)
        form.pack(fill="both", expand=True)

        self.name_entry = self.create_label_entry(form, "Equipment Name*")
        
        auto_code = f"EQ-{random.randint(10000,99999)}"
        self.id_entry = self.create_label_entry(form, "Code (Auto)*", val=auto_code, readonly=True)

        tk.Label(form, text="Category*", bg="white", font=("Arial", 9, "bold"), fg="#555").pack(anchor="w", pady=(10,0))
        self.cat_cb = ttk.Combobox(form, values=["Glassware", "PPE", "Measurement", "Apparatus", "Tools", "Others"], state="readonly")
        self.cat_cb.pack(fill="x", pady=5, ipady=3)
        self.cat_cb.current(0)

        self.qty_entry = self.create_label_entry(form, "Quantity*")

        tk.Label(form, text="Condition*", bg="white", font=("Arial", 9, "bold"), fg="#555").pack(anchor="w", pady=(10,0))
        self.cond_cb = ttk.Combobox(form, values=["Good", "New", "Fair"], state="readonly")
        self.cond_cb.pack(fill="x", pady=5, ipady=3)
        self.cond_cb.current(0)

        btn_frame = tk.Frame(self.top, bg="white", pady=20)
        btn_frame.pack(fill="x", padx=30)
        
        tk.Button(btn_frame, text="Submit", bg=COLORS["primary_green"], fg="white", 
                  relief="flat", pady=8, width=12, cursor="hand2",
                  command=self.save_item).pack(side="right")
        
        tk.Button(btn_frame, text="Cancel", bg="#F0F0F0", fg="#333", 
                  relief="flat", pady=8, width=10, cursor="hand2",
                  command=self.top.destroy).pack(side="right", padx=10)

    def create_label_entry(self, parent, label, val="", readonly=False):
        tk.Label(parent, text=label, bg="white", font=("Arial", 9, "bold"), fg="#555").pack(anchor="w", pady=(10,0))
        e = tk.Entry(parent, relief="solid", bd=1)
        e.pack(fill="x", pady=5, ipady=4)
        if val: 
            e.insert(0, val)
            if readonly: e.config(state="readonly")
        return e

    def save_item(self):
        name = self.name_entry.get()
        code = self.id_entry.get()
        cat = self.cat_cb.get()
        qty = self.qty_entry.get()
        cond = self.cond_cb.get()

        if not name or not qty:
            messagebox.showerror("Error", "Missing required fields.")
            return

        if add_equipment(name, code, cat, int(qty), cond):
            messagebox.showinfo("Success", "Item Added!")
            if self.callback: self.callback()
            self.top.destroy()
        else:
            messagebox.showerror("Error", "Database Error")

# 2. EDIT ITEM POPUP
class EditItemPopup:
    def __init__(self, parent_root, item_data, callback=None):
        self.top = tk.Toplevel(parent_root)
        self.top.title("Edit Equipment")
        self.top.geometry("400x500")
        self.top.configure(bg="white")
        self.item = item_data
        self.callback = callback
        self.top.transient(parent_root); self.top.grab_set(); self.top.focus_force()
        self.build_ui()

    def build_ui(self):
        tk.Label(self.top, text="Edit Equipment", font=("Arial", 16, "bold"), 
                 bg="white", fg="#1976D2").pack(pady=(20, 10))

        form = tk.Frame(self.top, bg="white", padx=30)
        form.pack(fill="both", expand=True)

        self.create_label_entry(form, "ID (Locked)", val=self.item['code'], readonly=True)
        self.create_label_entry(form, "Name (Locked)", val=self.item['name'], readonly=True)

        tk.Label(form, text="Category", bg="white", font=("Arial", 9, "bold"), fg="#555").pack(anchor="w", pady=(10, 0))
        self.cat_cb = ttk.Combobox(form, values=["Glassware", "PPE", "Measurement", "Apparatus", "Tools", "Others"], state="readonly")
        self.cat_cb.set(self.item['category'])
        self.cat_cb.pack(fill="x", pady=5, ipady=3)

        self.qty_ent = self.create_label_entry(form, "Quantity", val=str(self.item['qty']))

        tk.Label(form, text="Condition", bg="white", font=("Arial", 9, "bold"), fg="#555").pack(anchor="w", pady=(10, 0))
        self.cond_cb = ttk.Combobox(form, values=["Good", "Fair", "Minor Damage", "Broken", "Out of Stock"], state="readonly")
        self.cond_cb.set(self.item['status'])
        self.cond_cb.pack(fill="x", pady=5, ipady=3)

        btn_frame = tk.Frame(self.top, bg="white", pady=20)
        btn_frame.pack(fill="x", padx=30)
        
        tk.Button(btn_frame, text="Save Changes", bg="#1976D2", fg="white", 
                  relief="flat", pady=8, width=15, cursor="hand2",
                  command=self.save).pack(side="right")
        tk.Button(btn_frame, text="Cancel", bg="#F0F0F0", fg="#333", 
                  relief="flat", pady=8, width=10, cursor="hand2",
                  command=self.top.destroy).pack(side="right", padx=10)

    def create_label_entry(self, parent, label, val="", readonly=False):
        tk.Label(parent, text=label, bg="white", font=("Arial", 9, "bold"), fg="#555").pack(anchor="w", pady=(10, 0))
        e = tk.Entry(parent, relief="solid", bd=1)
        if readonly: e.config(state="normal")
        e.insert(0, val)
        if readonly: e.config(state="readonly")
        e.pack(fill="x", pady=5, ipady=4)
        return e

    def save(self):
        cat = self.cat_cb.get()
        qty = self.qty_ent.get()
        cond = self.cond_cb.get()
        if update_equipment(self.item['db_id'], cat, int(qty), cond):
            messagebox.showinfo("Success", "Updated!")
            if self.callback: self.callback()
            self.top.destroy()
        else:
            messagebox.showerror("Error", "Failed to update.")

# 3. QUICK BORROW POPUP (UPDATED with TIME LIMIT)
class BorrowPopup:
    def __init__(self, parent_root, callback=None):
        self.top = tk.Toplevel(parent_root)
        self.top.title("Quick Borrow")
        self.top.geometry("450x750")  # Increased height for calendar inputs
        self.top.configure(bg="white")
        self.top.transient(parent_root); self.top.grab_set(); self.top.focus_force()
        
        self.callback = callback
        self.user = Session.get_user() 
        self.items_map = {} 
        self.build_ui()

    def build_ui(self):
        tk.Label(self.top, text="Quick Borrow", font=("Arial", 18, "bold"), bg="white", fg=COLORS["primary_green"]).pack(pady=(20,5))
        form = tk.Frame(self.top, bg="white", padx=30); form.pack(fill="both", expand=True)

        uname = self.user.get('username', '')
        role = self.user.get('role', 'Student')
        uid_fmt = generate_formatted_id(role, self.user.get('user_id', 0))
        contact = self.user.get('contact', '')
        dept = self.user.get('department', '')

        self.name_ent = self.create_label_entry(form, "Full Name", val=uname, readonly=True)
        self.contact_ent = self.create_label_entry(form, "Contact Number", val=contact)
        self.dept_ent = self.create_label_entry(form, "Department", val=dept)
        self.stu_id_ent = self.create_label_entry(form, "Student ID (Auto)", val=uid_fmt, readonly=True)

        tk.Label(form, text="Select Equipment", bg="white", font=("Arial", 9, "bold")).pack(anchor="w", pady=(10,0))
        try: 
            db_items = get_all_equipment()
            item_names = []
            for i in db_items:
                if i['quantity'] > 0:
                    self.items_map[i['name']] = i
                    item_names.append(i['name'])
        except: item_names = []
        
        self.item_cb = ttk.Combobox(form, values=item_names, state="readonly")
        self.item_cb.pack(fill="x", pady=5)
        self.item_cb.bind("<<ComboboxSelected>>", self.on_select)
        
        self.eq_id_entry = self.create_label_entry(form, "Equipment ID", readonly=True)
        
        # --- RETURN TIME SECTION ---
        tk.Label(form, text="Expected Return Time", bg="white", font=("Arial", 9, "bold")).pack(anchor="w", pady=(10, 0))
        time_frame = tk.Frame(form, bg="white")
        time_frame.pack(fill="x", pady=5)
        
        # Date
        self.date_var = tk.StringVar(value=datetime.now().strftime("%Y-%m-%d"))
        date_ent = tk.Entry(time_frame, textvariable=self.date_var, width=12, state="readonly", relief="solid", bd=1)
        date_ent.pack(side="left", ipady=4)
        tk.Button(time_frame, text="📅", width=3, bg="#E0E0E0", relief="flat", 
                  command=lambda: CalendarPopup(self.top, lambda d: self.date_var.set(d))).pack(side="left", padx=(2, 10))
        
        # Time
        tk.Label(time_frame, text="at", bg="white").pack(side="left", padx=5)
        self.hour_spin = ttk.Spinbox(time_frame, from_=1, to=12, width=3); self.hour_spin.set("5"); self.hour_spin.pack(side="left")
        tk.Label(time_frame, text=":", bg="white").pack(side="left")
        self.min_spin = ttk.Spinbox(time_frame, from_=0, to=59, width=3, format="%02.0f"); self.min_spin.set("00"); self.min_spin.pack(side="left")
        self.ampm_cb = ttk.Combobox(time_frame, values=["AM", "PM"], width=3, state="readonly"); self.ampm_cb.set("PM"); self.ampm_cb.pack(side="left", padx=5)

        tk.Label(form, text="Quantity", bg="white").pack(anchor="w", pady=(10, 0))
        self.qty_spin = tk.Spinbox(form, from_=1, to=1)
        self.qty_spin.pack(pady=5, anchor="w")
        self.max_lbl = tk.Label(form, text="(Max: -)", bg="white", fg="#999")
        self.max_lbl.pack(anchor="w")

        tk.Button(form, text="Confirm", bg=COLORS["primary_green"], fg="white", command=self.confirm).pack(pady=20)

    def create_label_entry(self, parent, label, val="", readonly=False):
        tk.Label(parent, text=label, bg="white", font=("Arial", 9, "bold")).pack(anchor="w", pady=(5,0))
        e = tk.Entry(parent, relief="solid", bd=1)
        if readonly: e.config(state="normal")
        if val: e.insert(0, val)
        if readonly: e.config(state="readonly")
        e.pack(fill="x", pady=5); return e

    def on_select(self, event):
        name = self.item_cb.get()
        if name in self.items_map:
            d = self.items_map[name]
            self.eq_id_entry.config(state="normal"); self.eq_id_entry.delete(0, tk.END); self.eq_id_entry.insert(0, d['code']); self.eq_id_entry.config(state="readonly")
            max_q = d['quantity']
            self.max_lbl.config(text=f"(Max: {max_q})")
            self.qty_spin.config(to=max_q)

    def confirm(self):
        item = self.item_cb.get()
        if item in self.items_map:
            # 1. Validate Time
            try:
                d_str = self.date_var.get()
                h, m, ap = int(self.hour_spin.get()), int(self.min_spin.get()), self.ampm_cb.get()
                if ap == "PM" and h != 12: h += 12
                if ap == "AM" and h == 12: h = 0
                return_dt = datetime.strptime(f"{d_str} {h:02}:{m:02}:00", "%Y-%m-%d %H:%M:%S")
                if return_dt <= datetime.now():
                    messagebox.showerror("Error", "Return time must be in future.")
                    return
            except:
                messagebox.showerror("Error", "Invalid Date/Time")
                return

            # 2. Process
            try:
                qty = int(self.qty_spin.get())
                if qty > self.items_map[item]['quantity']:
                    messagebox.showerror("Error", "Not enough stock.")
                    return

                b_id = get_or_create_borrower(self.stu_id_ent.get(), self.name_ent.get(), self.contact_ent.get(), self.dept_ent.get())
                
                if borrow_equipment(self.items_map[item]['equipment_id'], b_id, datetime.now(), return_dt, "Quick Borrow"):
                    messagebox.showinfo("Success", "Borrowed!")
                    if self.callback: self.callback() 
                    self.top.destroy()
            except ValueError: messagebox.showerror("Error", "Invalid Quantity")

# 4. RETURN POPUP
class ReturnPopup:
    def __init__(self, parent_root, data, callback=None):
        self.top = tk.Toplevel(parent_root); self.top.title("Return"); self.top.geometry("400x550"); self.top.configure(bg="white")
        self.data = data
        self.callback = callback
        self.top.transient(parent_root); self.top.grab_set(); self.top.focus_force()
        self.build_ui()

    def build_ui(self):
        tk.Label(self.top, text="Return", font=("Arial", 16, "bold"), bg="white", fg=COLORS["primary_green"]).pack(pady=20)
        self.cond_var = tk.StringVar(value="Good")
        for m in ["Good", "Minor Damage", "Broken"]: tk.Radiobutton(self.top, text=m, variable=self.cond_var, value=m, bg="white").pack(anchor="w", padx=30)
        tk.Label(self.top, text="Remarks", bg="white").pack(anchor="w", padx=30)
        self.notes = tk.Text(self.top, height=4); self.notes.pack(padx=30, fill="x")
        tk.Button(self.top, text="Complete", bg=COLORS["primary_green"], fg="white", command=self.process).pack(pady=20)

    def process(self):
        if return_equipment(self.data['id'], self.cond_var.get(), self.notes.get("1.0", "end-1c").strip()):
            messagebox.showinfo("Success", "Returned!")
            if self.callback: self.callback()
            self.top.destroy()