# gui/dashboard_page.py
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from utils.colors import COLORS
from gui.popups import BorrowPopup  # Quick Access Popup

# Clean, single-file DashboardPage implementation.
# Version A: same structure as your original but cleaned, fixed, comments added.

class DashboardPage(tk.Frame):
    def __init__(self, parent, controller):
        """
        parent: tk container
        controller: application controller that exposes navigation methods:
            - controller.show_dashboard()
            - controller.show_borrow_page()
            etc.
        """
        super().__init__(parent, bg=COLORS["bg_light"])
        self.controller = controller
        self.build_ui()

    # -----------------------
    # Build main UI structure
    # -----------------------
    def build_ui(self):
        # Top navigation bar
        nav_bar = tk.Frame(self, bg="white", height=60, padx=20)
        nav_bar.pack(side="top", fill="x", pady=(0, 2))
        nav_bar.pack_propagate(False)

        tk.Label(
            nav_bar,
            text="TRACKLAB",
            font=("Arial", 16, "bold"),
            fg=COLORS["primary_green"],
            bg="white"
        ).pack(side="left", pady=15)

        # Navigation buttons (right side)
        nav_items = ["Dashboard", "Equipment", "Borrow", "Reports"]
        for item in nav_items:
            if item == "Borrow":
                cmd = self.controller.show_borrow_page
            elif item == "Dashboard":
                cmd = self.controller.show_dashboard
            elif item == "Reports":
                cmd = self.controller.show_reports
            elif item == "Equipment":
                cmd = self.controller.show_equipment_page # <--- Link here
            else:
                cmd = lambda x=item: print(f"Clicked {x}")

            tk.Button(
                nav_bar,
                text=item,
                bg="white",
                fg="#555",
                relief="flat",
                font=("Arial", 10),
                command=cmd
            ).pack(side="right", padx=10, pady=15)

        # Main content container
        content_frame = tk.Frame(self, bg=COLORS["bg_light"], padx=20, pady=20)
        content_frame.pack(fill="both", expand=True)

        # Layout config: left takes more space
        content_frame.rowconfigure(0, weight=1)
        content_frame.columnconfigure(0, weight=3)  # left panel
        content_frame.columnconfigure(1, weight=2)  # right panel

        # Build left and right panels
        self.build_left_panel(content_frame)
        self.build_right_panel(content_frame)

    # -----------------------
    # Utility: Rounded canvas
    # -----------------------
    def create_rounded_canvas(self, parent):
        """Return a canvas sized to parent that can be drawn on."""
        canvas = tk.Canvas(parent, bg=COLORS["bg_light"], highlightthickness=0)
        canvas.pack(fill="both", expand=True)
        return canvas

    def draw_rounded_rect(self, canvas, x, y, w, h, radius=20, color="white"):
        """Draw a rounded-ish rectangle polygon on canvas (approximation)."""
        points = [
            x+radius, y,
            x+w-radius, y,
            x+w, y,
            x+w, y+radius,
            x+w, y+h-radius,
            x+w, y+h,
            x+w-radius, y+h,
            x+radius, y+h,
            x, y+h,
            x, y+h-radius,
            x, y+radius,
            x, y
        ]
        return canvas.create_polygon(points, fill=color, smooth=True)

    # -----------------------
    # Left panel: Active borrowers (scrollable)
    # -----------------------
    def build_left_panel(self, parent):
        left_container = tk.Frame(parent, bg=COLORS["bg_light"])
        left_container.grid(row=0, column=0, sticky="nsew", padx=(0, 20))

        # Canvas used to draw rounded bg and host content
        self.left_canvas = self.create_rounded_canvas(left_container)

        def update_left_bg(event):
            self.left_canvas.delete("bg")
            self.draw_rounded_rect(self.left_canvas, 0, 0, event.width, event.height, 25, "white")

        self.left_canvas.bind("<Configure>", update_left_bg)

        # Title
        tk.Label(
            self.left_canvas,
            text="Current Equipment Holders",
            font=("Arial", 14, "bold"),
            bg="white",
            fg=COLORS["text_dark"]
        ).place(x=20, y=20)

        # Scroll region frame inside canvas
        list_frame = tk.Frame(self.left_canvas, bg="white")
        # place to allow overlaying rounded background
        list_frame.place(x=5, y=60, relwidth=0.96, relheight=0.85)

        scroll_canvas = tk.Canvas(list_frame, bg="white", highlightthickness=0)
        scrollbar = ttk.Scrollbar(list_frame, orient="vertical", command=scroll_canvas.yview)

        self.borrower_scroll_content = tk.Frame(scroll_canvas, bg="white")
        self.borrower_scroll_content.bind(
            "<Configure>",
            lambda e: scroll_canvas.configure(scrollregion=scroll_canvas.bbox("all"))
        )

        # Put borrower content frame into the scroll canvas
        scroll_canvas.create_window((0, 0), window=self.borrower_scroll_content, anchor="nw", width=550)
        scroll_canvas.configure(yscrollcommand=scrollbar.set)

        # Pack canvas + scrollbar
        scroll_canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Keep width responsive
        scroll_canvas.bind("<Configure>", lambda e: scroll_canvas.itemconfig(scroll_canvas.find_all()[0], width=e.width))

        # --- Mock data for borrower cards (replace with DB later) ---
        borrowers = [
            {"id": 101, "name": "Khan", "items": "3x Beakers", "status": "Ongoing", "col": COLORS["ongoing"]},
            {"id": 102, "name": "Malapare", "items": "Microscope Kit", "status": "Returned", "col": COLORS["returned"]},
            {"id": 103, "name": "Cruz", "items": "Extension Cord", "status": "Overdue", "col": COLORS["overdue"]},
            {"id": 104, "name": "Santos", "items": "Safety Goggles", "status": "Ongoing", "col": COLORS["ongoing"]},
            {"id": 105, "name": "Reyes", "items": "Digital Scale", "status": "Returned", "col": COLORS["returned"]},
            {"id": 106, "name": "Dy", "items": "Flask Set", "status": "Ongoing", "col": COLORS["ongoing"]},
            {"id": 107, "name": "Lim", "items": "Test Tubes", "status": "Ongoing", "col": COLORS["ongoing"]},
            {"id": 108, "name": "Dizon", "items": "Lab Coat", "status": "Ongoing", "col": COLORS["ongoing"]},
            {"id": 109, "name": "Yap", "items": "Petri Dish", "status": "Returned", "col": COLORS["returned"]},
        ]

        for data in borrowers:
            self.create_borrower_card(data)

        # Quick Borrow button (opens modal)
        add_btn = tk.Button(
            self.left_canvas,
            text="+ Quick Borrow",
            bg=COLORS["primary_green"],
            fg="white",
            relief="flat",
            pady=10,
            font=("Arial", 10, "bold"),
            cursor="hand2",
            command=lambda: BorrowPopup(self.winfo_toplevel())
        )
        add_btn.place(relx=0.05, rely=0.92, relwidth=0.9)

    def create_borrower_card(self, data):
        """Create a single borrower card in the scroll content."""
        card = tk.Frame(self.borrower_scroll_content, bg="white")
        card.pack(fill="x", pady=5, padx=10)

        top = tk.Frame(card, bg="white")
        top.pack(fill="x")

        tk.Label(top, text=data["name"], font=("Arial", 11, "bold"), bg="white").pack(side="left")

        status_frame = tk.Frame(top, bg="white")
        status_frame.pack(side="right")

        tk.Button(
            status_frame,
            text="🗑",
            relief="flat",
            bg="white",
            fg="#999",
            cursor="hand2",
            command=lambda: card.destroy()
        ).pack(side="right", padx=5)

        tk.Label(
            status_frame,
            text=data["status"],
            fg=data["col"],
            bg="white",
            font=("Arial", 9, "bold")
        ).pack(side="right")

        tk.Label(card, text=f"Items: {data['items']}", fg=COLORS["text_light"], bg="white", font=("Arial", 9)).pack(anchor="w")
        ttk.Separator(card, orient="horizontal").pack(fill="x", pady=(10, 0))

    # -----------------------
    # Right Panel: Inventory accordion (scrollable)
    # -----------------------
    def build_right_panel(self, parent):
        right_container = tk.Frame(parent, bg=COLORS["bg_light"])
        right_container.grid(row=0, column=1, sticky="nsew")

        self.right_canvas = self.create_rounded_canvas(right_container)

        def update_right_bg(event):
            self.right_canvas.delete("bg")
            # draw rounded background
            self.draw_rounded_rect(self.right_canvas, 0, 0, event.width, event.height, 25, "white")
            # draw top green header band
            self.right_canvas.create_rectangle(0, 0, event.width, 60, fill=COLORS["primary_green"], outline="")

        self.right_canvas.bind("<Configure>", update_right_bg)

        # Header text placed on top band
        tk.Label(
            self.right_canvas,
            text="☰  Available Equipment",
            font=("Arial", 12, "bold"),
            bg=COLORS["primary_green"],
            fg="white"
        ).place(x=20, y=18)

        # Scrollable list area inside rounded canvas
        list_frame = tk.Frame(self.right_canvas, bg="white")
        list_frame.place(x=2, y=62, relwidth=0.98, relheight=0.9)

        self.inv_canvas = tk.Canvas(list_frame, bg="white", highlightthickness=0)
        scrollbar = ttk.Scrollbar(list_frame, orient="vertical", command=self.inv_canvas.yview)

        self.category_container = tk.Frame(self.inv_canvas, bg="white", padx=10, pady=10)
        self.category_container.bind(
            "<Configure>",
            lambda e: self.inv_canvas.configure(scrollregion=self.inv_canvas.bbox("all"))
        )

        # put category_container into inv_canvas
        self.inv_canvas.create_window((0, 0), window=self.category_container, anchor="nw", tags="window")
        self.inv_canvas.configure(yscrollcommand=scrollbar.set)

        self.inv_canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Keep inner width responsive
        self.inv_canvas.bind("<Configure>", lambda e: self.inv_canvas.itemconfig("window", width=e.width))

        # Mock inventory dataset (replace with DB later)
        inventory_data = {
            "Personal Protective Equip...": [
                {"id": 201, "name": "Safety Goggles", "qty": 30, "status": "Available"},
                {"id": 202, "name": "Lab Coats (L)", "qty": 5, "status": "Out of Stock"},
            ],
            "Glassware": [
                {"id": 301, "name": "Beaker 500ml", "qty": 12, "status": "Available"},
                {"id": 302, "name": "Test Tubes", "qty": 50, "status": "Available"},
                {"id": 303, "name": "Flask", "qty": 2, "status": "Broken"},
                {"id": 304, "name": "Petri Dish", "qty": 100, "status": "Available"},
            ],
            "Measurement Tools": [
                {"id": 401, "name": "Digital Scale", "qty": 4, "status": "Available"},
            ],
        }

        # Create categories accordion
        for cat_name, items in inventory_data.items():
            self.create_accordion_category(self.category_container, cat_name, items)

    def create_accordion_category(self, parent, cat_name, items):
        """
        Each category creates a toggle button row and a hidden content frame.
        Clicking toggles visibility (accordion behaviour).
        """
        wrapper = tk.Frame(parent, bg="white")
        wrapper.pack(fill="x", pady=2)

        content_frame = tk.Frame(wrapper, bg="#F9F9F9", padx=10, pady=5)

        def toggle():
            if content_frame.winfo_ismapped():
                content_frame.pack_forget()
                icon_lbl.config(text="▶")
            else:
                content_frame.pack(fill="x")
                icon_lbl.config(text="▼")
            # update scrollregion after toggle
            self.category_container.update_idletasks()
            self.inv_canvas.configure(scrollregion=self.inv_canvas.bbox("all"))

        btn_frame = tk.Frame(wrapper, bg="white", height=40, cursor="hand2")
        btn_frame.pack(fill="x")
        btn_frame.pack_propagate(False)
        # allow clicking anywhere on the row to toggle
        btn_frame.bind("<Button-1>", lambda e: toggle())

        icon_lbl = tk.Label(btn_frame, text="▶", bg="white", fg=COLORS["text_light"], font=("Arial", 10))
        icon_lbl.pack(side="left", padx=(5, 10))

        name_lbl = tk.Label(btn_frame, text=cat_name, bg="white", fg=COLORS["text_dark"], font=("Arial", 10, "bold"))
        name_lbl.pack(side="left")

        ttk.Separator(wrapper, orient="horizontal").pack(fill="x")

        # Header row inside accordion content
        if items:
            h_row = tk.Frame(content_frame, bg="#F9F9F9", pady=2)
            h_row.pack(fill="x")
            tk.Label(h_row, text="Item Name", width=20, anchor="w", font=("Arial", 9, "bold"), bg="#F9F9F9").pack(side="left")
            tk.Label(h_row, text="Qty", width=6, font=("Arial", 9, "bold"), bg="#F9F9F9").pack(side="left")
            tk.Label(h_row, text="Status", width=12, font=("Arial", 9, "bold"), bg="#F9F9F9").pack(side="left")

            for item in items:
                self.create_inventory_row(content_frame, item)

    def create_inventory_row(self, parent, item):
        """Single item row inside accordion content."""
        row = tk.Frame(parent, bg="#F9F9F9", pady=2)
        row.pack(fill="x")

        tk.Label(row, text=item["name"], width=20, anchor="w", bg="#F9F9F9", font=("Arial", 9)).pack(side="left")
        tk.Label(row, text=str(item["qty"]), width=6, bg="#F9F9F9", font=("Arial", 9)).pack(side="left")

        s_color = COLORS["success"]
        if item["status"] == "Broken":
            s_color = COLORS["broken"]
        if item["status"] == "Out of Stock":
            s_color = COLORS["outofstock"]

        tk.Label(row, text=item["status"], width=12, fg=s_color, bg="#F9F9F9", font=("Arial", 9, "bold"), anchor="w").pack(side="left")
