import tkinter as tk
from tkinter import ttk, messagebox
from utils.colors import COLORS
from utils.session import Session
from gui.popups import AddItemPopup, EditItemPopup
from database.equipment_db import get_all_equipment, delete_equipment
from database.return_db import get_return_history
# FIX: Removed circular import here

class EquipmentPage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg=COLORS["bg_light"])
        self.controller = controller
        
        self.user = Session.get_user()
        self.user_role = self.user.get('role', 'Student') if self.user else 'Student'
        
        self.build_ui()

    def build_ui(self):
        # NAV BAR
        nav_bar = tk.Frame(self, bg="white", height=60, padx=20)
        nav_bar.pack(side="top", fill="x", pady=(0, 2))
        
        # --- LOGO INTEGRATION ---
        if self.controller.logo_image:
            tk.Label(nav_bar, image=self.controller.logo_image, bg="white").pack(side="left", pady=10, padx=5)
        else:
            tk.Label(nav_bar, text="TRACKLAB", font=("Arial", 16, "bold"), 
                     fg=COLORS["primary_green"], bg="white").pack(side="left", pady=15)
        # ------------------------

        nav_items = ["Dashboard", "Equipment", "Borrow", "Reports", "Profile"]
        for item in nav_items:
            cmd = None
            if item == "Dashboard": cmd = self.controller.show_dashboard
            elif item == "Borrow": cmd = self.controller.show_borrow_page
            elif item == "Reports": cmd = self.controller.show_reports
            elif item == "Profile": cmd = self.controller.show_profile_page
            color = COLORS["primary_green"] if item == "Equipment" else "#555"
            font = ("Arial", 10, "bold") if item == "Equipment" else ("Arial", 10)
            tk.Button(nav_bar, text=item, bg="white", fg=color, relief="flat", font=font, command=cmd).pack(side="right", padx=10, pady=15)

        main_content = tk.Frame(self, bg=COLORS["bg_light"])
        main_content.pack(fill="both", expand=True, padx=30, pady=20)
        tk.Label(main_content, text="Equipment Management", font=("Arial", 22, "bold"), bg=COLORS["bg_light"]).pack(anchor="w", pady=(0, 15))

        notebook = ttk.Notebook(main_content)
        notebook.pack(fill="both", expand=True)
        self.tab_inv = tk.Frame(notebook, bg="white", padx=20, pady=20)
        self.tab_ret = tk.Frame(notebook, bg="white", padx=20, pady=20)
        notebook.add(self.tab_inv, text=" Current Inventory ")
        notebook.add(self.tab_ret, text=" Return History ")

        self.build_inventory_tab()
        self.build_returns_tab()

    def build_inventory_tab(self):
        ctrl = tk.Frame(self.tab_inv, bg="white")
        ctrl.pack(fill="x", pady=(0, 15))
        
        tk.Label(ctrl, text="Search:", bg="white", font=("Arial", 9, "bold")).pack(side="left")
        self.search_var = tk.StringVar(); self.search_var.trace("w", self.refresh_inventory)
        ttk.Entry(ctrl, textvariable=self.search_var, width=30).pack(side="left", padx=10)
        
        if self.user_role == "Admin":
            tk.Button(ctrl, text="+ Add Equipment", bg=COLORS["primary_green"], fg="white", 
                      command=lambda: AddItemPopup(self.winfo_toplevel(), callback=self.refresh_inventory)).pack(side="right")

        cols = ("id", "name", "cat", "qty", "cond")
        self.tree_inv = ttk.Treeview(self.tab_inv, columns=cols, show="headings", selectmode="browse")
        self.tree_inv.heading("id", text="ID (Code)"); self.tree_inv.column("id", width=100)
        self.tree_inv.heading("name", text="Name"); self.tree_inv.column("name", width=250)
        self.tree_inv.heading("cat", text="Category"); self.tree_inv.column("cat", width=150)
        self.tree_inv.heading("qty", text="Qty"); self.tree_inv.column("qty", width=80, anchor="center")
        self.tree_inv.heading("cond", text="Condition"); self.tree_inv.column("cond", width=100)
        
        sb = ttk.Scrollbar(self.tab_inv, orient="vertical", command=self.tree_inv.yview)
        self.tree_inv.configure(yscrollcommand=sb.set); sb.pack(side="right", fill="y")
        self.tree_inv.pack(fill="both", expand=True)

        if self.user_role == "Admin":
            actions = tk.Frame(self.tab_inv, bg="white")
            actions.pack(fill="x", pady=10)
            tk.Button(actions, text="✎ Edit Selected", bg="#E3F2FD", fg="#1976D2", command=self.edit_selected).pack(side="right", padx=5)
            tk.Button(actions, text="🗑 Delete Selected", bg="#FFEBEE", fg="red", command=self.delete_selected).pack(side="right")
        
        self.refresh_inventory()

    def refresh_inventory(self, *args):
        for row in self.tree_inv.get_children(): self.tree_inv.delete(row)
        term = self.search_var.get().lower()
        for i in get_all_equipment():
            if term in i['name'].lower() or term in i['code'].lower():
                self.tree_inv.insert("", "end", values=(i['code'], i['name'], i['category'], i['quantity'], i['condition']), tags=(str(i['equipment_id']),))

    def edit_selected(self):
        sel = self.tree_inv.selection()
        if not sel: return
        vals = self.tree_inv.item(sel[0])['values']
        data = {"db_id": self.tree_inv.item(sel[0])['tags'][0], "code": vals[0], "name": vals[1], "category": vals[2], "qty": vals[3], "status": vals[4]}
        EditItemPopup(self.winfo_toplevel(), data, callback=self.refresh_inventory)

    def delete_selected(self):
        sel = self.tree_inv.selection()
        if sel and messagebox.askyesno("Confirm", "Are you sure you want to permanently delete this equipment record?"):
            if delete_equipment(self.tree_inv.item(sel[0])['tags'][0]): self.refresh_inventory()

    def build_returns_tab(self):
        cols = ("date", "time", "item", "by", "cond", "notes")
        self.tree_ret = ttk.Treeview(self.tab_ret, columns=cols, show="headings")
        self.tree_ret.heading("date", text="Date"); self.tree_ret.column("date", width=100)
        self.tree_ret.heading("time", text="Time"); self.tree_ret.column("time", width=80)
        self.tree_ret.heading("item", text="Item Name"); self.tree_ret.column("item", width=200)
        self.tree_ret.heading("by", text="Returned By"); self.tree_ret.column("by", width=150)
        self.tree_ret.heading("cond", text="Condition"); self.tree_ret.column("cond", width=100)
        self.tree_ret.heading("notes", text="Remarks"); self.tree_ret.column("notes", width=250)
        
        sb = ttk.Scrollbar(self.tab_ret, orient="vertical", command=self.tree_ret.yview)
        self.tree_ret.configure(yscrollcommand=sb.set)
        sb.pack(side="right", fill="y")
        self.tree_ret.pack(fill="both", expand=True)
        
        tk.Button(self.tab_ret, text="Refresh History", command=self.refresh_history).pack(pady=5, anchor="e")
        self.refresh_history()

    def refresh_history(self):
        for row in self.tree_ret.get_children(): self.tree_ret.delete(row)
        for r in get_return_history():
            self.tree_ret.insert("", "end", values=(r['ret_date'], r['ret_time'], r['item_name'], r['returned_by'], r['condition'], r['remarks']))