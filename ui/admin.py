import tkinter as tk
from tkinter import messagebox, ttk

from config import COLORS


def center_window(win, width, height):
    sw = win.winfo_screenwidth()
    sh = win.winfo_screenheight()
    x = (sw - width) // 2
    y = (sh - height) // 2
    win.geometry(f"{width}x{height}+{x}+{y}")


class AdminPanel(tk.Toplevel):
    def __init__(self, parent, db, state, center_panel):
        super().__init__(parent)
        self.db = db
        self.state = state
        self.center_panel = center_panel
        self.selected_id = None
        self.configure(bg=COLORS["root_bg"])
        self.resizable(False, False)
        center_window(self, 860, 580)
        self.grab_set()
        self._build()
        self.show_tab("menu")

    def _build(self):
        title = tk.Frame(self, bg=COLORS["title_bar"], height=34)
        title.pack(fill=tk.X)
        title.pack_propagate(False)
        tk.Label(title, text="⚙️ Admin Panel", bg=COLORS["title_bar"], fg=COLORS["white"], font=("Helvetica", 11, "bold")).pack(side=tk.LEFT, padx=10)
        tk.Button(title, text="✕ Close", bg=COLORS["title_bar"], fg=COLORS["white"], relief=tk.FLAT, command=self.destroy).pack(side=tk.RIGHT, padx=8)

        tab_row = tk.Frame(self, bg=COLORS["root_bg"])
        tab_row.pack(fill=tk.X, padx=10, pady=(8, 0))
        self.menu_tab_btn = tk.Button(tab_row, text="📋 Menu Items", command=lambda: self.show_tab("menu"), relief=tk.FLAT)
        self.sales_tab_btn = tk.Button(tab_row, text="📊 Sales Report", command=lambda: self.show_tab("sales"), relief=tk.FLAT)
        self.menu_tab_btn.pack(side=tk.LEFT, padx=(0, 4))
        self.sales_tab_btn.pack(side=tk.LEFT)

        self.menu_frame = tk.Frame(self, bg=COLORS["root_bg"])
        self.sales_frame = tk.Frame(self, bg=COLORS["root_bg"])
        self._build_menu_tab()
        self._build_sales_tab()

    def show_tab(self, tab):
        self.menu_frame.pack_forget()
        self.sales_frame.pack_forget()
        active = {"bg": COLORS["accent"], "fg": COLORS["white"]}
        inactive = {"bg": COLORS["size_btn_inactive"], "fg": COLORS["text_secondary"]}
        if tab == "menu":
            self.menu_tab_btn.configure(**active)
            self.sales_tab_btn.configure(**inactive)
            self.menu_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
            self.load_menu_items()
        else:
            self.sales_tab_btn.configure(**active)
            self.menu_tab_btn.configure(**inactive)
            self.sales_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
            self.load_sales()

    def _build_menu_tab(self):
        top = tk.Frame(self.menu_frame, bg=COLORS["root_bg"])
        top.pack(fill=tk.X, pady=(0, 8))
        tk.Label(top, text="Menu Items", bg=COLORS["root_bg"], fg=COLORS["left_bg"], font=("Helvetica", 13, "bold")).pack(side=tk.LEFT)
        tk.Button(top, text="+ Add New Item", bg=COLORS["accent"], fg=COLORS["white"], relief=tk.FLAT, command=self.open_add_item).pack(side=tk.RIGHT)

        columns = ("id", "name", "category", "ps", "pm", "pl", "pf", "sizes", "status")
        self.tree = ttk.Treeview(self.menu_frame, columns=columns, show="headings", height=16)
        headers = ["#", "Name", "Category", "S Price", "M Price", "L Price", "Fixed Price", "Sizes", "Status"]
        widths = [30, 160, 110, 70, 70, 70, 80, 50, 70]
        for col, text, width in zip(columns, headers, widths):
            self.tree.heading(col, text=text)
            self.tree.column(col, width=width, anchor="center")
        self.tree.pack(fill=tk.BOTH, expand=True)
        self.tree.bind("<<TreeviewSelect>>", self.on_select)

        btns = tk.Frame(self.menu_frame, bg=COLORS["root_bg"])
        btns.pack(fill=tk.X, pady=8)
        self.edit_btn = tk.Button(btns, text="✏️ Edit Selected", state=tk.DISABLED, command=self.edit_selected, relief=tk.FLAT, bg=COLORS["accent_light"])
        self.delete_btn = tk.Button(btns, text="🗑 Delete Selected", state=tk.DISABLED, command=self.delete_selected, relief=tk.FLAT, bg=COLORS["danger_light"], fg=COLORS["danger"])
        self.edit_btn.pack(side=tk.LEFT, padx=(0, 6))
        self.delete_btn.pack(side=tk.LEFT)

    def _build_sales_tab(self):
        cards = tk.Frame(self.sales_frame, bg=COLORS["root_bg"])
        cards.pack(fill=tk.X, pady=(0, 8))
        self.card_sales = self._summary_card(cards, "Today's Sales")
        self.card_orders = self._summary_card(cards, "Total Orders Today")
        self.card_top = self._summary_card(cards, "Top Selling Item")
        self.card_sales.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 6))
        self.card_orders.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=6)
        self.card_top.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(6, 0))

        columns = ("id", "ts", "cashier", "type", "payment", "total")
        self.sales_tree = ttk.Treeview(self.sales_frame, columns=columns, show="headings", height=16)
        for col, text, width in [
            ("id", "Order #", 60),
            ("ts", "Date & Time", 150),
            ("cashier", "Cashier", 80),
            ("type", "Type", 80),
            ("payment", "Payment", 80),
            ("total", "Total", 80),
        ]:
            self.sales_tree.heading(col, text=text)
            self.sales_tree.column(col, width=width, anchor="center")
        self.sales_tree.pack(fill=tk.BOTH, expand=True)
        self.sales_tree.bind("<Double-1>", self.open_sales_detail)

    def _summary_card(self, parent, title):
        card = tk.Frame(parent, bg=COLORS["white"], padx=10, pady=8, highlightbackground=COLORS["divider"], highlightthickness=1)
        tk.Frame(card, bg=COLORS["accent"], height=3).pack(fill=tk.X, side=tk.TOP)
        tk.Label(card, text=title, bg=COLORS["white"], fg=COLORS["text_secondary"], font=("Helvetica", 10)).pack(anchor="w", pady=(6, 2))
        value = tk.Label(card, text="", bg=COLORS["white"], fg=COLORS["left_bg"], font=("Helvetica", 13, "bold"))
        value.pack(anchor="w")
        card.value_label = value
        return card

    def load_menu_items(self):
        self.selected_id = None
        self.edit_btn.configure(state=tk.DISABLED)
        self.delete_btn.configure(state=tk.DISABLED)
        for row in self.tree.get_children():
            self.tree.delete(row)
        for item in self.db.get_all_menu_items():
            has_sizes = item["has_sizes"] == 1
            self.tree.insert(
                "",
                "end",
                values=(
                    item["id"],
                    item["name"],
                    item["category"],
                    f'₱{item["price_small"]:.2f}' if has_sizes else "",
                    f'₱{item["price_medium"]:.2f}' if has_sizes else "",
                    f'₱{item["price_large"]:.2f}' if has_sizes else "",
                    "" if has_sizes else f'₱{item["price_fixed"]:.2f}',
                    "✅ Yes" if has_sizes else "❌ No",
                    "Available" if item["available"] == 1 else "Unavailable",
                ),
            )

    def load_sales(self):
        summary = self.db.sales_summary_today()
        self.card_sales.value_label.configure(text=f"₱ {summary['sales']:.2f}")
        self.card_orders.value_label.configure(text=f"{summary['orders']} orders")
        self.card_top.value_label.configure(text=summary["top_item"])
        for row in self.sales_tree.get_children():
            self.sales_tree.delete(row)
        for order in self.db.get_recent_orders(100):
            self.sales_tree.insert(
                "",
                "end",
                values=(
                    order["id"],
                    order["timestamp"],
                    order["cashier"],
                    order["order_type"],
                    order["payment_method"],
                    f'₱{order["total"]:.2f}',
                ),
            )

    def on_select(self, _event):
        selected = self.tree.selection()
        if not selected:
            return
        self.selected_id = int(self.tree.item(selected[0], "values")[0])
        self.edit_btn.configure(state=tk.NORMAL)
        self.delete_btn.configure(state=tk.NORMAL)

    def open_add_item(self):
        AddItemForm(self, self.db, self.load_menu_items, self.center_panel)

    def edit_selected(self):
        if self.selected_id is None:
            return
        item = next((entry for entry in self.db.get_all_menu_items() if entry["id"] == self.selected_id), None)
        if item:
            AddItemForm(self, self.db, self.load_menu_items, self.center_panel, item=item)

    def delete_selected(self):
        if self.selected_id is None:
            return
        if not messagebox.askyesno("Delete item", "Delete selected item?"):
            return
        if self.db.delete_menu_item(self.selected_id):
            self.load_menu_items()
            self.center_panel.load_category(self.center_panel.state.selected_category)

    def open_sales_detail(self, _event):
        selected = self.sales_tree.selection()
        if not selected:
            return
        order_id = int(self.sales_tree.item(selected[0], "values")[0])
        OrderDetailWindow(self, self.db, order_id)


