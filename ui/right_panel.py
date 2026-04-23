import tkinter as tk
from datetime import datetime
from tkinter import messagebox, ttk

from config import APP, COLORS, FONTS


class RightPanel(tk.Frame):
    def __init__(self, parent, db, state):
        super().__init__(parent, bg=COLORS["white"], width=300)
        self.db = db
        self.state = state
        self.order_type_var = tk.StringVar(value=self.state.order_type)
        self.payment_var = tk.StringVar(value=self.state.payment_method)
        self.cash_var = tk.StringVar(value="")
        self.change_var = tk.StringVar(value="₱ 0.00")
        self.subtotal_value = 0.0
        self.tax_value = 0.0
        self.pack_propagate(False)
        self._build()
        self.refresh_order()

    def _build(self):
        tk.Label(self, text="Current Order", bg=COLORS["white"], fg=COLORS["left_bg"], font=FONTS["section_hdr"]).pack(anchor="w", padx=12, pady=(12, 4))
        ttk.Separator(self, orient=tk.HORIZONTAL).pack(fill=tk.X, padx=10, pady=(0, 8))

        order_type = tk.Frame(self, bg=COLORS["white"])
        order_type.pack(fill=tk.X, padx=10, pady=(0, 8))
        self.dine_btn = self._toggle_button(order_type, "🪑 Dine-in", "Dine-in", self.on_order_type_change)
        self.takeout_btn = self._toggle_button(order_type, "🥡 Takeout", "Takeout", self.on_order_type_change)
        self.dine_btn.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 3))
        self.takeout_btn.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(3, 0))
        self._refresh_order_type_buttons()

        list_wrap = tk.Frame(self, bg=COLORS["white"])
        list_wrap.pack(fill=tk.BOTH, expand=True, padx=8)
        self.order_canvas = tk.Canvas(list_wrap, bg=COLORS["white"], highlightthickness=0, height=230)
        scroll = tk.Scrollbar(list_wrap, orient=tk.VERTICAL, command=self.order_canvas.yview)
        self.order_inner = tk.Frame(self.order_canvas, bg=COLORS["white"])
        self.order_inner.bind("<Configure>", lambda _e: self.order_canvas.configure(scrollregion=self.order_canvas.bbox("all")))
        self.order_window = self.order_canvas.create_window((0, 0), window=self.order_inner, anchor="nw")
        self.order_canvas.configure(yscrollcommand=scroll.set)
        self.order_canvas.bind("<Configure>", self._on_order_canvas_resize)
        self.order_canvas.bind("<MouseWheel>", self._on_order_mouse_wheel)
        self.order_canvas.bind("<Button-4>", lambda _e: self.order_canvas.yview_scroll(-1, "units"))
        self.order_canvas.bind("<Button-5>", lambda _e: self.order_canvas.yview_scroll(1, "units"))
        self.order_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scroll.pack(side=tk.RIGHT, fill=tk.Y)

        tk.Label(self, text="Payment Method", bg=COLORS["white"], fg=COLORS["text_secondary"], font=FONTS["small"]).pack(anchor="w", padx=12, pady=(6, 2))
        pay_row = tk.Frame(self, bg=COLORS["white"])
        pay_row.pack(fill=tk.X, padx=10, pady=(0, 6))
        self.cash_btn = self._toggle_button(pay_row, "💵 Cash", "Cash", self.on_payment_change)
        self.ewallet_btn = self._toggle_button(pay_row, "📱 E-Wallet", "E-Wallet", self.on_payment_change)
        self.card_btn = self._toggle_button(pay_row, "💳 Card", "Card", self.on_payment_change)
        self.cash_btn.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 2))
        self.ewallet_btn.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=2)
        self.card_btn.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(2, 0))

        self.cash_frame = tk.Frame(self, bg=COLORS["white"])
        self.cash_frame.pack(fill=tk.X, padx=12, pady=(0, 4))
        self.cash_label = tk.Label(self.cash_frame, text="Cash Tendered:", bg=COLORS["white"], fg=COLORS["text_secondary"], font=FONTS["small"])
        self.cash_label.pack(anchor="w")
        self.cash_entry = ttk.Entry(self.cash_frame, textvariable=self.cash_var)
        self.cash_entry.pack(fill=tk.X, pady=(2, 3))
        self.cash_entry.bind("<KeyRelease>", lambda _e: self.compute_change())
        change_row = tk.Frame(self.cash_frame, bg=COLORS["white"])
        change_row.pack(fill=tk.X)
        self.change_text_label = tk.Label(change_row, text="Change:", bg=COLORS["white"], fg=COLORS["text_secondary"], font=FONTS["small"])
        self.change_text_label.pack(side=tk.LEFT)
        self.change_label = tk.Label(change_row, textvariable=self.change_var, bg=COLORS["white"], fg=COLORS["success"], font=("Helvetica", 11, "bold"))
        self.change_label.pack(side=tk.RIGHT)

        self.summary = tk.Frame(self, bg=COLORS["white"])
        self.summary.pack(fill=tk.X, padx=10, pady=4)
        tk.Frame(self.summary, bg=COLORS["divider"], height=2).pack(fill=tk.X, pady=(0, 6))
        self.subtotal_label = self._summary_row(self.summary, "Subtotal:")
        self.tax_label = self._summary_row(self.summary, "Tax (12%):")
        self.discount_label = self._summary_row(self.summary, "Discount:")
        ttk.Separator(self.summary, orient=tk.HORIZONTAL).pack(fill=tk.X, pady=4)
        total_row = tk.Frame(self.summary, bg=COLORS["white"])
        total_row.pack(fill=tk.X)
        tk.Label(total_row, text="TOTAL:", bg=COLORS["white"], fg=COLORS["left_bg"], font=FONTS["total_lbl"]).pack(side=tk.LEFT)
        self.total_label = tk.Label(total_row, text="₱ 0.00", bg=COLORS["white"], fg=COLORS["accent"], font=FONTS["total_lbl"])
        self.total_label.pack(side=tk.RIGHT)

        actions = tk.Frame(self, bg=COLORS["white"])
        actions.pack(fill=tk.X, padx=10, pady=(4, 10))
        tk.Button(actions, text="Apply Discount", command=self.open_discount, bg=COLORS["accent_light"], fg=COLORS["left_bg"], relief=tk.FLAT, pady=8).pack(fill=tk.X, pady=2)
        tk.Button(actions, text="Clear Order", command=self.clear_order, bg=COLORS["danger_light"], fg=COLORS["danger"], relief=tk.FLAT, pady=8).pack(fill=tk.X, pady=2)
        tk.Button(actions, text="☕  Place Order", command=self.place_order, bg=COLORS["accent"], fg=COLORS["white"], relief=tk.FLAT, pady=12, font=FONTS["place_btn"]).pack(fill=tk.X, pady=2)
        self.reprint_btn = tk.Button(
            actions,
            text="🧾 Reopen Last Receipt",
            command=self.open_last_receipt,
            bg=COLORS["size_btn_inactive"],
            fg=COLORS["text_primary"],
            relief=tk.FLAT,
            pady=8,
            state=tk.DISABLED,
        )
        self.reprint_btn.pack(fill=tk.X, pady=2)
        self._refresh_payment_buttons()
        self.on_payment_change(self.state.payment_method)

    def _toggle_button(self, parent, text, value, command):
        return tk.Button(
            parent,
            text=text,
            relief=tk.FLAT,
            bd=1,
            cursor="hand2",
            font=FONTS["small"],
            command=lambda: command(value),
        )

    def _summary_row(self, parent, label):
        row = tk.Frame(parent, bg=COLORS["white"])
        row.pack(fill=tk.X, pady=1)
        tk.Label(row, text=label, bg=COLORS["white"], fg=COLORS["text_secondary"], font=FONTS["summary_lbl"]).pack(side=tk.LEFT)
        value = tk.Label(row, text="₱ 0.00", bg=COLORS["white"], fg=COLORS["text_secondary"], font=FONTS["summary_lbl"])
        value.pack(side=tk.RIGHT)
        return value

    def on_order_type_change(self, value):
        self.state.order_type = value
        self.order_type_var.set(value)
        self._refresh_order_type_buttons()

    def _refresh_order_type_buttons(self):
        for button, value in [(self.dine_btn, "Dine-in"), (self.takeout_btn, "Takeout")]:
            active = self.state.order_type == value
            button.configure(
                bg=COLORS["accent"] if active else COLORS["size_btn_inactive"],
                fg=COLORS["white"] if active else COLORS["text_secondary"],
            )

    def on_payment_change(self, value):
        self.state.payment_method = value
        self.payment_var.set(value)
        self._refresh_payment_buttons()
        if value == "Cash":
            self.cash_entry.configure(state="normal")
            self.cash_label.configure(text="Cash Tendered:")
            self.change_text_label.configure(text="Change:")
            self.change_label.configure(fg=COLORS["success"])
            self.compute_change()
        else:
            self.cash_var.set("")
            self.cash_entry.configure(state="disabled")
            self.cash_label.configure(text=f"{value} Payment:")
            self.change_text_label.configure(text="Status:")
            self.change_var.set("Paid")
            self.change_label.configure(fg=COLORS["success"])

    def _refresh_payment_buttons(self):
        for button, value in [(self.cash_btn, "Cash"), (self.ewallet_btn, "E-Wallet"), (self.card_btn, "Card")]:
            active = self.state.payment_method == value
            button.configure(
                bg=COLORS["accent"] if active else COLORS["size_btn_inactive"],
                fg=COLORS["white"] if active else COLORS["text_secondary"],
            )

    def add_to_order(self, name, size, price, qty=1):
        for item in self.state.current_order:
            if item["name"] == name and item["size"] == size:
                item["qty"] += qty
                self.refresh_order()
                return
        self.state.current_order.append({"name": name, "size": size, "price": float(price), "qty": qty})
        self.refresh_order()

    def refresh_order(self):
        for widget in self.order_inner.winfo_children():
            widget.destroy()
        if not self.state.current_order:
            tk.Label(self.order_inner, text="☕ No items yet", bg=COLORS["white"], fg=COLORS["text_secondary"], font=FONTS["summary_lbl"]).pack(pady=18)
        else:
            for idx, item in enumerate(self.state.current_order):
                row_bg = COLORS["white"] if idx % 2 == 0 else COLORS["row_alt"]
                row = tk.Frame(self.order_inner, bg=row_bg, padx=4, pady=5, highlightbackground=COLORS["divider"], highlightthickness=1)
                row.pack(fill=tk.X, padx=1, pady=1)
                top = tk.Frame(row, bg=row_bg)
                top.pack(fill=tk.X)
                full_name = item["name"] if item["size"] == "Regular" else f'{item["name"]} ({item["size"]})'
                name = full_name[:24] + "..." if len(full_name) > 27 else full_name
                tk.Label(top, text=name, bg=row_bg, fg=COLORS["text_primary"], font=FONTS["order_item"]).pack(side=tk.LEFT)
                controls = tk.Frame(top, bg=row_bg)
                controls.pack(side=tk.RIGHT)
                tk.Button(controls, text="–", command=lambda i=idx: self.change_qty(i, -1), relief=tk.FLAT, bg=COLORS["size_btn_inactive"], width=2).pack(side=tk.LEFT)
                tk.Label(controls, text=str(item["qty"]), bg=row_bg, fg=COLORS["text_primary"], width=2, font=("Helvetica", 10, "bold")).pack(side=tk.LEFT)
                tk.Button(controls, text="+", command=lambda i=idx: self.change_qty(i, 1), relief=tk.FLAT, bg=COLORS["size_btn_inactive"], width=2).pack(side=tk.LEFT)
                tk.Button(controls, text="🗑", command=lambda i=idx: self.remove_item(i), relief=tk.FLAT, bg=row_bg, fg=COLORS["danger"], width=2).pack(side=tk.LEFT)
                line_total = item["price"] * item["qty"]
                tk.Label(row, text=f'₱{item["price"]:.2f} x {item["qty"]} = ₱{line_total:.2f}', bg=row_bg, fg=COLORS["text_secondary"], font=FONTS["order_sub"]).pack(anchor="w")
        self.update_summary()

    def change_qty(self, index, delta):
        self.state.current_order[index]["qty"] += delta
        if self.state.current_order[index]["qty"] <= 0:
            self.state.current_order.pop(index)
        self.refresh_order()

    def remove_item(self, index):
        self.state.current_order.pop(index)
        self.refresh_order()

    def update_summary(self):
        subtotal = sum(item["price"] * item["qty"] for item in self.state.current_order)
        tax = subtotal * APP["tax_rate"]
        total = subtotal + tax - self.state.discount_amount
        if total < 0:
            total = 0.0
        self.subtotal_value = subtotal
        self.tax_value = tax
        self.state.total = total
        self.subtotal_label.configure(text=f"₱ {subtotal:.2f}")
        self.tax_label.configure(text=f"₱ {tax:.2f}")
        self.discount_label.configure(text=f"-₱ {self.state.discount_amount:.2f}", fg=COLORS["success"] if self.state.discount_amount > 0 else COLORS["text_secondary"])
        self.total_label.configure(text=f"₱ {total:.2f}")
        self.compute_change()

    def refresh_discount_label(self):
        self.discount_label.configure(
            text=f"-₱ {self.state.discount_amount:.2f}",
            fg=COLORS["success"] if self.state.discount_amount > 0 else COLORS["text_secondary"],
        )

    def compute_change(self):
        if self.state.payment_method != "Cash":
            self.change_var.set("Paid")
            self.change_label.configure(fg=COLORS["success"])
            return 0.0
        try:
            tendered = float(self.cash_var.get()) if self.cash_var.get().strip() else 0.0
            change = tendered - self.state.total
            if change >= 0:
                self.change_label.configure(fg=COLORS["success"])
                self.change_var.set(f"₱ {change:.2f}")
            else:
                self.change_label.configure(fg=COLORS["danger"])
                self.change_var.set(f"-₱ {abs(change):.2f}")
            return change
        except ValueError:
            self.change_label.configure(fg=COLORS["text_secondary"])
            self.change_var.set("₱ 0.00")
            return None

    def open_discount(self):
        from ui.discount import DiscountWindow

        if not self.state.current_order:
            messagebox.showwarning("No order", "Add items before applying discount.")
            return
        DiscountWindow(self.winfo_toplevel(), self.state, self.update_summary, self.refresh_discount_label)

    def clear_order(self):
        if not self.state.current_order:
            return
        if not messagebox.askyesno("Clear order", "Clear current order?"):
            return
        self.state.current_order = []
        self.state.discount_amount = 0.0
        self.cash_var.set("")
        self.refresh_order()

    def place_order(self):
        if not self.state.current_order:
            messagebox.showwarning("Empty order", "Please add items before placing an order.")
            return
        cash_tendered = 0.0
        change_amount = 0.0
        if self.state.payment_method == "Cash":
            try:
                cash_tendered = float(self.cash_var.get())
            except ValueError:
                messagebox.showwarning("Invalid cash", "Please input a valid cash tendered amount.")
                return
            if cash_tendered < self.state.total:
                messagebox.showwarning("Insufficient cash", "Cash tendered must be equal or higher than total.")
                return
            change_amount = cash_tendered - self.state.total

        payload = {
            "cashier": self.state.current_user.get("name", "Unknown"),
            "order_type": self.state.order_type,
            "payment_method": self.state.payment_method,
            "subtotal": self.subtotal_value,
            "tax": self.tax_value,
            "discount": self.state.discount_amount,
            "total": self.state.total,
            "cash_tendered": cash_tendered,
            "change_amount": change_amount,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "items": self.state.current_order,
        }
        order_id = self.db.insert_order(payload)
        if not order_id:
            messagebox.showerror("Database error", "Failed to save order.")
            return

        from ui.receipt import ReceiptWindow

        order_data = dict(payload)
        order_data["order_id"] = order_id
        self.state.last_receipt_data = order_data
        self.reprint_btn.configure(state=tk.NORMAL)
        ReceiptWindow(self.winfo_toplevel(), order_data)
        self.state.current_order = []
        self.state.discount_amount = 0.0
        self.cash_var.set("")
        self.refresh_order()

    def open_last_receipt(self):
        if not self.state.last_receipt_data:
            messagebox.showinfo("No receipt", "No receipt available yet.")
            return
        from ui.receipt import ReceiptWindow

        ReceiptWindow(self.winfo_toplevel(), dict(self.state.last_receipt_data))

    def _on_order_canvas_resize(self, event):
        self.order_canvas.itemconfigure(self.order_window, width=event.width)

    def _on_order_mouse_wheel(self, event):
        self.order_canvas.yview_scroll(-1 * int(event.delta / 120), "units")
