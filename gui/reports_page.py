# gui/reports_page.py
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import csv
from datetime import datetime, timedelta
from utils.colors import COLORS
# FIX: Removed circular import here

from database.reports_db import (
    get_borrowing_history, get_damage_reports, 
    get_overdue_items, get_inventory_status,
    get_analytics_chart_data
)

class ReportsPage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg=COLORS["bg_light"])
        self.controller = controller
        self.current_data = []
        self.current_columns = []
        self.build_ui()
        self.generate_report()

    def build_ui(self):
        # --- NAV BAR ---
        nav_bar = tk.Frame(self, bg="white", height=60, padx=20)
        nav_bar.pack(side="top", fill="x", pady=(0, 2))

        # --- LOGO INTEGRATION ---
        if self.controller.logo_image:
            tk.Label(nav_bar, image=self.controller.logo_image, bg="white").pack(side="left", pady=10, padx=5)
        else:
            tk.Label(nav_bar, text="TRACKLAB", font=("Arial", 16, "bold"),
                     fg=COLORS["primary_green"], bg="white").pack(side="left", pady=15)
        # ------------------------

        # === FIXED NAVIGATION LOGIC ===
        nav_items = ["Dashboard", "Equipment", "Borrow", "Reports", "Profile"]
        for item in nav_items:
            if item == "Dashboard": cmd = self.controller.show_dashboard
            elif item == "Equipment": cmd = self.controller.show_equipment_page
            elif item == "Borrow": cmd = self.controller.show_borrow_page
            elif item == "Reports": cmd = None
            elif item == "Profile": cmd = self.controller.show_profile_page

            color = COLORS["primary_green"] if item == "Reports" else "#555"
            font_style = ("Arial", 10, "bold") if item == "Reports" else ("Arial", 10)

            tk.Button(nav_bar, text=item, bg="white", fg=color,
                      relief="flat", font=font_style, command=cmd
            ).pack(side="right", padx=10, pady=15)

        content = tk.Frame(self, bg=COLORS["bg_light"], padx=20, pady=20)
        content.pack(fill="both", expand=True)

        tk.Label(content, text="Reports & Analytics", font=("Arial", 22, "bold"),
                 bg=COLORS["bg_light"], fg=COLORS["text_dark"]).pack(anchor="w", pady=(0, 15))

        # 1. CONTROLS
        controls = tk.Frame(content, bg="white", padx=20, pady=20)
        controls.pack(fill="x", pady=(0, 15))
        
        tk.Label(controls, text="From:", bg="white", font=("Arial", 9, "bold")).pack(side="left")
        self.date_from = tk.Entry(controls, width=12, relief="solid", bd=1)
        self.date_from.pack(side="left", padx=5)
        start_def = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")
        self.date_from.insert(0, start_def)

        tk.Label(controls, text="To:", bg="white", font=("Arial", 9, "bold")).pack(side="left", padx=(10,0))
        self.date_to = tk.Entry(controls, width=12, relief="solid", bd=1)
        self.date_to.pack(side="left", padx=5)
        self.date_to.insert(0, datetime.now().strftime("%Y-%m-%d"))

        tk.Label(controls, text="Report Type:", bg="white", font=("Arial", 9, "bold")).pack(side="left", padx=(20,0))
        self.type_cb = ttk.Combobox(controls, state="readonly", width=20,
                                    values=["Borrowing History", "Damage Reports", "Overdue Items", "Current Inventory"])
        self.type_cb.current(0)
        self.type_cb.pack(side="left", padx=5)

        tk.Button(controls, text="Generate Report", bg=COLORS["primary_green"], fg="white",
                  font=("Arial", 10, "bold"), padx=15, pady=5, relief="flat", cursor="hand2",
                  command=self.generate_report).pack(side="left", padx=20)

        # 2. SPLIT VIEW (Chart & Table)
        split = tk.Frame(content, bg=COLORS["bg_light"])
        split.pack(fill="both", expand=True)
        split.columnconfigure(0, weight=1)
        split.columnconfigure(1, weight=1)

        chart_frame = tk.Frame(split, bg="white", padx=10, pady=10)
        chart_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 10))
        tk.Label(chart_frame, text="Activity Trends (Daily Usage)", font=("Arial", 12, "bold"), bg="white", fg="#555").pack(anchor="w")
        
        self.chart_canvas = tk.Canvas(chart_frame, bg="white", height=250, highlightthickness=0)
        self.chart_canvas.pack(fill="both", expand=True, pady=10)

        table_frame = tk.Frame(split, bg="white", padx=10, pady=10)
        table_frame.grid(row=0, column=1, sticky="nsew")
        
        t_head = tk.Frame(table_frame, bg="white")
        t_head.pack(fill="x", pady=(0, 10))
        self.table_title = tk.Label(t_head, text="Data Preview", font=("Arial", 12, "bold"), bg="white", fg="#555")
        self.table_title.pack(side="left")
        
        tk.Button(t_head, text="⬇ Export Excel (CSV)", bg="#4A90E2", fg="white", 
                  relief="flat", font=("Arial", 9, "bold"), cursor="hand2",
                  command=self.export_csv).pack(side="right")

        self.tree_frame = tk.Frame(table_frame, bg="white")
        self.tree_frame.pack(fill="both", expand=True)
        
        self.create_tree([]) 

    def create_tree(self, columns):
        for widget in self.tree_frame.winfo_children(): widget.destroy()
        
        if not columns:
            tk.Label(self.tree_frame, text="Select a report type and click Generate.", bg="white", fg="#999").pack(pady=50)
            return

        self.current_columns = columns
        scroll_y = ttk.Scrollbar(self.tree_frame)
        scroll_y.pack(side="right", fill="y")
        scroll_x = ttk.Scrollbar(self.tree_frame, orient="horizontal")
        scroll_x.pack(side="bottom", fill="x")

        self.tree = ttk.Treeview(self.tree_frame, columns=columns, show="headings",
                                 yscrollcommand=scroll_y.set, xscrollcommand=scroll_x.set)
        
        scroll_y.config(command=self.tree.yview)
        scroll_x.config(command=self.tree.xview)

        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=100, anchor="w")
        
        self.tree.pack(fill="both", expand=True)

    def generate_report(self):
        report_type = self.type_cb.get()
        start = self.date_from.get()
        end = self.date_to.get()

        self.draw_chart(start, end)
        self.current_data = []
        data = []
        
        if report_type == "Borrowing History":
            data = get_borrowing_history(start, end)
            cols = ["Item Name", "Borrower", "Date Borrowed", "Due Date", "Status"]
            db_keys = ["item_name", "borrower", "date_borrowed", "due_date", "status"]
            
        elif report_type == "Damage Reports":
            data = get_damage_reports(start, end)
            cols = ["Item Name", "Reported By", "Date Returned", "Severity", "Remarks"]
            db_keys = ["item_name", "reported_by", "date_returned", "severity", "remarks"]
            
        elif report_type == "Overdue Items":
            data = get_overdue_items()
            cols = ["Item Name", "Borrower", "Date Borrowed", "Due Date", "Days Overdue"]
            db_keys = ["item_name", "borrower", "date_borrowed", "due_date", "days_overdue"]
            
        elif report_type == "Current Inventory":
            data = get_inventory_status()
            cols = ["Code", "Name", "Category", "Quantity", "Status"]
            db_keys = ["code", "name", "category", "quantity", "status"]
        
        else:
            return

        self.table_title.config(text=f"{report_type} ({len(data)} Records)")
        self.create_tree(cols)
        
        if not data:
            pass 
        
        for row in data:
            values = [str(row.get(k, "")) for k in db_keys]
            self.tree.insert("", "end", values=values)
            self.current_data.append(values)

    def draw_chart(self, start, end):
        self.chart_canvas.delete("all")
        data = get_analytics_chart_data(start, end)
        
        if not data:
            self.chart_canvas.create_text(200, 100, text="No activity data for selected period.", fill="#999")
            return

        w, h, margin = 400, 200, 30
        counts = [d['count'] for d in data]
        max_val = max(counts) if counts else 1
        num_points = len(data)
        x_step = (w - 2 * margin) / max(1, num_points - 1)
        
        self.chart_canvas.create_line(margin, h-margin, w-margin, h-margin, fill="#999", width=2)
        self.chart_canvas.create_line(margin, h-margin, margin, margin, fill="#999", width=2)

        prev_x, prev_y = None, None
        
        for i, point in enumerate(data):
            x = margin + (i * x_step)
            y = (h - margin) - ((point['count'] / max_val) * (h - 2 * margin))
            
            if prev_x is not None:
                self.chart_canvas.create_line(prev_x, prev_y, x, y, fill=COLORS["primary_green"], width=2)
            
            self.chart_canvas.create_oval(x-3, y-3, x+3, y+3, fill=COLORS["primary_green"], outline="white")
            
            if num_points < 10 or i % 3 == 0:
                day_lbl = point['day'][5:]
                self.chart_canvas.create_text(x, h-margin+10, text=day_lbl, font=("Arial", 7), angle=45)
            
            self.chart_canvas.create_text(x, y-10, text=str(point['count']), font=("Arial", 8, "bold"), fill="#555")

            prev_x, prev_y = x, y

    def export_csv(self):
        if not self.current_data:
            messagebox.showwarning("Warning", "No data to export. Generate a report first.")
            return
            
        path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV Files", "*.csv")])
        if path:
            try:
                with open(path, mode="w", newline="", encoding="utf-8") as f:
                    writer = csv.writer(f)
                    writer.writerow(self.current_columns)
                    writer.writerows(self.current_data)
                messagebox.showinfo("Success", "Export successful!")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to export: {e}")