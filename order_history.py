import tkinter as tk
from tkinter import ttk

from config import COLORS
from ui.admin import OrderDetailWindow


def center_window(win, width, height):
    sw = win.winfo_screenwidth()
    sh = win.winfo_screenheight()
    x = (sw - width) // 2
    y = (sh - height) // 2
    win.geometry(f"{width}x{height}+{x}+{y}")


class OrderHistory(tk.Toplevel):
    def __init__(self, parent, db):
        super().__init__(parent)
        self.db = db
        self.filter_var = tk.StringVar(value="Today")
        self.configure(bg=COLORS["white"])
        self.resizable(False, False)
        center_window(self, 860, 520)
        self.grab_set()
        self._build()
        self.reload_orders()

    def _build(self):
        top = tk.Frame(self, bg=COLORS["white"], padx=12, pady=10)
        top.pack(fill=tk.X)
        tk.Label(top, text="Show:", bg=COLORS["white"], fg=COLORS["text_primary"]).pack(side=tk.LEFT, padx=(0, 6))
        combo = ttk.Combobox(top, values=["Today", "This Week", "This Month", "All Time"], textvariable=self.filter_var, state="readonly", width=16)
        combo.pack(side=tk.LEFT)
        combo.bind("<<ComboboxSelected>>", lambda _e: self.reload_orders())
        tk.Button(top, text="🔄 Refresh", command=self.reload_orders, bg=COLORS["size_btn_inactive"], relief=tk.FLAT).pack(side=tk.LEFT, padx=8)

        columns = ("id", "ts", "cashier", "type", "payment", "items", "total")
        self.tree = ttk.Treeview(self, columns=columns, show="headings", height=20)
        for col, text, width in [
            ("id", "Order #", 60),
            ("ts", "Date & Time", 140),
            ("cashier", "Cashier", 80),
            ("type", "Type", 70),
            ("payment", "Payment", 80),
            ("items", "Items", 50),
            ("total", "Total", 80),
        ]:
            self.tree.heading(col, text=text)
            self.tree.column(col, width=width, anchor="center")
        self.tree.pack(fill=tk.BOTH, expand=True, padx=12, pady=(0, 12))
        self.tree.bind("<Double-1>", self.open_detail)

    def reload_orders(self):
        for row in self.tree.get_children():
            self.tree.delete(row)
        for order in self.db.get_filtered_orders(self.filter_var.get()):
            self.tree.insert(
                "",
                "end",
                values=(
                    order["id"],
                    order["timestamp"],
                    order["cashier"],
                    order["order_type"],
                    order["payment_method"],
                    order["item_count"],
                    f'₱{order["total"]:.2f}',
                ),
            )

    def open_detail(self, _event):
        selected = self.tree.selection()
        if not selected:
            return
        order_id = int(self.tree.item(selected[0], "values")[0])
        OrderDetailWindow(self, self.db, order_id)
