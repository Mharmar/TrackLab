# gui/equipment_page.py
import tkinter as tk
from tkinter import ttk, messagebox
from utils.colors import COLORS
from database.mock_db import INVENTORY_DB
from gui.popups import AddItemPopup

class EquipmentPage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg=COLORS["bg_light"])
        self.controller = controller
        self.build_ui()

    def build_ui(self):
        # =================================================================
        # 1. TOP NAVIGATION BAR
        # =================================================================
        nav_bar = tk.Frame(self, bg="white", height=60, padx=20)
        nav_bar.pack(side="top", fill="x", pady=(0, 2))

        tk.Label(nav_bar, text="TRACKLAB", font=("Arial", 16, "bold"),
                 fg=COLORS["primary_green"], bg="white").pack(side="left", pady=15)

        nav_items = ["Dashboard", "Equipment", "Borrow", "Reports"]
        for item in nav_items:
            if item == "Dashboard":
                cmd = self.controller.show_dashboard
            elif item == "Borrow":
                cmd = self.controller.show_borrow_page
            elif item == "Reports":
                cmd = self.controller.show_reports
            elif item == "Equipment":
                cmd = None # Already here
            else:
                cmd = lambda x=item: print(f"Clicked {x}")

            # Active State Styling
            color = COLORS["primary_green"] if item == "Equipment" else "#555"
            font_style = ("Arial", 10, "bold") if item == "Equipment" else ("Arial", 10)

            tk.Button(nav_bar, text=item, bg="white", fg=color,
                      relief="flat", font=font_style, command=cmd
            ).pack(side="right", padx=10, pady=15)

        # =================================================================
        # 2. MAIN CONTENT
        # =================================================================
        main_content = tk.Frame(self, bg=COLORS["bg_light"])
        main_content.pack(fill="both", expand=True, padx=40, pady=20)

        # Header
        tk.Label(main_content, text="Equipment Inventory", font=("Arial", 22, "bold"),
                 bg=COLORS["bg_light"], fg=COLORS["text_dark"]).pack(anchor="w", pady=(0, 15))

        # ------------------------------------------------------
        # CONTROL CARD (Search, Filter, Add)
        # ------------------------------------------------------
        control_card = tk.Frame(main_content, bg="white", padx=20, pady=20)
        control_card.pack(fill="x", pady=(0, 15))
        control_card.config(highlightbackground="#E0E0E0", highlightthickness=1)

        # Grid Layout for Controls
        control_card.columnconfigure(2, weight=1) # Spacer column

        # Search Bar
        tk.Label(control_card, text="Search:", bg="white", font=("Arial", 9, "bold"), fg="#555").grid(row=0, column=0, sticky="w")
        self.search_var = tk.StringVar()
        self.search_var.trace("w", self.on_search_change) # Real-time search
        search_entry = ttk.Entry(control_card, textvariable=self.search_var, width=30)
        search_entry.grid(row=1, column=0, sticky="w", ipady=3, padx=(0, 20))

        # Filter Dropdown
        tk.Label(control_card, text="Status:", bg="white", font=("Arial", 9, "bold"), fg="#555").grid(row=0, column=1, sticky="w")
        self.filter_cb = ttk.Combobox(control_card, values=["All", "Available", "Borrowed", "Damaged", "Out of Stock"], state="readonly", width=20)
        self.filter_cb.current(0)
        self.filter_cb.grid(row=1, column=1, sticky="w", ipady=3)
        self.filter_cb.bind("<<ComboboxSelected>>", self.on_search_change)

        # Add Button (Right aligned)
        tk.Button(control_card, text="+ Add New Equipment", bg=COLORS["primary_green"], fg="white",
                  relief="flat", font=("Arial", 10, "bold"), padx=20, pady=5,
                  command=lambda: AddItemPopup(self.winfo_toplevel())
                  ).grid(row=1, column=3, sticky="e")

        # ------------------------------------------------------
        # TABLE AREA
        # ------------------------------------------------------
        table_card = tk.Frame(main_content, bg="white", padx=20, pady=20)
        table_card.pack(fill="both", expand=True)
        table_card.config(highlightbackground="#E0E0E0", highlightthickness=1)

        # Action Toolbar (Above Table)
        action_bar = tk.Frame(table_card, bg="white")
        action_bar.pack(fill="x", pady=(0, 10))
        
        tk.Label(action_bar, text="Select a row to perform actions:", bg="white", fg="#777", font=("Arial", 9, "italic")).pack(side="left")
        
        tk.Button(action_bar, text="🗑 Delete Selected", bg="#FFEBEE", fg=COLORS["danger"], relief="flat", font=("Arial", 9),
                  command=self.delete_selected).pack(side="right", padx=5)
        
        tk.Button(action_bar, text="✎ Edit Selected", bg="#E3F2FD", fg="#1976D2", relief="flat", font=("Arial", 9),
                  command=self.edit_selected).pack(side="right")

        # Treeview Setup
        columns = ("id", "name", "category", "qty", "status")
        self.tree = ttk.Treeview(table_card, columns=columns, show="headings", selectmode="browse")
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(table_card, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        scrollbar.pack(side="right", fill="y")
        self.tree.pack(fill="both", expand=True)

        # Define Headings
        self.tree.heading("id", text="Equipment ID")
        self.tree.heading("name", text="Name")
        self.tree.heading("category", text="Category") # Not in mock DB yet, but good to have col
        self.tree.heading("qty", text="Qty")
        self.tree.heading("status", text="Status")

        # Define Columns
        self.tree.column("id", width=100)
        self.tree.column("name", width=250)
        self.tree.column("category", width=150)
        self.tree.column("qty", width=50, anchor="center")
        self.tree.column("status", width=100)

        # Bind Double Click to Edit
        self.tree.bind("<Double-1>", lambda e: self.edit_selected())

        # Load Initial Data
        self.refresh_table()

    # =================================================================
    # LOGIC FUNCTIONS
    # =================================================================
    def refresh_table(self):
        """Clears and reloads the table based on filters"""
        # Clear existing
        for item in self.tree.get_children():
            self.tree.delete(item)

        search_term = self.search_var.get().lower()
        status_filter = self.filter_cb.get()

        # Loop through Mock DB
        for name, details in INVENTORY_DB.items():
            # Filter Logic
            matches_search = search_term in name.lower() or search_term in details['id'].lower()
            matches_status = status_filter == "All" or status_filter == details['status']

            if matches_search and matches_status:
                # Insert row
                # Note: Category is hardcoded as 'General' since it's not in mock_db yet
                self.tree.insert("", "end", values=(
                    details['id'], 
                    name, 
                    "General", 
                    details['qty'], 
                    details['status']
                ))

    def on_search_change(self, *args):
        self.refresh_table()

    def delete_selected(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Warning", "Please select an item to delete.")
            return
        
        # Get Item Name from the selected row
        item_values = self.tree.item(selected[0])['values']
        item_name = item_values[1] # Column 1 is Name

        # Confirm Dialog
        confirm = messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete '{item_name}'?")
        if confirm:
            # In real app: Database delete query here
            self.tree.delete(selected[0])
            messagebox.showinfo("Deleted", f"{item_name} has been removed.")

    def edit_selected(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Warning", "Please select an item to edit.")
            return
        
        item_values = self.tree.item(selected[0])['values']
        # Open Edit Popup (Future implementation)
        messagebox.showinfo("Edit Equipment", f"Opening edit form for: {item_values[1]}\n(ID: {item_values[0]})")