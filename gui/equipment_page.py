# gui/equipment_page.py
import tkinter as tk
from tkinter import ttk, messagebox
from utils.colors import COLORS
from database.mock_db import INVENTORY_DB, RETURN_HISTORY
from gui.popups import AddItemPopup

class EquipmentPage(tk.Frame):
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

        # === FIXED NAVIGATION LOGIC ===
        nav_items = ["Dashboard", "Equipment", "Borrow", "Reports", "Profile"]
        for item in nav_items:
            if item == "Dashboard":
                cmd = self.controller.show_dashboard
            elif item == "Equipment":
                cmd = None # Already here
            elif item == "Borrow":
                cmd = self.controller.show_borrow_page
            elif item == "Reports":
                cmd = self.controller.show_reports
            elif item == "Profile":
                cmd = self.controller.show_profile_page
            else:
                cmd = None

            # Active State
            color = COLORS["primary_green"] if item == "Equipment" else "#555"
            font = ("Arial", 10, "bold") if item == "Equipment" else ("Arial", 10)
            tk.Button(nav_bar, text=item, bg="white", fg=color, relief="flat", 
                      font=font, command=cmd).pack(side="right", padx=10, pady=15)

        # ... (Keep the rest of your tabs and main content) ...
        # If you need the rest of the code, use the version from the previous "Tabs" response.
        # COPY EVERYTHING BELOW THIS LINE FROM THE PREVIOUS 'tabs' RESPONSE FOR equipment_page.py
        # --- MAIN LAYOUT ---
        main_content = tk.Frame(self, bg=COLORS["bg_light"])
        main_content.pack(fill="both", expand=True, padx=30, pady=20)

        tk.Label(main_content, text="Equipment Management", font=("Arial", 22, "bold"), 
                 bg=COLORS["bg_light"], fg=COLORS["text_dark"]).pack(anchor="w", pady=(0, 15))

        style = ttk.Style()
        style.configure("TNotebook", background=COLORS["bg_light"])
        style.configure("TNotebook.Tab", font=("Arial", 10, "bold"), padding=[15, 5])

        notebook = ttk.Notebook(main_content)
        notebook.pack(fill="both", expand=True)

        self.tab_inventory = tk.Frame(notebook, bg="white", padx=20, pady=20)
        self.tab_returns = tk.Frame(notebook, bg="white", padx=20, pady=20)

        notebook.add(self.tab_inventory, text="  Current Inventory  ")
        notebook.add(self.tab_returns, text="  Returned Items (History)  ")

        self.build_inventory_tab()
        self.build_returns_tab()

    def build_inventory_tab(self):
        ctrl = tk.Frame(self.tab_inventory, bg="white")
        ctrl.pack(fill="x", pady=(0, 15))

        tk.Label(ctrl, text="Search:", bg="white", font=("Arial", 9, "bold")).pack(side="left")
        self.search_var = tk.StringVar()
        self.search_var.trace("w", self.refresh_inventory)
        ttk.Entry(ctrl, textvariable=self.search_var, width=25).pack(side="left", padx=10)

        tk.Button(ctrl, text="+ Add Equipment", bg=COLORS["primary_green"], fg="white", 
                  relief="flat", font=("Arial", 9, "bold"), padx=15,
                  command=lambda: AddItemPopup(self.winfo_toplevel())).pack(side="right")

        columns = ("id", "name", "category", "qty", "status")
        self.tree_inv = ttk.Treeview(self.tab_inventory, columns=columns, show="headings")
        
        for col in columns: self.tree_inv.heading(col, text=col.title())
        self.tree_inv.column("id", width=80)
        self.tree_inv.column("qty", width=50)
        
        self.tree_inv.pack(fill="both", expand=True)
        self.refresh_inventory()

        btn_row = tk.Frame(self.tab_inventory, bg="white")
        btn_row.pack(fill="x", pady=10)
        tk.Button(btn_row, text="Edit Selected", bg="#E3F2FD", relief="flat", command=self.edit_selected).pack(side="right")
        tk.Button(btn_row, text="Delete Selected", bg="#FFEBEE", fg="red", relief="flat", command=self.delete_selected).pack(side="right", padx=10)

    def refresh_inventory(self, *args):
        for row in self.tree_inv.get_children(): self.tree_inv.delete(row)
        term = self.search_var.get().lower()
        
        for name, d in INVENTORY_DB.items():
            if term in name.lower() or term in d['id'].lower():
                self.tree_inv.insert("", "end", values=(d['id'], name, "General", d['qty'], d['status']))

    def edit_selected(self):
        messagebox.showinfo("Edit", "Edit feature ready.")

    def delete_selected(self):
        sel = self.tree_inv.selection()
        if sel:
            self.tree_inv.delete(sel[0])
            messagebox.showinfo("Deleted", "Item removed.")

    def build_returns_tab(self):
        tk.Label(self.tab_returns, text="History of returned items and their condition checks.", 
                 bg="white", fg="#777", font=("Arial", 10, "italic")).pack(anchor="w", pady=(0, 10))

        columns = ("id", "item", "borrower", "date", "condition", "remarks")
        self.tree_ret = ttk.Treeview(self.tab_returns, columns=columns, show="headings")

        self.tree_ret.heading("id", text="Return ID")
        self.tree_ret.heading("item", text="Item Name")
        self.tree_ret.heading("borrower", text="Returned By")
        self.tree_ret.heading("date", text="Date")
        self.tree_ret.heading("condition", text="Condition")
        self.tree_ret.heading("remarks", text="Remarks / Notes")

        self.tree_ret.column("id", width=80)
        self.tree_ret.column("date", width=100)
        self.tree_ret.column("condition", width=120)
        self.tree_ret.column("remarks", width=250)

        self.tree_ret.pack(fill="both", expand=True)

        self.refresh_returns()
        
        tk.Button(self.tab_returns, text="↻ Refresh Log", bg="white", fg=COLORS["primary_green"], 
                  relief="solid", bd=1, command=self.refresh_returns).pack(pady=10, anchor="e")

    def refresh_returns(self):
        for row in self.tree_ret.get_children(): self.tree_ret.delete(row)
        
        for log in RETURN_HISTORY:
            tag = "damage" if log["condition"] != "Good" else "good"
            self.tree_ret.insert("", "end", values=(
                log['id'], log['item'], log['borrower'], log['date'], log['condition'], log['remarks']
            ), tags=(tag,))
        
        self.tree_ret.tag_configure("damage", foreground="red")
        self.tree_ret.tag_configure("good", foreground="green")