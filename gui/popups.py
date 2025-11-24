# gui/popups.py
import tkinter as tk
from tkinter import messagebox
from utils.colors import COLORS

class AddItemPopup:
    def __init__(self, parent_root):
        self.top = tk.Toplevel(parent_root)
        self.top.title("Add Equipment")
        self.top.geometry("400x500")
        self.top.configure(bg="white")
        self.build_ui()

    def build_ui(self):
        tk.Label(self.top, text="Add New Equipment", font=("Arial", 16, "bold"), 
                 bg="white", fg=COLORS["primary_green"]).pack(pady=20)

        # Helper for entries
        def create_entry(label_text):
            frame = tk.Frame(self.top, bg="white", padx=20, pady=5)
            frame.pack(fill="x")
            tk.Label(frame, text=label_text, bg="white", font=("Arial", 10, "bold")).pack(anchor="w")
            entry = tk.Entry(frame, relief="solid", bd=1)
            entry.pack(fill="x", pady=5, ipady=3)
            return entry

        self.name_entry = create_entry("Equipment Name")
        self.id_entry = create_entry("Equipment ID")
        self.cat_entry = create_entry("Category")
        self.qty_entry = create_entry("Quantity")

        # Buttons
        btn_frame = tk.Frame(self.top, bg="white", pady=20)
        btn_frame.pack()

        tk.Button(btn_frame, text="Save Item", bg=COLORS["primary_green"], fg="white", 
                  width=15, relief="flat", pady=5, 
                  command=self.save_item).pack(side="left", padx=5)

        tk.Button(btn_frame, text="Cancel", bg="#e0e0e0", fg="#333", 
                  width=10, relief="flat", pady=5, command=self.top.destroy).pack(side="left", padx=5)

    def save_item(self):
        # This is where your group mates will add the Database INSERT code
        messagebox.showinfo("Success", "Item Added (Simulated)")
        self.top.destroy()