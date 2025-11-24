# utils/error_handler.py
from tkinter import messagebox

class ErrorHandler:
    @staticmethod
    def show_error(title, message):
        messagebox.showerror(title, message)

    @staticmethod
    def show_warning(title, message):
        messagebox.showwarning(title, message)

    @staticmethod
    def validate_quantity(input_qty, max_qty):
        """Returns True if valid, raises ValueError if not."""
        try:
            qty = int(input_qty)
            if qty <= 0:
                raise ValueError("Quantity must be at least 1.")
            if qty > max_qty:
                raise ValueError(f"Cannot borrow {qty}. Only {max_qty} available.")
            return True
        except ValueError as e:
            # Re-raise to let the GUI handle the specific message
            raise e
        