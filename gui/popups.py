# gui/popups.py
import tkinter as tk
from tkinter import ttk, messagebox
import random
from utils.colors import COLORS
from database.mock_db import INVENTORY_DB, get_item_details, RETURN_HISTORY
from datetime import datetime

# ===========================================================
# 1. ADD ITEM POPUP (For Inventory)
# ===========================================================
class AddItemPopup:
    def __init__(self, parent_root):
        self.top = tk.Toplevel(parent_root)
        self.top.title("Add Inventory")
        self.top.geometry("400x600")
        self.top.configure(bg="white")
        
        self.top.transient(parent_root)
        self.top.grab_set()
        self.top.focus_force()
        
        self.build_ui()

    def build_ui(self):
        tk.Label(self.top, text="Add Inventory", font=("Arial", 16, "bold"), 
                 bg="white", fg=COLORS["primary_green"]).pack(pady=20)
        
        container = tk.Frame(self.top, bg="white", padx=20)
        container.pack(fill="both", expand=True)

        self.name = self.create_entry(container, "Equipment Name")
        self.code = self.create_entry(container, "Item Code (Auto)", val=f"EQ-{random.randint(100,999)}")
        
        tk.Label(container, text="Category", bg="white", font=("Arial", 9, "bold"), fg="#555").pack(anchor="w", pady=(5,0))
        self.cat = ttk.Combobox(container, values=["Glassware", "PPE", "Tools"], state="readonly")
        self.cat.pack(fill="x", pady=5)
        self.cat.current(0)

        self.qty = self.create_entry(container, "Quantity")
        
        tk.Button(self.top, text="Save Item", bg=COLORS["primary_green"], fg="white", 
                  command=self.save).pack(pady=20)

    def create_entry(self, parent, label, val=""):
        tk.Label(parent, text=label, bg="white", font=("Arial", 9, "bold"), fg="#555").pack(anchor="w", pady=(5,0))
        e = tk.Entry(parent, relief="solid", bd=1)
        e.pack(fill="x", pady=5)
        if val: e.insert(0, val)
        return e

    def save(self):
        messagebox.showinfo("Success", "Item Added!")
        self.top.destroy()

# ===========================================================
# 2. QUICK BORROW POPUP (For Dashboard)
# ===========================================================
class BorrowPopup:
    def __init__(self, parent_root):
        self.top = tk.Toplevel(parent_root)
        self.top.title("Quick Borrow")
        self.top.geometry("450x680") 
        self.top.configure(bg="white")

        self.top.transient(parent_root)
        self.top.grab_set()
        self.top.focus_force()

        self.build_ui()

    def build_ui(self):
        tk.Label(self.top, text="Quick Borrow", font=("Arial", 18, "bold"), 
                 bg="white", fg=COLORS["primary_green"]).pack(pady=(20, 5))
        tk.Label(self.top, text="Enter details to check out items.", font=("Arial", 10), 
                 bg="white", fg="#777").pack(pady=(0, 20))

        form_frame = tk.Frame(self.top, bg="white", padx=30)
        form_frame.pack(fill="both", expand=True)

        self.create_label_entry(form_frame, "Full Name")
        self.create_label_entry(form_frame, "Contact Number")
        self.create_label_entry(form_frame, "Department / Section")

        auto_id = f"STU-{random.randint(10000,99999)}"
        self.create_label_entry(form_frame, "Student ID (Auto-Generated)", val=auto_id, readonly=True)

        tk.Label(form_frame, text="Select Equipment", bg="white", font=("Arial", 9, "bold"), fg="#555").pack(anchor="w", pady=(10, 0))
        
        item_list = list(INVENTORY_DB.keys())
        self.item_cb = ttk.Combobox(form_frame, values=item_list, state="readonly", font=("Arial", 10))
        self.item_cb.pack(fill="x", pady=(5, 0), ipady=4)
        self.item_cb.bind("<<ComboboxSelected>>", self.on_item_select)

        self.eq_id_entry = self.create_label_entry(form_frame, "Equipment ID (Auto)", readonly=True)

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
        self.eq_id_entry.config(state="normal")
        self.eq_id_entry.delete(0, tk.END)
        self.eq_id_entry.insert(0, details["id"])
        self.eq_id_entry.config(state="readonly")
        self.max_lbl.config(text=f"(Max: {details['qty']})")
        self.qty_spin.config(to=details['qty'])

    def confirm(self):
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

