# gui/borrow_page.py
import tkinter as tk
from tkinter import ttk, messagebox
import random
from datetime import datetime
from utils.colors import COLORS
from database.mock_db import INVENTORY_DB, get_item_details

class BorrowPage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg=COLORS["bg_light"])
        self.controller = controller
        self.build_ui()

    # =============================================================
    # UI LAYOUT FIXED: Borrow Form LEFT | Item Picker RIGHT PANEL
    # =============================================================
    def build_ui(self):
        # --- NAV BAR ---
        nav_bar = tk.Frame(self, bg="white", height=60, padx=20)
        nav_bar.pack(side="top", fill="x")

        tk.Label(nav_bar, text="TRACKLAB", font=("Arial", 16, "bold"),
                 fg=COLORS["primary_green"], bg="white").pack(side="left", pady=15)

        nav_items = ["Dashboard", "Equipment", "Borrow", "Reports"]
        for item in nav_items:
            if item == "Dashboard":
                cmd = self.controller.show_dashboard
            elif item == "Borrow":
                cmd = None
            elif item == "Reports":
                cmd = self.controller.show_reports  # <--- FIX THIS LINE
            else:
                cmd = lambda x=item: print(f"Clicked {x}")

            color = COLORS["primary_green"] if item == "Borrow" else "#555"
            font_style = ("Arial", 10, "bold") if item == "Borrow" else ("Arial", 10)

            tk.Button(nav_bar, text=item, bg="white", fg=color,
                      relief="flat", font=font_style, command=cmd
            ).pack(side="right", padx=10)

        # --------------------- MAIN CONTENT ---------------------
        main = tk.Frame(self, bg=COLORS["bg_light"])
        main.pack(fill="both", expand=True, padx=40, pady=20)

        tk.Label(main, text="Borrow Equipment", font=("Arial", 22, "bold"),
                 bg=COLORS["bg_light"]).pack(anchor="w", pady=(0, 20))

        # ---- SPLIT INTO LEFT (FORM) + RIGHT (ITEM PICK PANEL) ----
        split = tk.Frame(main, bg=COLORS["bg_light"])
        split.pack(fill="both", expand=True)
        split.columnconfigure(0, weight=2)
        split.columnconfigure(1, weight=2)

        # ============================================================
        # LEFT: BORROWER FORM
        # ============================================================
        form = tk.Frame(split, bg="white", padx=30, pady=30)
        form.grid(row=0, column=0, sticky="nsew", padx=(0, 20))
        form.config(highlightbackground="#E0E0E0", highlightthickness=1)

        tk.Label(form, text="Borrower Information", font=("Arial", 14, "bold"),
                 bg="white", fg=COLORS["primary_green"]).pack(anchor="w", pady=(0, 15))

        self.create_entry(form, "Full Name")
        self.create_entry(form, "Contact Number")
        self.create_entry(form, "Department / Section")

        auto_id = f"STU-{random.randint(10000,99999)}"
        self.create_entry(form, "Student ID (Auto)", val=auto_id, readonly=True)

        tk.Button(form, text="Confirm Borrow", bg=COLORS["primary_green"], fg="white",
                  font=("Arial", 11, "bold"), relief="flat", padx=20, pady=10,
                  command=self.confirm).pack(side="bottom", pady=20)

        # ============================================================
        # RIGHT: ITEM PICK PANEL (NEW STRUCTURE)
        # ============================================================
        picker = tk.Frame(split, bg="white", padx=25, pady=25)
        picker.grid(row=0, column=1, sticky="nsew")
        picker.config(highlightbackground="#E0E0E0", highlightthickness=1)

        tk.Label(picker, text="Select Equipment", font=("Arial", 14, "bold"),
                 bg="white", fg=COLORS["primary_green"]).pack(anchor="w")

        tk.Label(picker, text="Choose Item", bg="white",
                 font=("Arial", 9, "bold"), fg="#555").pack(anchor="w", pady=(15, 3))

        item_list = [name for name, d in INVENTORY_DB.items() if d["status"] == "Available"]
        self.item_cb = ttk.Combobox(picker, values=item_list, state="readonly", font=("Arial", 10))
        self.item_cb.pack(fill="x", pady=(0, 15), ipady=4)
        self.item_cb.bind("<<ComboboxSelected>>", self.on_item_select)

        # ITEM INFORMATION PANEL
        info = tk.Frame(picker, bg="white")
        info.pack(fill="x", pady=(10, 10))

        self.eq_id = self.labeled_value(info, "Equipment ID")
        self.eq_qty = self.labeled_value(info, "Available Qty")

        # QUANTITY PICKER
        tk.Label(picker, text="Quantity to Borrow", bg="white",
                 font=("Arial", 9, "bold"), fg="#555").pack(anchor="w")

        self.qty_spin = ttk.Spinbox(picker, from_=1, to=1, width=10, font=("Arial", 10))
        self.qty_spin.pack(anchor="w", pady=(5, 10))

    # ============================================================
    # HELPERS
    # ============================================================
    def labeled_value(self, parent, label):
        frame = tk.Frame(parent, bg="white")
        frame.pack(fill="x", pady=(3, 3))
        tk.Label(frame, text=f"{label}:", bg="white", fg="#666",
                 font=("Arial", 9, "bold")).pack(anchor="w")
        value = tk.Label(frame, text="-", bg="white", fg="#222",
                         font=("Arial", 11))
        value.pack(anchor="w")
        return value

    def create_entry(self, parent, label, val="", readonly=False):
        frame = tk.Frame(parent, bg="white")
        frame.pack(fill="x", pady=10)

        tk.Label(frame, text=label, bg="white", font=("Arial", 9, "bold"),
                 fg="#555").pack(anchor="w")

        entry = tk.Entry(frame, font=("Arial", 10), relief="solid", bd=1,
                         bg="#FAFAFA" if readonly else "white")
        entry.pack(fill="x", ipady=5)

        if val:
            entry.insert(0, val)
        if readonly:
            entry.config(state="readonly")
        return entry

    # ============================================================
    # ITEM SELECT LOGIC
    # ============================================================
    def on_item_select(self, event):
        item = self.item_cb.get()
        details = get_item_details(item)

        qty = details["qty"]

        self.eq_id.config(text=details["id"])
        self.eq_qty.config(text=str(qty))

        # Update Spinbox max
        self.qty_spin.config(to=qty)
        self.qty_spin.set(1)

    # ============================================================
    # CONFIRM
    # ============================================================
    def confirm(self):
        messagebox.showinfo("Success", "Borrowing Confirmed!")
        self.controller.show_dashboard()
