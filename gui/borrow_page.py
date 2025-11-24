# gui/borrow_page.py
import tkinter as tk
from tkinter import ttk
from datetime import datetime
from utils.colors import COLORS
from utils.error_handler import ErrorHandler
from database.mock_db import INVENTORY_DB, get_item_details # Link to Mock DB

class BorrowPage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg=COLORS["bg_light"])
        self.controller = controller
        self.build_ui()

    def build_ui(self):
        # --- NAV BAR ---
        nav_bar = tk.Frame(self, bg="white", height=60, padx=20)
        nav_bar.pack(side="top", fill="x", pady=(0, 2))

        tk.Label(nav_bar, text="TRACKLAB", font=("Arial", 16, "bold"), 
                 fg=COLORS["primary_green"], bg="white").pack(side="left", pady=15)

        tk.Button(nav_bar, text="< Back to Dashboard", bg="white", fg=COLORS["text_light"], relief="flat",
                  command=self.controller.show_dashboard, font=("Arial", 10)).pack(side="right", pady=15)

        # --- MAIN SCROLL FRAME ---
        scroll_frame = tk.Frame(self, bg=COLORS["bg_light"])
        scroll_frame.pack(fill="both", expand=True, padx=40, pady=20)

        tk.Label(scroll_frame, text="Borrow Equipment", font=("Arial", 22, "bold"), 
                 bg=COLORS["bg_light"], fg=COLORS["text_dark"]).pack(anchor="w", pady=(0, 5))

        # --- THE CARD ---
        card = tk.Frame(scroll_frame, bg="white", padx=30, pady=30)
        card.pack(fill="x")
        card.columnconfigure(0, weight=1)
        card.columnconfigure(1, weight=1)

        # LEFT COL
        tk.Label(card, text="1. Borrower Details", font=("Arial", 12, "bold"), bg="white", fg=COLORS["primary_green"]).grid(row=0, column=0, sticky="w", pady=(0, 20))
        self.make_entry(card, "Full Name", 1, 0)
        self.make_entry(card, "Student / Staff ID", 2, 0)
        self.make_entry(card, "Department / Section", 3, 0)
        self.make_entry(card, "Contact Number", 4, 0)

        # RIGHT COL
        tk.Label(card, text="2. Equipment Details", font=("Arial", 12, "bold"), bg="white", fg=COLORS["primary_green"]).grid(row=0, column=1, sticky="w", pady=(0, 20), padx=20)

        # ITEM SELECTION
        tk.Label(card, text="Select Item", bg="white", font=("Arial", 9, "bold"), fg="#555").grid(row=1, column=1, sticky="w", padx=20)
        
        # Get item names from Mock DB
        item_list = list(INVENTORY_DB.keys())
        
        self.item_cb = ttk.Combobox(card, values=item_list, state="readonly", width=30, font=("Arial", 10))
        self.item_cb.grid(row=2, column=1, sticky="w", padx=20, pady=(0, 15))
        self.item_cb.bind("<<ComboboxSelected>>", self.on_item_select) # Bind Event

        # QUANTITY
        tk.Label(card, text="Quantity", bg="white", font=("Arial", 9, "bold"), fg="#555").grid(row=3, column=1, sticky="w", padx=20)
        
        qty_frame = tk.Frame(card, bg="white")
        qty_frame.grid(row=4, column=1, sticky="w", padx=20, pady=(0, 15))
        
        self.qty_spin = ttk.Spinbox(qty_frame, from_=1, to=100, width=10, font=("Arial", 10))
        self.qty_spin.set(1)
        self.qty_spin.pack(side="left")
        
        # Label to show max available
        self.max_qty_lbl = tk.Label(qty_frame, text="(Select item)", bg="white", fg="#777", font=("Arial", 9))
        self.max_qty_lbl.pack(side="left", padx=10)

        # AUTO FILLED ID
        self.id_entry = self.make_entry(card, "Item Barcode / ID (Auto)", 5, 1, readonly=True)
        
        # DATE
        today = datetime.now().strftime("%Y-%m-%d %H:%M")
        self.make_entry(card, "Date Borrowed (Auto)", 6, 1, val=today, readonly=True)

        # BUTTONS
        btn_row = tk.Frame(card, bg="white", pady=20)
        btn_row.grid(row=7, column=0, columnspan=2, sticky="e", pady=(20, 0))
        
        tk.Button(btn_row, text="Confirm Borrow", bg=COLORS["primary_green"], fg="white", 
                  font=("Arial", 10, "bold"), relief="flat", padx=25, pady=8,
                  command=self.confirm_borrow).pack(side="right")

    def make_entry(self, parent, label, r, c, val="", readonly=False):
        tk.Label(parent, text=label, bg="white", font=("Arial", 9, "bold"), fg="#555").grid(row=r*2-1, column=c, sticky="w", padx=(20 if c==1 else 0))
        e = tk.Entry(parent, relief="solid", bd=1, width=30, font=("Arial", 10), bg="#FAFAFA" if readonly else "white")
        e.grid(row=r*2, column=c, sticky="w", pady=(0, 15), ipady=5, padx=(20 if c==1 else 0))
        if val: e.insert(0, val)
        if readonly: e.config(state="readonly")
        return e

    def on_item_select(self, event):
        """Automate ID filling and Max Quantity display"""
        selected_item = self.item_cb.get()
        details = get_item_details(selected_item)
        
        # Update ID Entry
        self.id_entry.config(state="normal")
        self.id_entry.delete(0, tk.END)
        self.id_entry.insert(0, details['id'])
        self.id_entry.config(state="readonly")

        # Update Max Quantity Label
        max_qty = details['qty']
        self.max_qty_lbl.config(text=f"(Max: {max_qty} pcs)")

    def confirm_borrow(self):
        """Validate Quantity and Save"""
        item_name = self.item_cb.get()
        if not item_name:
            ErrorHandler.show_error("Input Error", "Please select an item.")
            return

        details = get_item_details(item_name)
        max_qty = details['qty']
        
        try:
            # USE THE NEW ERROR HANDLER
            if ErrorHandler.validate_quantity(self.qty_spin.get(), max_qty):
                # Success Logic
                ErrorHandler.show_warning("Success", f"Borrow request confirmed for {self.qty_spin.get()}x {item_name}")
                self.controller.show_dashboard()
        except ValueError as e:
            ErrorHandler.show_error("Quantity Error", str(e))