# gui/dashboard_page.py
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from utils.colors import COLORS
from gui.popups import AddItemPopup, BorrowPopup, ReturnPopup
from database.borrow_db import get_active_borrows 
from database.equipment_db import get_all_equipment

class DashboardPage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg=COLORS["bg_light"])
        self.controller = controller
        # Store images/canvas refs to prevent garbage collection issues
        self.images = []
        self.build_ui()

    def build_ui(self):
        # --- TOP NAV BAR ---
        nav_bar = tk.Frame(self, bg="white", height=60, padx=20)
        nav_bar.pack(side="top", fill="x", pady=(0, 2))

        tk.Label(nav_bar, text="TRACKLAB", font=("Arial", 16, "bold"), 
                 fg=COLORS["primary_green"], bg="white").pack(side="left", pady=15)
        
        # === NAVIGATION LOGIC ===
        nav_items = ["Dashboard", "Equipment", "Borrow", "Reports", "Profile"]
        for item in nav_items:
            if item == "Dashboard":
                cmd = None # Already on Dashboard
            elif item == "Equipment":
                cmd = self.controller.show_equipment_page
            elif item == "Borrow":
                # Dashboard 'Borrow' button specifically opens the Full Page
                cmd = self.controller.show_borrow_page 
            elif item == "Reports":
                cmd = self.controller.show_reports
            elif item == "Profile":
                cmd = self.controller.show_profile_page
            else:
                cmd = None

            # Active State Styling
            color = COLORS["primary_green"] if item == "Dashboard" else "#555"
            font_style = ("Arial", 10, "bold") if item == "Dashboard" else ("Arial", 10)

            tk.Button(nav_bar, text=item, bg="white", fg=color, relief="flat", 
                      font=font_style, command=cmd).pack(side="right", padx=10, pady=15)

        # --- MAIN CONTENT CONTAINER ---
        content_frame = tk.Frame(self, bg=COLORS["bg_light"], padx=20, pady=20)
        content_frame.pack(fill="both", expand=True)

        content_frame.rowconfigure(0, weight=1) 
        content_frame.columnconfigure(0, weight=3) # Left side
        content_frame.columnconfigure(1, weight=2) # Right side

        # LEFT PANEL
        self.build_left_panel(content_frame)
        # RIGHT PANEL
        self.build_right_panel(content_frame)

    # ==========================================
    # HELPER: DRAW ROUNDED BACKGROUND
    # ==========================================
    def create_rounded_canvas(self, parent):
        canvas = tk.Canvas(parent, bg=COLORS["bg_light"], highlightthickness=0)
        canvas.pack(fill="both", expand=True)
        return canvas

    def draw_rounded_rect(self, canvas, x, y, w, h, radius=20, color="white"):
        points = [x+radius, y, x+radius, y, x+w-radius, y, x+w-radius, y, x+w, y, x+w, y+radius, x+w, y+radius, x+w, y+h-radius, x+w, y+h-radius, x+w, y+h, x+w-radius, y+h, x+w-radius, y+h, x+radius, y+h, x+radius, y+h, x, y+h, x, y+h-radius, x, y+h-radius, x, y+radius, x, y+radius, x, y]
        return canvas.create_polygon(points, fill=color, smooth=True)

    # ==========================================
    # LEFT PANEL: ACTIVE BORROWERS
    # ==========================================
    def build_left_panel(self, parent):
        left_container = tk.Frame(parent, bg=COLORS["bg_light"])
        left_container.grid(row=0, column=0, sticky="nsew", padx=(0, 20))
        
        self.left_canvas = self.create_rounded_canvas(left_container)
        
        def update_left_bg(event):
            self.left_canvas.delete("bg")
            self.draw_rounded_rect(self.left_canvas, 0, 0, event.width, event.height, 25, "white")
        self.left_canvas.bind("<Configure>", update_left_bg)

        tk.Label(self.left_canvas, text="Current Equipment Holders", font=("Arial", 14, "bold"), 
                 bg="white", fg=COLORS["text_dark"]).place(x=20, y=20)

        # Scrollable Area
        list_frame = tk.Frame(self.left_canvas, bg="white")
        list_frame.place(x=5, y=60, relwidth=0.96, relheight=0.85) 

        scroll_canvas = tk.Canvas(list_frame, bg="white", highlightthickness=0)
        scrollbar = ttk.Scrollbar(list_frame, orient="vertical", command=scroll_canvas.yview)
        
        self.borrower_scroll_content = tk.Frame(scroll_canvas, bg="white")
        self.borrower_scroll_content.bind(
            "<Configure>",
            lambda e: scroll_canvas.configure(scrollregion=scroll_canvas.bbox("all"))
        )

        scroll_canvas.create_window((0, 0), window=self.borrower_scroll_content, anchor="nw", width=550)
        scroll_canvas.configure(yscrollcommand=scrollbar.set)

        scroll_canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        scroll_canvas.bind("<Configure>", lambda e: scroll_canvas.itemconfig(scroll_canvas.find_all()[0], width=e.width))

        # --- REAL DATABASE DATA (Active Borrows) ---
        try:
            db_data = get_active_borrows() 
        except:
            db_data = [] # Fallback if DB fails

        # Convert DB results to UI format
        borrowers = []
        if db_data:
            for row in db_data:
                borrowers.append({
                    "id": row.get('borrow_id'), 
                    "name": row.get('full_name', 'Unknown'), 
                    "items": row.get('item_name', 'Unknown Item'), 
                    "status": row.get('status', 'Ongoing'), 
                    "col": COLORS["ongoing"]
                })
        else:
            tk.Label(self.borrower_scroll_content, text="No active borrows.", bg="white", fg="#999").pack(pady=20)

        for data in borrowers:
            self.create_borrower_card(data)

        # Quick Borrow Button
        add_btn = tk.Button(self.left_canvas, text="+ Quick Borrow", bg=COLORS["primary_green"], fg="white", 
                  relief="flat", pady=10, font=("Arial", 10, "bold"), cursor="hand2",
                  command=lambda: BorrowPopup(self.winfo_toplevel()))
        add_btn.place(relx=0.05, rely=0.92, relwidth=0.9)

    def create_borrower_card(self, data):
        card = tk.Frame(self.borrower_scroll_content, bg="white")
        card.pack(fill="x", pady=5, padx=10)
        
        top = tk.Frame(card, bg="white")
        top.pack(fill="x")
        
        tk.Label(top, text=data["name"], font=("Arial", 11, "bold"), bg="white").pack(side="left")
        
        status_frame = tk.Frame(top, bg="white")
        status_frame.pack(side="right")
        
        if data["status"] != "Returned":
            tk.Button(status_frame, text="↩ Return", relief="flat", bg="#E3F2FD", fg="#1976D2", 
                      font=("Arial", 8, "bold"), cursor="hand2", padx=5,
                      command=lambda: ReturnPopup(self.winfo_toplevel(), data)
                      ).pack(side="right", padx=5)
        else:
            tk.Label(status_frame, text="✓", fg=COLORS["success"], bg="white", font=("Arial", 10, "bold")).pack(side="right", padx=10)
        
        tk.Label(status_frame, text=data["status"], fg=data["col"], bg="white", font=("Arial", 9, "bold")).pack(side="right")

        tk.Label(card, text=f"Items: {data['items']}", fg=COLORS["text_light"], bg="white", font=("Arial", 9)).pack(anchor="w")
        ttk.Separator(card, orient="horizontal").pack(fill="x", pady=(10, 0))

    # ==========================================
    # RIGHT PANEL: INVENTORY
    # ==========================================
    def build_right_panel(self, parent):
        right_container = tk.Frame(parent, bg=COLORS["bg_light"])
        right_container.grid(row=0, column=1, sticky="nsew")

        self.right_canvas = self.create_rounded_canvas(right_container)
        
        def update_right_bg(event):
            self.right_canvas.delete("bg")
            self.draw_rounded_rect(self.right_canvas, 0, 0, event.width, event.height, 25, "white")
            self.right_canvas.create_rectangle(0, 0, event.width, 60, fill=COLORS["primary_green"], outline="")
        
        self.right_canvas.bind("<Configure>", update_right_bg)

        tk.Label(self.right_canvas, text="☰  Available Equipment", font=("Arial", 12, "bold"), 
                 bg=COLORS["primary_green"], fg="white").place(x=20, y=18)

        # Scrollable List
        list_frame = tk.Frame(self.right_canvas, bg="white")
        list_frame.place(x=2, y=62, relwidth=0.98, relheight=0.9)

        self.inv_canvas = tk.Canvas(list_frame, bg="white", highlightthickness=0)
        scrollbar = ttk.Scrollbar(list_frame, orient="vertical", command=self.inv_canvas.yview)
        
        self.category_container = tk.Frame(self.inv_canvas, bg="white", padx=10, pady=10)

        self.category_container.bind(
            "<Configure>",
            lambda e: self.inv_canvas.configure(scrollregion=self.inv_canvas.bbox("all"))
        )
        
        self.inv_canvas.create_window((0, 0), window=self.category_container, anchor="nw", tags="window")
        self.inv_canvas.configure(yscrollcommand=scrollbar.set)

        self.inv_canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        self.inv_canvas.bind("<Configure>", lambda e: self.inv_canvas.itemconfig("window", width=e.width))

        # --- REAL DATABASE DATA (Inventory) ---
        try:
            db_equip = get_all_equipment()
        except:
            db_equip = []

        inventory_data = {}
        if db_equip:
            for item in db_equip:
                cat = item.get('category', 'Uncategorized')
                if cat not in inventory_data:
                    inventory_data[cat] = []
                
                inventory_data[cat].append({
                    "id": item.get('equipment_id'),
                    "name": item.get('name'),
                    "qty": item.get('quantity'),
                    "status": item.get('condition', 'Available') 
                })
        
        for cat_name, items in inventory_data.items():
            self.create_accordion_category(self.category_container, cat_name, items)
            
        if not inventory_data:
             tk.Label(self.category_container, text="No inventory found in database.", bg="white", fg="#999").pack(pady=20)

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

        if items:
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
        if item["status"] == "Broken": s_color = COLORS["broken"]
        if item["status"] == "Out of Stock": s_color = COLORS["outofstock"]

        tk.Label(row, text=item["status"], width=12, fg=s_color, bg="#F9F9F9", font=("Arial", 8, "bold"), anchor="w").pack(side="left")