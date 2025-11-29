# gui/reports_page.py
import tkinter as tk
from tkinter import ttk, messagebox
from utils.colors import COLORS

class ReportsPage(tk.Frame):
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
                cmd = self.controller.show_equipment_page
            elif item == "Borrow":
                cmd = self.controller.show_borrow_page
            elif item == "Reports":
                cmd = None # Already here
            elif item == "Profile":
                cmd = self.controller.show_profile_page
            else:
                cmd = None

            # Active Styling
            color = COLORS["primary_green"] if item == "Reports" else "#555"
            font_style = ("Arial", 10, "bold") if item == "Reports" else ("Arial", 10)

            tk.Button(nav_bar, text=item, bg="white", fg=color,
                      relief="flat", font=font_style, command=cmd
            ).pack(side="right", padx=10, pady=15)

        # ... (Keep the rest of your Reports Page code) ...
        # COPY THE REST OF YOUR REPORTS PAGE CODE HERE (Main content, table, etc)
        # =================================================================
        # 2. MAIN CONTENT AREA
        # =================================================================
        self.rowconfigure(1, weight=1)
        self.columnconfigure(0, weight=1)

        content_frame = tk.Frame(self, bg=COLORS["bg_light"], padx=20, pady=20)
        content_frame.pack(fill="both", expand=True)

        # Header
        tk.Label(content_frame, text="Reports & Analytics", font=("Arial", 22, "bold"),
                 bg=COLORS["bg_light"], fg=COLORS["text_dark"]).pack(anchor="w", pady=(0, 15))

        # ---------------------------------------------------------
        # SECTION A: CONTROL PANEL (Date & Type)
        # ---------------------------------------------------------
        controls_card = tk.Frame(content_frame, bg="white", padx=20, pady=20)
        controls_card.pack(fill="x", pady=(0, 15))
        controls_card.config(highlightbackground="#E0E0E0", highlightthickness=1)

        controls_card.columnconfigure(0, weight=0) # Date
        controls_card.columnconfigure(1, weight=0) # Type
        controls_card.columnconfigure(2, weight=1) # Spacer
        controls_card.columnconfigure(3, weight=0) # Buttons

        # Date Range Picker
        tk.Label(controls_card, text="Date Range:", bg="white", font=("Arial", 9, "bold"), fg="#555").grid(row=0, column=0, sticky="w", padx=10)
        
        date_frame = tk.Frame(controls_card, bg="white")
        date_frame.grid(row=1, column=0, sticky="w", padx=10, pady=(5,0))
        
        self.date_from = ttk.Entry(date_frame, width=12)
        self.date_from.insert(0, "2025-01-01")
        self.date_from.pack(side="left")
        
        tk.Label(date_frame, text=" to ", bg="white").pack(side="left")
        
        self.date_to = ttk.Entry(date_frame, width=12)
        self.date_to.insert(0, "2025-12-31")
        self.date_to.pack(side="left")

        # Report Type Dropdown
        tk.Label(controls_card, text="Report Type:", bg="white", font=("Arial", 9, "bold"), fg="#555").grid(row=0, column=1, sticky="w", padx=20)
        
        report_types = ["Borrowing History", "Equipment Status", "Damage Reports", "Overdue Items"]
        self.report_cb = ttk.Combobox(controls_card, values=report_types, state="readonly", width=25)
        self.report_cb.current(0)
        self.report_cb.grid(row=1, column=1, sticky="w", padx=20, pady=(5,0))

        # Generate Button
        tk.Button(controls_card, text="Generate Report", bg=COLORS["primary_green"], fg="white",
                  font=("Arial", 10, "bold"), relief="flat", padx=20, pady=5,
                  command=self.generate_report).grid(row=1, column=3, sticky="e")

        # ---------------------------------------------------------
        # SECTION B: VISUALS & DATA (Split Layout)
        # ---------------------------------------------------------
        split_frame = tk.Frame(content_frame, bg=COLORS["bg_light"])
        split_frame.pack(fill="both", expand=True)
        split_frame.columnconfigure(0, weight=1) # Chart
        split_frame.columnconfigure(1, weight=1) # Table

        # --- LEFT: CHART AREA ---
        chart_card = tk.Frame(split_frame, bg="white", padx=20, pady=20)
        chart_card.grid(row=0, column=0, sticky="nsew", padx=(0, 10))
        chart_card.config(highlightbackground="#E0E0E0", highlightthickness=1)

        tk.Label(chart_card, text="Usage Trends (Visual)", font=("Arial", 12, "bold"), 
                 bg="white", fg=COLORS["primary_green"]).pack(anchor="w", pady=(0, 10))

        self.chart_canvas = tk.Canvas(chart_card, bg="white", height=200, highlightthickness=0)
        self.chart_canvas.pack(fill="both", expand=True)
        self.draw_mock_chart()

        # --- RIGHT: DAMAGE / DATA TABLE ---
        table_card = tk.Frame(split_frame, bg="white", padx=20, pady=20)
        table_card.grid(row=0, column=1, sticky="nsew", padx=(10, 0))
        table_card.config(highlightbackground="#E0E0E0", highlightthickness=1)

        header_row = tk.Frame(table_card, bg="white")
        header_row.pack(fill="x", pady=(0, 10))
        
        tk.Label(header_row, text="Damage / Status Tracking", font=("Arial", 12, "bold"), 
                 bg="white", fg=COLORS["primary_green"]).pack(side="left")
        
        tk.Button(header_row, text="+ Add Damage Report", bg="#FF9800", fg="white",
                  relief="flat", font=("Arial", 8, "bold"), padx=10,
                  command=lambda: messagebox.showinfo("Info", "Open Damage Popup")).pack(side="right")

        columns = ("name", "date", "severity", "responsible", "status")
        tree_scroll = ttk.Scrollbar(table_card)
        tree_scroll.pack(side="right", fill="y")

        self.tree = ttk.Treeview(table_card, columns=columns, show="headings", yscrollcommand=tree_scroll.set)
        self.tree.pack(fill="both", expand=True)
        tree_scroll.config(command=self.tree.yview)

        self.tree.heading("name", text="Equipment Name")
        self.tree.heading("date", text="Date")
        self.tree.heading("severity", text="Severity")
        self.tree.heading("responsible", text="Responsible")
        self.tree.heading("status", text="Status")

        self.tree.column("name", width=120)
        self.tree.column("date", width=80)
        self.tree.column("severity", width=80)
        self.tree.column("responsible", width=100)
        self.tree.column("status", width=80)

        self.tree.insert("", "end", values=("Microscope A", "2025-02-10", "Minor", "John Doe", "Repair"))
        self.tree.insert("", "end", values=("Beaker 500ml", "2025-02-12", "Major", "Jane Smith", "Replace"))
        self.tree.insert("", "end", values=("Extension Cord", "2025-02-14", "Minor", "Mark Lee", "Repair"))

        # ---------------------------------------------------------
        # SECTION C: FOOTER ACTIONS
        # ---------------------------------------------------------
        footer = tk.Frame(content_frame, bg=COLORS["bg_light"], pady=15)
        footer.pack(fill="x")

        tk.Button(footer, text="Export PDF", bg="#E74C3C", fg="white", 
                  font=("Arial", 9, "bold"), relief="flat", padx=20, pady=8).pack(side="right", padx=(10, 0))
        
        tk.Button(footer, text="Export Excel", bg="#4A90E2", fg="white", 
                  font=("Arial", 9, "bold"), relief="flat", padx=20, pady=8).pack(side="right")

    # =================================================================
    # HELPER: DRAW MOCK CHART
    # =================================================================
    def draw_mock_chart(self):
        """Draws a simple line graph to simulate analytics"""
        self.chart_canvas.update()
        w = self.chart_canvas.winfo_width()
        h = self.chart_canvas.winfo_height()
        
        # Draw Axes
        self.chart_canvas.create_line(30, h-30, w-10, h-30, fill="#999", width=2) # X Axis
        self.chart_canvas.create_line(30, h-30, 30, 10, fill="#999", width=2)    # Y Axis

        # Mock Data Points
        points = [
            (30, h-30), (80, h-60), (130, h-40), (180, h-90), 
            (230, h-70), (280, h-120), (330, h-100), (380, h-150)
        ]
        
        # Draw Line & Dots
        for i in range(len(points)-1):
            x1, y1 = points[i]
            x2, y2 = points[i+1]
            self.chart_canvas.create_line(x1, y1, x2, y2, fill=COLORS["primary_green"], width=3, smooth=True)
            
        for x, y in points:
            self.chart_canvas.create_oval(x-3, y-3, x+3, y+3, fill=COLORS["primary_green"], outline="white")

    def generate_report(self):
        rtype = self.report_cb.get()
        messagebox.showinfo("Report Generated", f"Generating report for: {rtype}\nFrom {self.date_from.get()} to {self.date_to.get()}")