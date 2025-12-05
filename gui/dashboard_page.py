import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk, ImageDraw, ImageOps 
import os
import random

from utils.colors import COLORS
from utils.session import Session
from utils.id_generator import generate_formatted_id
# FIX: Removed circular import here

from gui.popups import BorrowPopup, ReturnPopup
from database.borrow_db import get_active_borrows, delete_borrow_transaction 
from database.equipment_db import get_all_equipment

class DashboardPage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg=COLORS["bg_light"])
        self.controller = controller
        
        self.user = Session.get_user()
        self.user_role = self.user.get('role', 'Student') if self.user else 'Student'
        self.user_db_id = self.user.get('user_id', 0) if self.user else 0
        self.my_formatted_id = generate_formatted_id(self.user_role, self.user_db_id)
        
        self.image_refs = []
        
        self.build_ui()
        self.refresh_data()

    def build_ui(self):
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
            if item == "Dashboard": cmd = self.refresh_data
            elif item == "Equipment": cmd = self.controller.show_equipment_page
            elif item == "Borrow": cmd = self.controller.show_borrow_page 
            elif item == "Reports": cmd = self.controller.show_reports
            elif item == "Profile": cmd = self.controller.show_profile_page

            color = COLORS["primary_green"] if item == "Dashboard" else "#555"
            font_style = ("Arial", 10, "bold") if item == "Dashboard" else ("Arial", 10)
            tk.Button(nav_bar, text=item, bg="white", fg=color, relief="flat", font=font_style, command=cmd).pack(side="right", padx=10, pady=15)

        content = tk.Frame(self, bg=COLORS["bg_light"], padx=20, pady=20)
        content.pack(fill="both", expand=True)
        content.columnconfigure(0, weight=3); content.columnconfigure(1, weight=2); content.rowconfigure(0, weight=1)

        # LEFT PANEL
        left_panel = tk.Frame(content, bg=COLORS["bg_light"])
        left_panel.grid(row=0, column=0, sticky="nsew", padx=(0, 20))

        tk.Label(left_panel, text="Current Equipment Holders", font=("Arial", 14, "bold"), bg=COLORS["bg_light"], fg=COLORS["text_dark"]).pack(anchor="w", pady=(0, 10))
        
        self.left_canvas = tk.Canvas(left_panel, bg="white", highlightthickness=0)
        sb_left = ttk.Scrollbar(left_panel, orient="vertical", command=self.left_canvas.yview)
        self.borrower_frame = tk.Frame(self.left_canvas, bg="white", padx=10, pady=10)
        self.borrower_frame.bind("<Configure>", lambda e: self.left_canvas.configure(scrollregion=self.left_canvas.bbox("all")))
        self.left_canvas.create_window((0, 0), window=self.borrower_frame, anchor="nw", width=550)
        self.left_canvas.configure(yscrollcommand=sb_left.set)
        self.left_canvas.pack(side="left", fill="both", expand=True)
        sb_left.pack(side="right", fill="y")
        self.left_canvas.bind("<Configure>", lambda e: self.left_canvas.itemconfig(self.left_canvas.find_all()[0], width=e.width))

        tk.Button(left_panel, text="+ Quick Borrow", bg=COLORS["primary_green"], fg="white", relief="flat", pady=12, font=("Arial", 11, "bold"), command=self.open_quick_borrow).place(relx=0.05, rely=0.9, relwidth=0.9)

        # RIGHT PANEL
        right_panel = tk.Frame(content, bg=COLORS["bg_light"])
        right_panel.grid(row=0, column=1, sticky="nsew")

        r_head = tk.Frame(right_panel, bg=COLORS["primary_green"], padx=15, pady=10)
        r_head.pack(fill="x")
        tk.Label(r_head, text="☰  Available Equipment", font=("Arial", 12, "bold"), bg=COLORS["primary_green"], fg="white").pack(anchor="w")

        self.right_canvas = tk.Canvas(right_panel, bg="white", highlightthickness=0)
        sb_right = ttk.Scrollbar(right_panel, orient="vertical", command=self.right_canvas.yview)
        self.inv_frame = tk.Frame(self.right_canvas, bg="white", padx=10, pady=10)
        self.inv_frame.bind("<Configure>", lambda e: self.right_canvas.configure(scrollregion=self.inv_frame.bbox("all")))
        self.right_canvas.create_window((0, 0), window=self.inv_frame, anchor="nw", tags="window")
        self.right_canvas.configure(yscrollcommand=sb_right.set)
        self.right_canvas.pack(side="left", fill="both", expand=True)
        sb_right.pack(side="right", fill="y")
        self.right_canvas.bind("<Configure>", lambda e: self.right_canvas.itemconfig("window", width=e.width))

    def refresh_data(self):
        print(f"[Dashboard] Refreshing data...")
        self.image_refs.clear()
        for w in self.borrower_frame.winfo_children(): w.destroy()
        for w in self.inv_frame.winfo_children(): w.destroy()

        borrows = get_active_borrows(None)
        
        if not borrows:
            tk.Label(self.borrower_frame, text="No active borrows.", bg="white", fg="#999").pack(pady=20)
        else:
            for b in borrows:
                self.create_borrower_card(b)

        equipment = get_all_equipment()
        cats = {}
        for item in equipment:
            c = item.get('category', 'Others')
            if c not in cats: cats[c] = []
            cats[c].append(item)

        if not cats:
             tk.Label(self.inv_frame, text="Inventory empty.", bg="white", fg="#999").pack(pady=20)
        else:
            for c_name, items in cats.items():
                self.create_accordion(c_name, items)

    def create_borrower_card(self, data):
        card = tk.Frame(self.borrower_frame, bg="white")
        card.pack(fill="x", pady=0)
        
        container = tk.Frame(card, bg="white", padx=5, pady=8)
        container.pack(fill="x")

        # --- 1. AVATAR (LEFT) ---
        avatar_frame = tk.Frame(container, bg="white", width=60, height=60)
        avatar_frame.pack_propagate(False)
        avatar_frame.pack(side="left", padx=(0, 10), anchor="n")
        
        img_path = data.get('profile_image')
        user_name = data.get('full_name', 'Unknown')
        
        tk_img = self.get_circle_image(img_path, 50, user_name)
        self.image_refs.append(tk_img)
        
        lbl_img = tk.Label(avatar_frame, image=tk_img, bg="white")
        lbl_img.place(relx=0.5, rely=0.5, anchor="center")

        # --- 2. INFO & ACTIONS (RIGHT) ---
        info_frame = tk.Frame(container, bg="white")
        info_frame.pack(side="left", fill="x", expand=True)

        top = tk.Frame(info_frame, bg="white")
        top.pack(fill="x")
        
        borrower_id_str = data.get('student_id', '')
        is_me = (borrower_id_str == self.my_formatted_id)
        name_fg = COLORS["primary_green"] if is_me else "#333"
        
        tk.Label(top, text=user_name, font=("Arial", 11, "bold"), bg="white", fg=name_fg).pack(side="left")
        
        action_frame = tk.Frame(top, bg="white")
        action_frame.pack(side="right")

        if self.user_role == "Admin":
            tk.Button(action_frame, text="🗑 Void", bg="#FFEBEE", fg="#D32F2F", relief="flat", font=("Arial", 8, "bold"), padx=5, 
                      command=lambda d=data: self.void_borrow_admin(d)).pack(side="right", padx=(5,0))
            
            tk.Button(action_frame, text="↩ Return", bg="#E3F2FD", fg="#1976D2", relief="flat", font=("Arial", 8, "bold"), padx=8, 
                      command=lambda d=data: self.open_return(d)).pack(side="right")
        
        elif is_me:
            tk.Button(action_frame, text="↩ Return", bg="#E3F2FD", fg="#1976D2", relief="flat", font=("Arial", 8, "bold"), padx=8, 
                      command=lambda d=data: self.open_return(d)).pack(side="right")
        else:
            tk.Label(action_frame, text="🔒 In Use", bg="white", fg="#999", font=("Arial", 8)).pack(side="right", padx=5)


        tk.Label(info_frame, text=f"{data['student_id']} | {data['department']}", font=("Arial", 8), bg="white", fg="#777").pack(anchor="w")
        tk.Label(info_frame, text=data['item_name'], font=("Arial", 10), bg="white", fg="#444").pack(anchor="w", pady=(3,0))

        bot = tk.Frame(info_frame, bg="white")
        bot.pack(fill="x", pady=(2,0))
        
        due_time = data.get('due_time', 'N/A')
        tk.Label(bot, text=f"Due: {due_time}", font=("Arial", 9), bg="white", fg="#555").pack(side="left")
        
        status_text = data.get('status', 'Ongoing')
        status_col = COLORS["overdue"] if status_text == "Overdue" else COLORS["ongoing"]
        tk.Label(bot, text=f"● {status_text}", font=("Arial", 8, "bold"), bg="white", fg=status_col).pack(side="right")

        ttk.Separator(card, orient="horizontal").pack(fill="x")

    def void_borrow_admin(self, data):
        borrow_id = data['borrow_id']
        item_name = data['item_name']
        
        if messagebox.askyesno("CONFIRM ADMIN VOID", 
                               f"WARNING: You are about to DELETE the borrow record for '{item_name}' (ID: {borrow_id}) and RESTORE the item to inventory.\n\n"
                               "This action should ONLY be used if the record is void or the item is permanently lost/broken."
                               "\n\nContinue?"):
            from database.borrow_db import delete_borrow_transaction 
            if delete_borrow_transaction(borrow_id):
                messagebox.showinfo("Success", f"Borrow transaction {borrow_id} voided. Item '{item_name}' quantity restored.")
                self.refresh_data()
            else:
                messagebox.showerror("Error", "Failed to void transaction due to database error.")

    def get_circle_image(self, path, size, name_for_initials):
        try:
            if path and os.path.exists(path):
                img = Image.open(path)
                img = ImageOps.fit(img, (size, size), method=Image.Resampling.LANCZOS)
                mask = Image.new('L', (size, size), 0)
                draw = ImageDraw.Draw(mask)
                draw.ellipse((0, 0, size, size), fill=255)
                circular = Image.new('RGBA', (size, size), (0,0,0,0))
                circular.paste(img, (0, 0), mask)
                return ImageTk.PhotoImage(circular)
        except:
            pass

        colors = ["#FFCDD2", "#F8BBD0", "#E1BEE7", "#D1C4E9", "#C5CAE9", "#BBDEFB", "#B3E5FC", "#B2EBF2", "#B2DFDB", "#C8E6C9", "#DCEDC8", "#F0F4C3", "#FFF9C4", "#FFECB3", "#FFE0B2", "#FFCCBC"]
        bg_color = colors[len(name_for_initials) % len(colors)]
        base = Image.new('RGBA', (size, size), (0,0,0,0))
        draw = ImageDraw.Draw(base)
        draw.ellipse((0, 0, size, size), fill=bg_color)
        return ImageTk.PhotoImage(base)

    def create_accordion(self, title, items):
        wrapper = tk.Frame(self.inv_frame, bg="white", pady=2)
        wrapper.pack(fill="x")
        btn = tk.Frame(wrapper, bg="#F1F8E9", height=30, cursor="hand2")
        btn.pack(fill="x")
        btn.pack_propagate(False)
        tk.Label(btn, text="▼", bg="#F1F8E9", fg=COLORS["dark_green"], font=("Arial", 8)).pack(side="left", padx=10)
        tk.Label(btn, text=title, bg="#F1F8E9", fg=COLORS["dark_green"], font=("Arial", 10, "bold")).pack(side="left")
        content = tk.Frame(wrapper, bg="white", padx=10)
        content.pack(fill="x")
        def toggle(e):
            if content.winfo_ismapped(): content.pack_forget()
            else: content.pack(fill="x")
        btn.bind("<Button-1>", toggle)
        
        h = tk.Frame(content, bg="white", pady=5)
        h.pack(fill="x")
        tk.Label(h, text="Item Name", width=20, anchor="w", font=("Arial", 8, "bold"), bg="white", fg="#888").pack(side="left")
        tk.Label(h, text="Qty", width=5, anchor="center", font=("Arial", 8, "bold"), bg="white", fg="#888").pack(side="left")
        tk.Label(h, text="Status", width=12, anchor="w", font=("Arial", 8, "bold"), bg="white", fg="#888").pack(side="left", padx=(10,0))

        for item in items: self.create_item_row(content, item)

    def create_item_row(self, parent, item):
        row = tk.Frame(parent, bg="white", pady=2)
        row.pack(fill="x")
        tk.Label(row, text=item['name'], width=22, anchor="w", font=("Arial", 9), bg="white").pack(side="left")
        qty = item['quantity']
        qty_color = "black" if qty > 0 else "#999"
        tk.Label(row, text=str(qty), width=5, anchor="center", font=("Arial", 9, "bold"), bg="white", fg=qty_color).pack(side="left")
        cond = item.get('condition', 'Good')
        if cond == 'Broken': s_txt, s_col = "Broken", COLORS["broken"]
        elif qty <= 0: s_txt, s_col = "Out of Stock", COLORS["outofstock"]
        else: s_txt, s_col = "Good", COLORS["success"]
        tk.Label(row, text=s_txt, width=15, anchor="w", font=("Arial", 8, "bold"), bg="white", fg=s_col).pack(side="left", padx=(10,0))
        ttk.Separator(parent, orient="horizontal").pack(fill="x")

    def open_quick_borrow(self):
        BorrowPopup(self.winfo_toplevel(), callback=self.refresh_data)

    def open_return(self, data):
        p_data = {'id': data['borrow_id'], 'name': data['item_name'], 'borrower': data['full_name']}
        ReturnPopup(self.winfo_toplevel(), p_data, callback=self.refresh_data)