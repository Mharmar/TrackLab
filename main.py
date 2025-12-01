# main.py
import tkinter as tk
from gui.app import TrackLabApp

if __name__ == "__main__":
    root = tk.Tk()
    app = TrackLabApp(root)
    root.mainloop()     