import hashlib
import tkinter as tk
from tkinter import ttk

from config import APP, COLORS


def center_window(win, width, height):
    sw = win.winfo_screenwidth()
    sh = win.winfo_screenheight()
    x = (sw - width) // 2
    y = (sh - height) // 2
    win.geometry(f"{width}x{height}+{x}+{y}")


class LoginWindow(tk.Toplevel):
    def __init__(self, parent, db, state, on_success):
        super().__init__(parent)
        self.db = db
        self.state = state
        self.on_success = on_success
        self.configure(bg=COLORS["left_bg"])
        self.overrideredirect(False)
        center_window(self, 400, 400)
        self.resizable(False, False)
        self.title("Login")
        self.grab_set()
        self.protocol("WM_DELETE_WINDOW", parent.destroy)
        self._build_ui()

    def _build_ui(self):
        container = tk.Frame(self, bg=COLORS["left_bg"], padx=30, pady=24)
        container.pack(fill=tk.BOTH, expand=True)

        tk.Label(
            container,
            text="☕",
            bg=COLORS["left_bg"],
            fg=COLORS["white"],
            font=("Helvetica", 34, "bold"),
        ).pack(pady=(8, 6))
        tk.Label(
            container,
            text=APP["name"],
            bg=COLORS["left_bg"],
            fg=COLORS["white"],
            font=("Helvetica", 14, "bold"),
        ).pack()
        tk.Label(
            container,
            text="Please log in to continue",
            bg=COLORS["left_bg"],
            fg=COLORS["left_text_dim"],
            font=("Helvetica", 10),
        ).pack(pady=(4, 12))
        ttk.Separator(container, orient=tk.HORIZONTAL).pack(fill=tk.X, pady=(0, 14))

        tk.Label(container, text="Username", bg=COLORS["left_bg"], fg=COLORS["white"]).pack(anchor="w")
        self.username_entry = ttk.Entry(container, font=("Helvetica", 11))
        self.username_entry.pack(fill=tk.X, pady=(5, 10))
        self.username_entry.focus_set()

        tk.Label(container, text="PIN", bg=COLORS["left_bg"], fg=COLORS["white"]).pack(anchor="w")
        self.pin_entry = ttk.Entry(container, show="*", font=("Helvetica", 11))
        self.pin_entry.pack(fill=tk.X, pady=(5, 14))
        self.pin_entry.bind("<Return>", lambda _e: self.validate_login())

        tk.Button(
            container,
            text="Login",
            bg=COLORS["accent"],
            fg=COLORS["white"],
            font=("Helvetica", 12, "bold"),
            relief=tk.FLAT,
            bd=0,
            pady=10,
            command=self.validate_login,
            cursor="hand2",
        ).pack(fill=tk.X)

        self.error_label = tk.Label(
            container,
            text="Invalid username or PIN",
            bg=COLORS["left_bg"],
            fg=COLORS["danger"],
            font=("Helvetica", 10),
        )
        self.error_label.pack(pady=(12, 0))
        self.error_label.pack_forget()

    def validate_login(self):
        username = self.username_entry.get().strip()
        pin = self.pin_entry.get().strip()
        if not username or not pin:
            self.error_label.pack(pady=(12, 0))
            return
        hashed = hashlib.sha256(pin.encode("utf-8")).hexdigest()
        user = self.db.validate_user(username, hashed)
        if user:
            self.state.current_user = {"name": user["username"], "role": user["role"]}
            self.destroy()
            self.on_success()
        else:
            self.error_label.pack(pady=(12, 0))