class AddItemForm(tk.Toplevel):
    def __init__(self, parent, db, callback, center_panel, item=None):
        super().__init__(parent)
        self.db = db
        self.callback = callback
        self.center_panel = center_panel
        self.item = item
        self.has_sizes = tk.IntVar(value=1 if item and item["has_sizes"] else 0)
        self.available = tk.IntVar(value=1 if not item else int(item["available"]))
        self.errors = {}
        self.configure(bg=COLORS["white"])
        self.resizable(False, False)
        center_window(self, 400, 480)
        self.grab_set()
        self._build()
        self.toggle_size_fields()

    def _build(self):
        title_text = "✏️ Edit Item" if self.item else "➕ Add New Item"
        title = tk.Frame(self, bg=COLORS["title_bar"], height=34)
        title.pack(fill=tk.X)
        title.pack_propagate(False)
        tk.Label(title, text=title_text, bg=COLORS["title_bar"], fg=COLORS["white"], font=("Helvetica", 11, "bold")).pack(side=tk.LEFT, padx=10)

        form = tk.Frame(self, bg=COLORS["white"], padx=14, pady=10)
        form.pack(fill=tk.BOTH, expand=True)
        self.name_entry = self._entry_row(form, "Item Name:", self.item["name"] if self.item else "")
        self.category_combo = self._combo_row(form, "Category:", ["Hot Drinks", "Cold Drinks", "Snacks", "Desserts", "Meals"])
        if self.item:
            self.category_combo.set(self.item["category"])
        tk.Checkbutton(
            form,
            text="This item has Small / Medium / Large sizes",
            variable=self.has_sizes,
            command=self.toggle_size_fields,
            bg=COLORS["white"],
        ).pack(anchor="w", pady=(6, 8))

        self.size_frame = tk.Frame(form, bg=COLORS["white"])
        self.ps_entry = self._entry_row(self.size_frame, "Small (S) Price: ₱", "" if not self.item else str(self.item["price_small"]))
        self.pm_entry = self._entry_row(self.size_frame, "Medium (M) Price: ₱", "" if not self.item else str(self.item["price_medium"]))
        self.pl_entry = self._entry_row(self.size_frame, "Large (L) Price: ₱", "" if not self.item else str(self.item["price_large"]))

        self.fixed_frame = tk.Frame(form, bg=COLORS["white"])
        self.pf_entry = self._entry_row(self.fixed_frame, "Price: ₱", "" if not self.item else str(self.item["price_fixed"]))

        tk.Checkbutton(form, text="Available", variable=self.available, bg=COLORS["white"]).pack(anchor="w", pady=(8, 0))
        self.error_label = tk.Label(form, text="", bg=COLORS["white"], fg=COLORS["danger"], font=("Helvetica", 9))
        self.error_label.pack(anchor="w", pady=(6, 0))

        actions = tk.Frame(form, bg=COLORS["white"])
        actions.pack(fill=tk.X, pady=(10, 0))
        tk.Button(actions, text="💾 Save Item", command=self.save, bg=COLORS["accent"], fg=COLORS["white"], relief=tk.FLAT).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 4))
        tk.Button(actions, text="Cancel", command=self.destroy, bg="#F5F5F5", fg=COLORS["text_primary"], relief=tk.FLAT).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(4, 0))

    def _entry_row(self, parent, label, value):
        tk.Label(parent, text=label, bg=COLORS["white"], fg=COLORS["text_primary"], font=("Helvetica", 10, "bold")).pack(anchor="w")
        entry = ttk.Entry(parent)
        entry.pack(fill=tk.X, pady=(2, 6))
        if value != "":
            entry.insert(0, value)
        return entry

    def _combo_row(self, parent, label, values):
        tk.Label(parent, text=label, bg=COLORS["white"], fg=COLORS["text_primary"], font=("Helvetica", 10, "bold")).pack(anchor="w")
        combo = ttk.Combobox(parent, values=values, state="readonly")
        combo.pack(fill=tk.X, pady=(2, 6))
        return combo

    def toggle_size_fields(self):
        self.size_frame.pack_forget()
        self.fixed_frame.pack_forget()
        if self.has_sizes.get() == 1:
            self.size_frame.pack(fill=tk.X)
        else:
            self.fixed_frame.pack(fill=tk.X)

    def save(self):
        name = self.name_entry.get().strip()
        category = self.category_combo.get().strip()
        has_sizes = self.has_sizes.get()
        if not name:
            self.error_label.configure(text="Name is required.")
            return
        if not category:
            self.error_label.configure(text="Category is required.")
            return
        payload = {
            "name": name,
            "category": category,
            "has_sizes": has_sizes,
            "price_small": 0.0,
            "price_medium": 0.0,
            "price_large": 0.0,
            "price_fixed": 0.0,
            "available": self.available.get(),
        }
        try:
            if has_sizes == 1:
                ps = float(self.ps_entry.get())
                pm = float(self.pm_entry.get())
                pl = float(self.pl_entry.get())
                if min(ps, pm, pl) <= 0:
                    self.error_label.configure(text="Size prices must be positive.")
                    return
                if not (ps <= pm <= pl):
                    self.error_label.configure(text="Require Small <= Medium <= Large.")
                    return
                payload["price_small"] = ps
                payload["price_medium"] = pm
                payload["price_large"] = pl
            else:
                pf = float(self.pf_entry.get())
                if pf <= 0:
                    self.error_label.configure(text="Fixed price must be positive.")
                    return
                payload["price_fixed"] = pf
        except ValueError:
            self.error_label.configure(text="Prices must be valid numbers.")
            return

        ok = self.db.update_menu_item(self.item["id"], payload) if self.item else self.db.add_menu_item(payload)
        if not ok:
            self.error_label.configure(text="Failed to save item.")
            return
        self.callback()
        self.center_panel.load_category(self.center_panel.state.selected_category)
        self.destroy()


class OrderDetailWindow(tk.Toplevel):
    def __init__(self, parent, db, order_id):
        super().__init__(parent)
        self.db = db
        self.order_id = order_id
        self.configure(bg=COLORS["white"])
        self.resizable(False, False)
        center_window(self, 520, 360)
        self.grab_set()
        self._build()

    def _build(self):
        tk.Label(self, text=f"Order #{self.order_id} Details", bg=COLORS["white"], fg=COLORS["left_bg"], font=("Helvetica", 12, "bold")).pack(anchor="w", padx=12, pady=(12, 6))
        columns = ("name", "size", "qty", "price")
        tree = ttk.Treeview(self, columns=columns, show="headings", height=12)
        for col, text, width in [("name", "Item", 220), ("size", "Size", 80), ("qty", "Qty", 60), ("price", "Total", 100)]:
            tree.heading(col, text=text)
            tree.column(col, width=width, anchor="center")
        tree.pack(fill=tk.BOTH, expand=True, padx=12, pady=(0, 12))
        for item in self.db.get_order_items(self.order_id):
            tree.insert("", "end", values=(item["item_name"], item["size"], item["quantity"], f'₱{item["total_price"]:.2f}'))
