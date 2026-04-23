import tkinter as tk
import os
import sys

from config import APP, COLORS, FONTS
from database import Database
from ui.login import LoginWindow
from ui.main_layout import MainLayout


class AppState:
    def __init__(self):
        self.current_user = {}
        self.current_order = []
        self.selected_category = "Hot Drinks"
        self.discount_amount = 0.0
        self.order_type = "Dine-in"
        self.payment_method = "Cash"
        self.total = 0.0
        self.last_receipt_data = None


class POSApplication:
    def __init__(self, root):
        self.root = root
        self.db = Database(APP["db_file"])
        self.state = AppState()
        self.main_layout = None
        self._build_window()
        self.root.withdraw()
        self.root.after(100, self.show_login)

    def _build_window(self):
        self.root.title(f"☕ {APP['name']} — POS System")
        self.root.geometry(f'{APP["window_w"]}x{APP["window_h"]}')
        self.root.minsize(APP["window_w"], APP["window_h"])
        self.root.resizable(True, True)
        self.root.configure(bg=COLORS["root_bg"])
        icon_path = self._resource_path("images", "kofeeicon.ico")
        if os.path.exists(icon_path):
            try:
                self.root.iconbitmap(icon_path)
            except tk.TclError:
                pass

    def _resource_path(self, *parts):
        base_path = getattr(sys, "_MEIPASS", os.path.dirname(os.path.abspath(__file__)))
        return os.path.join(base_path, *parts)

    def show_login(self):
        LoginWindow(self.root, self.db, self.state, self.build_main_layout)

    def build_main_layout(self):
        if self.main_layout is not None:
            self.main_layout.destroy()
        self.main_layout = MainLayout(self.root, self.db, self.state)
        self.main_layout.pack(fill=tk.BOTH, expand=True)
        self.root.deiconify()
        self.root.state("zoomed")
        self.root.lift()
        self.root.focus_force()


def run():
    root = tk.Tk()
    app = POSApplication(root)
    root.mainloop()
    return app


if __name__ == "__main__":
    run()
