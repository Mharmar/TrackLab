# gui/popups.py
import tkinter as tk
from tkinter import ttk, messagebox
import random
from utils.colors import COLORS
from database.mock_db import INVENTORY_DB, get_item_details

class AddItemPopup:
    def __init__(self, parent_root):
        self.top = tk.Toplevel(parent_root)
        self.top.title("Add Inventory")
        self.top.geometry("400x500")
        self.top.configure(bg="white")
        
        # Make it a modal window
        self.top.transient(parent_root)
        self.top.grab_set()
        
        self.build_ui()

    def build_ui(self):
        tk.Label(self.top, text="Add Inventory", font=("Arial", 16, "bold"), 
                 bg="white", fg=COLORS["primary_green"]).pack(pady=20)
        tk.Label(self.top, text="(Inventory Logic Here)", bg="white").pack()
        tk.Button(self.top, text="Close", command=self.top.destroy).pack(pady=20)

class BorrowPopup:
    def __init__(self, parent_root):
        self.top = tk.Toplevel(parent_root)
        self.top.title("Quick Borrow")
        self.top.geometry("450x680") 
        self.top.configure(bg="white")

        # --- KEY FIX: Make it pop up ON TOP and HOLD FOCUS ---
        self.top.transient(parent_root) # Keep on top of main window
        self.top.grab_set()             # Prevent clicking background
        self.top.focus_force()          # Force focus to this window

        self.build_ui()

    def build_ui(self):
        # Header
        tk.Label(self.top, text="Quick Borrow", font=("Arial", 18, "bold"), 
                 bg="white", fg=COLORS["primary_green"]).pack(pady=(20, 5))
        tk.Label(self.top, text="Enter details to check out items.", font=("Arial", 10), 
                 bg="white", fg="#777").pack(pady=(0, 20))

        # Container
        form_frame = tk.Frame(self.top, bg="white", padx=30)
        form_frame.pack(fill="both", expand=True)

        # 1. Personal Info
        self.create_label_entry(form_frame, "Full Name")
        self.create_label_entry(form_frame, "Contact Number")
        self.create_label_entry(form_frame, "Department / Section")

        # 2. Automated Info (Simulating logged in user or scan)
        auto_id = f"STU-{random.randint(10000,99999)}"
        self.create_label_entry(form_frame, "Student ID (Auto-Generated)", val=auto_id, readonly=True)

        # 3. Equipment Selection
        tk.Label(form_frame, text="Select Equipment", bg="white", font=("Arial", 9, "bold"), fg="#555").pack(anchor="w", pady=(10, 0))
        
        item_list = list(INVENTORY_DB.keys())
        self.item_cb = ttk.Combobox(form_frame, values=item_list, state="readonly", font=("Arial", 10))
        self.item_cb.pack(fill="x", pady=(5, 0), ipady=4)
        self.item_cb.bind("<<ComboboxSelected>>", self.on_item_select)

        # 4. Equipment ID (Auto)
        self.eq_id_entry = self.create_label_entry(form_frame, "Equipment ID (Auto)", readonly=True)

        # 5. Quantity Section
        qty_container = tk.Frame(form_frame, bg="white")
        qty_container.pack(fill="x", pady=(10, 0))
        
        tk.Label(qty_container, text="Quantity", bg="white", font=("Arial", 9, "bold"), fg="#555").pack(anchor="w")
        
        qty_inner = tk.Frame(form_frame, bg="white")
        qty_inner.pack(fill="x", pady=5)
        
        self.qty_spin = ttk.Spinbox(qty_inner, from_=1, to=100, width=10, font=("Arial", 10))
        self.qty_spin.set(1)
        self.qty_spin.pack(side="left")
        
        self.max_lbl = tk.Label(qty_inner, text="(Max: -)", bg="white", fg="#999")
        self.max_lbl.pack(side="left", padx=10)

        # Buttons
        btn_frame = tk.Frame(self.top, bg="white", pady=20)
        btn_frame.pack(fill="x", padx=30)

        tk.Button(btn_frame, text="Confirm", bg=COLORS["primary_green"], fg="white", 
                  font=("Arial", 10, "bold"), relief="flat", pady=10, width=15, cursor="hand2",
                  command=self.confirm).pack(side="right")
        
        tk.Button(btn_frame, text="Cancel", bg="#F0F0F0", fg="#333", 
                  font=("Arial", 10), relief="flat", pady=10, width=10, cursor="hand2",
                  command=self.top.destroy).pack(side="right", padx=10)

    def create_label_entry(self, parent, label, val="", readonly=False):
        tk.Label(parent, text=label, bg="white", font=("Arial", 9, "bold"), fg="#555").pack(anchor="w", pady=(10, 0))
        e = tk.Entry(parent, relief="solid", bd=1, font=("Arial", 10), bg="#FAFAFA" if readonly else "white")
        e.pack(fill="x", pady=(5, 0), ipady=4)
        if val: e.insert(0, val)
        if readonly: e.config(state="readonly")
        return e

    def on_item_select(self, event):
        name = self.item_cb.get()
        details = get_item_details(name)
        
        # Update EQ ID
        self.eq_id_entry.config(state="normal")
        self.eq_id_entry.delete(0, tk.END)
        self.eq_id_entry.insert(0, details["id"])
        self.eq_id_entry.config(state="readonly")
        
        # Update Max Qty
        self.max_lbl.config(text=f"(Max: {details['qty']})")
        self.qty_spin.config(to=details['qty']) # Limit spinbox to max

    def confirm(self):
        # Add Quantity Logic Check
        try:
            qty = int(self.qty_spin.get())
            item = self.item_cb.get()
            if not item:
                messagebox.showerror("Error", "Please select an item.")
                return
                
            details = get_item_details(item)
            if qty > details['qty']:
                messagebox.showerror("Error", f"Cannot borrow {qty}. Only {details['qty']} available.")
                return
                
            messagebox.showinfo("Success", f"Borrow transaction recorded for {qty}x {item}!")
            self.top.destroy()
        except ValueError:
            messagebox.showerror("Error", "Invalid Quantity")