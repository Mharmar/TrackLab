# gui/dashboard_page.py
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from utils.colors import COLORS
from gui.popups import AddItemPopup

class DashboardPage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg=COLORS["bg_light"])
        self.controller = controller
        self.build_ui()

    def build_ui(self):
        # --- TOP NAV BAR ---
        nav_bar = tk.Frame(self, bg="white", height=60, padx=20)
        nav_bar.pack(side="top", fill="x", pady=(0, 2))

        tk.Label(nav_bar, text="TRACKLAB", font=("Arial", 16, "bold"), 
                 fg=COLORS["primary_green"], bg="white").pack(side="left", pady=15)
        
        # Nav Buttons
        nav_items = ["Dashboard", "Equipment", "Borrow", "Reports"]
        for item in nav_items:
            cmd = self.controller.show_borrow_page if item == "Borrow" else None
            tk.Button(nav_bar, text=item, bg="white", fg="#555", relief="flat", 
                      font=("Arial", 10), command=cmd).pack(side="right", padx=10, pady=15)

        # --- MAIN CONTENT ---
        content_frame = tk.Frame(self, bg=COLORS["bg_light"], padx=20, pady=20)
        content_frame.pack(fill="both", expand=True)

        # FIX: Give equal weight or specific ratios so Left Panel doesn't shrink
        content_frame.columnconfigure(0, weight=1, uniform="group1") 
        content_frame.columnconfigure(1, weight=1, uniform="group1")

        # LEFT PANEL
        self.build_left_panel(content_frame)
        
        # RIGHT PANEL
        self.build_right_panel(content_frame)

    # ==========================================
    # LEFT PANEL: ACTIVE BORROWERS
    # ==========================================
    def build_left_panel(self, parent):
        left_container = tk.Frame(parent, bg="white")
        left_container.grid(row=0, column=0, sticky="nsew", padx=(0, 20))
        
        # Prevent shrinking by turning off propagation for the container
        left_container.grid_propagate(False)

        # Header
        header_frame = tk.Frame(left_container, bg="white", padx=15, pady=15)
        header_frame.pack(fill="x")
        tk.Label(header_frame, text="Current Equipment Holders", font=("Arial", 14, "bold"), 
                 bg="white", fg=COLORS["text_dark"]).pack(anchor="w")

        # Scrollable Wrapper
        canvas_frame = tk.Frame(left_container, bg="white")
        canvas_frame.pack(fill="both", expand=True)

        canvas = tk.Canvas(canvas_frame, bg="white", highlightthickness=0)
        scrollbar = ttk.Scrollbar(canvas_frame, orient="vertical", command=canvas.yview)
        scroll_content = tk.Frame(canvas, bg="white", padx=15)

        # Link scrollbar
        scroll_content.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        # Create window inside canvas (width matches canvas)
        canvas.create_window((0, 0), window=scroll_content, anchor="nw", width=canvas.winfo_reqwidth())
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Force inner frame to match canvas width on resize
        canvas.bind("<Configure>", lambda e: canvas.itemconfig(canvas.find_all()[0], width=e.width))

        # Mock Data
        borrowers = [
            {"name": "Khan", "items": "3x Beakers", "status": "Ongoing", "col": COLORS["ongoing"]},
            {"name": "Malapare", "items": "Microscope Kit", "status": "Returned", "col": COLORS["returned"]},
            {"name": "Cruz", "items": "Extension Cord", "status": "Overdue", "col": COLORS["overdue"]},
            {"name": "Santos", "items": "Safety Goggles", "status": "Ongoing", "col": COLORS["ongoing"]},
            {"name": "Reyes", "items": "Digital Scale", "status": "Returned", "col": COLORS["returned"]},
            {"name": "Dizon", "items": "Flask Set", "status": "Ongoing", "col": COLORS["ongoing"]},
        ]

        for data in borrowers:
            card = tk.Frame(scroll_content, bg="white")
            card.pack(fill="x", pady=10)
            
            top = tk.Frame(card, bg="white")
            top.pack(fill="x")
            tk.Label(top, text=data["name"], font=("Arial", 11, "bold"), bg="white").pack(side="left")
            
            status = tk.Frame(top, bg="white")
            status.pack(side="right")
            tk.Button(status, text="🗑", relief="flat", bg="white", fg="#999").pack(side="right", padx=5)
            tk.Label(status, text=data["status"], fg=data["col"], bg="white", font=("Arial", 9, "bold")).pack(side="right")

            tk.Label(card, text=f"Items: {data['items']}", fg=COLORS["text_light"], bg="white", font=("Arial", 9)).pack(anchor="w")
            ttk.Separator(card, orient="horizontal").pack(fill="x", pady=(10, 0))

        tk.Button(left_container, text="+ Add New Equipment", bg=COLORS["primary_green"], fg="white", 
                  relief="flat", pady=12, font=("Arial", 10, "bold"),
                  command=lambda: AddItemPopup(self.winfo_toplevel())).pack(side="bottom", fill="x", padx=15, pady=15)

    # ==========================================
    # RIGHT PANEL: INVENTORY (Accordion)
    # ==========================================
    def build_right_panel(self, parent):
        right_panel = tk.Frame(parent, bg="white")
        right_panel.grid(row=0, column=1, sticky="nsew")
        right_panel.grid_propagate(False) # Fix ratio

        # Header
        header_block = tk.Frame(right_panel, bg=COLORS["primary_green"], pady=15, padx=15)
        header_block.pack(fill="x")
        tk.Label(header_block, text="☰  Available Equipment", font=("Arial", 12, "bold"), 
                 bg=COLORS["primary_green"], fg="white").pack(anchor="w")

        # Scrollable Wrapper for Categories
        canvas_frame = tk.Frame(right_panel, bg="white")
        canvas_frame.pack(fill="both", expand=True)

        self.inv_canvas = tk.Canvas(canvas_frame, bg="white", highlightthickness=0)
        scrollbar = ttk.Scrollbar(canvas_frame, orient="vertical", command=self.inv_canvas.yview)
        
        self.category_container = tk.Frame(self.inv_canvas, bg="white", padx=10, pady=10)

        self.category_container.bind(
            "<Configure>",
            lambda e: self.inv_canvas.configure(scrollregion=self.inv_canvas.bbox("all"))
        )
        
        self.inv_canvas.create_window((0, 0), window=self.category_container, anchor="nw", tags="window")
        self.inv_canvas.configure(yscrollcommand=scrollbar.set)

        self.inv_canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Make inner frame width match canvas
        self.inv_canvas.bind("<Configure>", lambda e: self.inv_canvas.itemconfig("window", width=e.width))

        # MOCK DATA
        inventory_data = {
            "Personal Protective Equip...": [
                {"name": "Safety Goggles", "qty": 30, "status": "Available"},
                {"name": "Lab Coats (L)", "qty": 5, "status": "Out of Stock"},
            ],
            "Glassware": [
                {"name": "Beaker 500ml", "qty": 12, "status": "Available"},
                {"name": "Test Tubes", "qty": 50, "status": "Available"},
                {"name": "Flask", "qty": 2, "status": "Broken"},
            ],
            "Measurement Tools": [
                {"name": "Digital Scale", "qty": 4, "status": "Available"},
            ],
             "Specialized Apparatus": [],
             "Handling and Containment": []
        }

        for cat_name, items in inventory_data.items():
            self.create_accordion_category(self.category_container, cat_name, items)

    def create_accordion_category(self, parent, cat_name, items):
        wrapper = tk.Frame(parent, bg="white")
        wrapper.pack(fill="x", pady=2)

        content_frame = tk.Frame(wrapper, bg="#F9F9F9", padx=10, pady=5)
        
        def toggle():
            if content_frame.winfo_viewable():
                content_frame.pack_forget()
                icon_lbl.config(text="▶")
            else:
                content_frame.pack(fill="x")
                icon_lbl.config(text="▼")
            # FIX: Update scrollregion immediately after toggle
            self.category_container.update_idletasks()
            self.inv_canvas.configure(scrollregion=self.inv_canvas.bbox("all"))
        
        btn_frame = tk.Frame(wrapper, bg="white", height=40, cursor="hand2")
        btn_frame.pack(fill="x")
        btn_frame.pack_propagate(False)
        btn_frame.bind("<Button-1>", lambda e: toggle())

        icon_lbl = tk.Label(btn_frame, text="▶", bg="white", fg=COLORS["text_light"], font=("Arial", 10))
        icon_lbl.pack(side="left", padx=(5, 10))
        
        name_lbl = tk.Label(btn_frame, text=cat_name, bg="white", fg=COLORS["text_dark"], font=("Arial", 10, "bold"))
        name_lbl.pack(side="left")

        ttk.Separator(wrapper, orient="horizontal").pack(fill="x")

        # Items
        if not items:
            tk.Label(content_frame, text="No items.", font=("Arial", 8, "italic"), bg="#F9F9F9", fg="#999").pack(anchor="w", pady=5)
        else:
            h_row = tk.Frame(content_frame, bg="#F9F9F9", pady=2)
            h_row.pack(fill="x")
            tk.Label(h_row, text="Item Name", width=15, anchor="w", font=("Arial", 8, "bold"), bg="#F9F9F9").pack(side="left")
            tk.Label(h_row, text="Qty", width=5, font=("Arial", 8, "bold"), bg="#F9F9F9").pack(side="left")
            tk.Label(h_row, text="Status", width=10, font=("Arial", 8, "bold"), bg="#F9F9F9").pack(side="left")

            for item in items:
                self.create_inventory_row(content_frame, item)

    def create_inventory_row(self, parent, item):
        row = tk.Frame(parent, bg="#F9F9F9", pady=2)
        row.pack(fill="x")

        tk.Label(row, text=item["name"], width=15, anchor="w", bg="#F9F9F9", font=("Arial", 9)).pack(side="left")
        tk.Label(row, text=str(item["qty"]), width=5, bg="#F9F9F9", font=("Arial", 9)).pack(side="left")
        
        s_color = COLORS["success"]