import tkinter as tk
from datetime import datetime
from tkinter import ttk

from config import APP, COLORS, FONTS


class LeftPanel(tk.Frame):
    def __init__(self, parent, db, state, center_panel, right_panel):
        super().__init__(parent, bg=COLORS["left_bg"], width=220)
        self.db = db
        self.state = state
        self.center_panel = center_panel
        self.right_panel = right_panel
        self.category_buttons = {}
        self.pack_propagate(False)
        self._build()
        self._update_clock()

    def _build(self):
        identity = tk.Frame(self, bg=COLORS["left_bg"], padx=14, pady=14)
        identity.pack(fill=tk.X)
        tk.Label(identity, text="☕", bg=COLORS["left_bg"], fg=COLORS["white"], font=("Helvetica", 20)).pack(anchor="w")
        tk.Label(identity, text=APP["name"], bg=COLORS["left_bg"], fg=COLORS["white"], font=FONTS["shop_name"]).pack(anchor="w")
        tk.Label(identity, text=APP["tagline"], bg=COLORS["left_bg"], fg=COLORS["left_text_dim"], font=FONTS["tagline"]).pack(anchor="w")
        ttk.Separator(self, orient=tk.HORIZONTAL).pack(fill=tk.X, padx=10, pady=(0, 8))

        nav_frame = tk.Frame(self, bg=COLORS["left_bg"])
        nav_frame.pack(fill=tk.X)

        categories = [
            ("☕", "Hot Drinks"),
            ("🧊", "Cold Drinks"),
            ("🥐", "Snacks"),
            ("🍰", "Desserts"),
            ("🍱", "Meals"),
        ]
        for icon, category in categories:
            button = tk.Button(
                nav_frame,
                text=f"{icon}  {category}",
                anchor="w",
                relief=tk.FLAT,
                padx=16,
                pady=12,
                cursor="hand2",
                font=FONTS["nav_btn"],
                bd=0,
                command=lambda value=category: self.select_category(value),
            )
            button.pack(fill=tk.X, padx=6, pady=1)
            self.category_buttons[category] = button

        self.select_category(self.state.selected_category)
        ttk.Separator(self, orient=tk.HORIZONTAL).pack(fill=tk.X, padx=10, pady=8)

        bottom_actions = tk.Frame(self, bg=COLORS["left_bg"])
        bottom_actions.pack(side=tk.BOTTOM, fill=tk.X, padx=6, pady=6)
        if self.state.current_user.get("role") == "admin":
            tk.Button(
                bottom_actions,
                text="⚙️ Admin Panel",
                anchor="w",
                relief=tk.FLAT,
                bd=0,
                bg=COLORS["left_btn_inactive"],
                fg=COLORS["left_text"],
                padx=12,
                pady=9,
                command=self.open_admin,
                cursor="hand2",
            ).pack(fill=tk.X, pady=2)

        tk.Button(
            bottom_actions,
            text="📋 Order History",
            anchor="w",
            relief=tk.FLAT,
            bd=0,
            bg=COLORS["left_btn_inactive"],
            fg=COLORS["left_text"],
            padx=12,
            pady=9,
            command=self.open_order_history,
            cursor="hand2",
        ).pack(fill=tk.X, pady=2)

        footer = tk.Frame(self, bg=COLORS["left_bg"], padx=12, pady=10)
        footer.pack(side=tk.BOTTOM, fill=tk.X)
        tk.Label(
            footer,
            text=f"👤 {self.state.current_user.get('name', 'Unknown')}",
            bg=COLORS["left_bg"],
            fg=COLORS["left_text_dim"],
            font=FONTS["small"],
        ).pack(anchor="w")
        self.clock_label = tk.Label(
            footer,
            bg=COLORS["left_bg"],
            fg=COLORS["left_text_dim"],
            font=FONTS["small"],
        )
        self.clock_label.pack(anchor="w")

    def select_category(self, name):
        self.state.selected_category = name
        for category, button in self.category_buttons.items():
            active = category == name
            button.configure(
                bg=COLORS["left_btn_active"] if active else COLORS["left_btn_inactive"],
                fg=COLORS["white"] if active else COLORS["left_text"],
            )
        self.center_panel.load_category(name)

    def _update_clock(self):
        now = datetime.now().strftime("%b %d %Y  %I:%M %p")
        self.clock_label.configure(text=now)
        self.after(30000, self._update_clock)

    def open_admin(self):
        from ui.admin import AdminPanel

        AdminPanel(self.winfo_toplevel(), self.db, self.state, self.center_panel)

    def open_order_history(self):
        from order_history import OrderHistory

        OrderHistory(self.winfo_toplevel(), self.db)