# ===========================================================
# 3. RETURN EQUIPMENT POPUP
# ===========================================================
class ReturnPopup:
    def __init__(self, parent_root, borrower_data):
        self.top = tk.Toplevel(parent_root)
        self.top.title("Return Equipment")
        self.top.geometry("400x550")
        self.top.configure(bg="white")
        self.data = borrower_data 

        self.top.transient(parent_root)
        self.top.grab_set()
        self.top.focus_force()

        self.build_ui()

    def build_ui(self):
        tk.Label(self.top, text="Return Process", font=("Arial", 16, "bold"), 
                 bg="white", fg=COLORS["primary_green"]).pack(pady=(20, 5))
        
        info_frame = tk.Frame(self.top, bg="#F5F5F5", padx=10, pady=10)
        info_frame.pack(fill="x", padx=30, pady=10)
        
        tk.Label(info_frame, text=f"Borrower: {self.data['name']}", bg="#F5F5F5", font=("Arial", 10, "bold")).pack(anchor="w")
        tk.Label(info_frame, text=f"Item: {self.data['items']}", bg="#F5F5F5", font=("Arial", 10)).pack(anchor="w")

        tk.Label(self.top, text="1. Condition Check", font=("Arial", 11, "bold"), 
                 bg="white", fg=COLORS["text_dark"]).pack(anchor="w", padx=30, pady=(10, 5))

        self.condition_var = tk.StringVar(value="Good")
        modes = [("Good Condition", "Good"), 
                 ("Minor Damage", "Minor"), 
                 ("Major Damage / Broken", "Major")]

        for text, mode in modes:
            tk.Radiobutton(self.top, text=text, variable=self.condition_var, value=mode,
                           bg="white", font=("Arial", 10)).pack(anchor="w", padx=40)

        tk.Label(self.top, text="2. Damage Notes / Remarks", font=("Arial", 11, "bold"), 
                 bg="white", fg=COLORS["text_dark"]).pack(anchor="w", padx=30, pady=(20, 5))

        self.notes_entry = tk.Text(self.top, height=4, width=30, relief="solid", bd=1, font=("Arial", 10))
        self.notes_entry.pack(padx=30, fill="x")

        btn_frame = tk.Frame(self.top, bg="white", pady=20)
        btn_frame.pack(fill="x", padx=30)

        tk.Button(btn_frame, text="Complete Return", bg=COLORS["primary_green"], fg="white", 
                  font=("Arial", 10, "bold"), relief="flat", pady=10, cursor="hand2",
                  command=self.process_return).pack(side="right", fill="x", expand=True)

    def process_return(self):
        cond = self.condition_var.get()
        notes = self.notes_entry.get("1.0", "end-1c").strip()
        if not notes: notes = "No remarks"

        # --- SAVE TO MOCK DATABASE ---
        if 'RETURN_HISTORY' in globals():
             new_log = {
                "id": f"RET-{random.randint(1000,9999)}",
                "item": self.data['items'],
                "borrower": self.data['name'],
                "date": datetime.now().strftime("%Y-%m-%d"),
                "condition": cond,
                "remarks": notes
            }
             RETURN_HISTORY.append(new_log)

        msg = f"Return Successful!\n\nCondition: {cond}\nSaved to Return History."
        if cond != "Good":
            msg += "\n\n⚠️ Item marked as Damaged."
        
        messagebox.showinfo("Return Complete", msg)
        self.top.destroy()