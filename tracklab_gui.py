import tkinter as tk
from tkinter import ttk
from tkinter import messagebox

class TrackLabApp:
    def __init__(self, root):
        self.root = root
        self.root.title("TrackLab - Laboratory Equipment System")
        self.root.geometry("1000x700")
        
        # Color Palette from your Figma
        self.colors = {
            "primary_green": "#4CAF50",
            "dark_green": "#2E7D32",
            "bg_light": "#F5F5F5",
            "white": "#FFFFFF",
            "text_dark": "#333333",
            "text_light": "#757575",
            "danger": "#FF5252",
            "success": "#4CAF50"
        }

        self.container = tk.Frame(self.root, bg=self.colors["bg_light"])
        self.container.pack(fill="both", expand=True)

        self.show_landing_page()

    # ---------------------------
    # PAGE NAVIGATION (SWAP FRAME)
    # ---------------------------
    def clear_container(self):
        for widget in self.container.winfo_children():
            widget.destroy()

    # ---------------------------
    # PAGE 1 – LANDING PAGE
    # ---------------------------
    def show_landing_page(self):
        self.clear_container()
        
        landing_frame = tk.Frame(self.container, bg=self.colors["primary_green"])
        landing_frame.pack(fill="both", expand=True)

        center_frame = tk.Frame(landing_frame, bg=self.colors["primary_green"])
        center_frame.place(relx=0.5, rely=0.5, anchor="center")

        icon_label = tk.Label(center_frame, text="⚙️\n⏱️", 
                              font=("Segoe UI Emoji", 48), 
                              bg=self.colors["primary_green"], fg="white")
        icon_label.pack(pady=10)

        title = tk.Label(center_frame, text="TRACKLAB", 
                         font=("Arial", 48, "bold"), 
                         bg=self.colors["primary_green"], fg="white")
        title.pack()

        subtitle = tk.Label(
            center_frame,
            text="A system that records and tracks lab equipment usage.",
            font=("Arial", 12),
            bg=self.colors["primary_green"],
            fg="#E8F5E9")
        subtitle.pack(pady=10)

        # ➜ OPEN button → goes to dashboard page
        open_btn = tk.Button(
            center_frame, text="➜  Open", 
            font=("Arial", 14, "bold"),
            bg="#388E3C", fg="white",
            relief="flat", padx=30, pady=10,
            command=self.show_dashboard
        )
        open_btn.pack(pady=30)

        footer = tk.Label(
            landing_frame,
            text="About us   |   Contact: 09613989802",
            bg=self.colors["primary_green"],
            fg="#C8E6C9",
            font=("Arial", 9)
        )
        footer.pack(side="bottom", pady=20)

    # ---------------------------
    # PAGE 2 – DASHBOARD PAGE
    # ---------------------------
    def show_dashboard(self):
        self.clear_container()

        # --- TOP NAV BAR ---
        nav_bar = tk.Frame(self.container, bg="white", height=60, padx=20)
        nav_bar.pack(side="top", fill="x", pady=(0, 2))

        tk.Label(
            nav_bar, text="TRACKLAB",
            font=("Arial", 16, "bold"),
            fg=self.colors["primary_green"], bg="white"
        ).pack(side="left", pady=15)
        
        nav_items = ["Dashboard", "Equipment", "Borrow", "Reports"]
        for item in nav_items:
            tk.Button(
                nav_bar, text=item,
                bg="white", fg="#555", relief="flat",
                font=("Arial", 10)
            ).pack(side="right", padx=10, pady=15)

        # --- MAIN CONTENT ---
        content_frame = tk.Frame(self.container, bg=self.colors["bg_light"], padx=20, pady=20)
        content_frame.pack(fill="both", expand=True)

        content_frame.columnconfigure(0, weight=2)
        content_frame.columnconfigure(1, weight=1)

        # LEFT PANEL
        left_panel = tk.Frame(content_frame, bg="white", padx=15, pady=15)
        left_panel.grid(row=0, column=0, sticky="nsew", padx=(0, 20))

        lbl_browse = tk.Label(
            left_panel, text="Browsing the Items.", 
            font=("Arial", 14, "bold"), 
            bg="white", fg=self.colors["text_dark"]
        )
        lbl_browse.pack(anchor="w")

        borrow_data = [
            {"user": "Khan", "items": "Beakers, Flask tubes, etc...", "status": "Ongoing", "color": self.colors["danger"]},
            {"user": "Malapare", "items": "Measuring tubes, micro etc...", "status": "Returned", "color": self.colors["success"]},
            {"user": "Malapare", "items": "Extension cords, kits...", "status": "Ongoing", "color": self.colors["danger"]},
        ]

        # Borrower Cards
        for data in borrow_data:
            card = tk.Frame(left_panel, bg="white")
            card.pack(fill="x", pady=10)

            top_row = tk.Frame(card, bg="white")
            top_row.pack(fill="x")

            tk.Label(top_row, text=data["user"], font=("Arial", 11, "bold"), bg="white").pack(side="left")

            status_frame = tk.Frame(top_row, bg="white")
            status_frame.pack(side="right")

            tk.Button(status_frame, text="🗑", relief="flat", bg="white", fg="#999").pack(side="right", padx=5)
            tk.Label(status_frame, text=data["status"], fg=data["color"], bg="white", font=("Arial", 9)).pack(side="right")

            tk.Label(card, text=data["items"], fg=self.colors["text_light"], bg="white").pack(anchor="w")

            ttk.Separator(card, orient="horizontal").pack(fill="x", pady=(10, 0))

        add_btn = tk.Button(
            left_panel, text="+ Add New Equipment",
            bg=self.colors["primary_green"], fg="white",
            relief="flat", pady=8,
            command=self.open_add_item_window
        )
        add_btn.pack(side="bottom", fill="x", pady=10)

        # RIGHT PANEL
        right_panel = tk.Frame(content_frame, bg="white")
        right_panel.grid(row=0, column=1, sticky="nsew")

        header_block = tk.Frame(right_panel, bg=self.colors["primary_green"], pady=15, padx=15)
        header_block.pack(fill="x")

        tk.Label(
            header_block, text="☰  Available Equipment",
            font=("Arial", 12, "bold"), bg=self.colors["primary_green"], fg="white"
        ).pack(anchor="w")

        categories = [
            "Personal Protective Equip...",
            "Glassware",
            "Measurement Tools",
            "Specialized Apparatus",
            "Handling and Contain..."
        ]

        list_container = tk.Frame(right_panel, bg="white", padx=10, pady=10)
        list_container.pack(fill="both", expand=True)

        for cat in categories:
            ttk.Separator(list_container, orient="horizontal").pack(fill="x", pady=5)
            tk.Button(
                list_container, text=cat,
                bg="white", fg=self.colors["text_light"],
                anchor="w", relief="flat"
            ).pack(fill="x", pady=5)

        tk.Label(list_container, text="more...", fg=self.colors["text_light"], bg="white").pack(pady=10)

    # ---------------------------
    # ADD ITEM WINDOW (Popup)
    # ---------------------------
    def open_add_item_window(self):
        add_win = tk.Toplevel(self.root)
        add_win.title("Add Equipment")
        add_win.geometry("400x500")
        add_win.configure(bg="white")

        tk.Label(add_win, text="Add New Equipment", font=("Arial", 16, "bold"), 
                 bg="white", fg=self.colors["primary_green"]).pack(pady=20)

        def create_entry(label_text):
            frame = tk.Frame(add_win, bg="white", padx=20, pady=5)
            frame.pack(fill="x")
            tk.Label(frame, text=label_text, bg="white", font=("Arial", 10, "bold")).pack(anchor="w")
            entry = tk.Entry(frame, relief="solid", bd=1)
            entry.pack(fill="x", pady=5, ipady=3)
            return entry

        name_entry = create_entry("Equipment Name")
        id_entry = create_entry("Equipment ID")
        cat_entry = create_entry("Category")
        qty_entry = create_entry("Quantity")

        btn_frame = tk.Frame(add_win, bg="white", pady=20)
        btn_frame.pack()

        tk.Button(
            btn_frame, text="Save Item",
            bg=self.colors["primary_green"], fg="white",
            width=15, relief="flat", pady=5,
            command=lambda: [messagebox.showinfo("Success", "Item Added (Simulated)"), add_win.destroy()]
        ).pack(side="left", padx=5)

        tk.Button(
            btn_frame, text="Cancel",
            bg="#e0e0e0", fg="#333",
            width=10, relief="flat", pady=5,
            command=add_win.destroy
        ).pack(side="left", padx=5)


# --- MAIN ---
if __name__ == "__main__":
    root = tk.Tk()
    app = TrackLabApp(root)
    root.mainloop()
