import tkinter as tk

from config import COLORS


def center_window(win, width, height):
    sw = win.winfo_screenwidth()
    sh = win.winfo_screenheight()
    x = (sw - width) // 2
    y = (sh - height) // 2
    win.geometry(f"{width}x{height}+{x}+{y}")


class DiscountWindow(tk.Toplevel):
    def __init__(self, parent, state, on_apply_summary, on_refresh_label):
        super().__init__(parent)
        self.state = state
        self.on_apply_summary = on_apply_summary
        self.on_refresh_label = on_refresh_label
        self.discount_type = tk.IntVar(value=1)
        self.value_var = tk.StringVar(value="20")
        self.preview_var = tk.StringVar(value="Discount: -₱ 0.00")
        self.error_var = tk.StringVar(value="")
        self.configure(bg=COLORS["white"])
        self.resizable(False, False)
        center_window(self, 340, 300)
        self.grab_set()
        self._build()
        self.preview_discount()

    def _build(self):
        title = tk.Frame(self, bg=COLORS["title_bar"], height=34)
        title.pack(fill=tk.X)
        title.pack_propagate(False)
        tk.Label(title, text="🎁 Apply Discount", bg=COLORS["title_bar"], fg=COLORS["white"], font=("Helvetica", 11, "bold")).pack(side=tk.LEFT, padx=10)

        content = tk.Frame(self, bg=COLORS["white"], padx=14, pady=12)
        content.pack(fill=tk.BOTH, expand=True)
        tk.Label(content, text="Select Discount Type:", bg=COLORS["white"], fg=COLORS["text_primary"], font=("Helvetica", 11, "bold")).pack(anchor="w")

        tk.Radiobutton(content, text="Senior / PWD Discount (20%)", variable=self.discount_type, value=1, bg=COLORS["white"], command=self.on_type_change).pack(anchor="w", pady=2)
        tk.Radiobutton(content, text="Custom Percentage (%)", variable=self.discount_type, value=2, bg=COLORS["white"], command=self.on_type_change).pack(anchor="w", pady=2)
        tk.Radiobutton(content, text="Fixed Amount (₱)", variable=self.discount_type, value=3, bg=COLORS["white"], command=self.on_type_change).pack(anchor="w", pady=2)

        self.hint_label = tk.Label(content, text="", bg=COLORS["white"], fg=COLORS["text_secondary"], font=("Helvetica", 9))
        self.hint_label.pack(anchor="w", pady=(8, 2))
        self.value_entry = tk.Entry(content, textvariable=self.value_var)
        self.value_entry.pack(fill=tk.X)
        self.value_entry.bind("<KeyRelease>", lambda _e: self.preview_discount())

        tk.Label(content, textvariable=self.preview_var, bg=COLORS["white"], fg=COLORS["success"], font=("Helvetica", 12, "bold")).pack(anchor="w", pady=(10, 2))
        tk.Label(content, textvariable=self.error_var, bg=COLORS["white"], fg=COLORS["danger"], font=("Helvetica", 9)).pack(anchor="w")

        actions = tk.Frame(content, bg=COLORS["white"])
        actions.pack(fill=tk.X, pady=(10, 0))
        tk.Button(actions, text="Apply", bg=COLORS["accent"], fg=COLORS["white"], relief=tk.FLAT, command=self.apply_discount).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 4))
        tk.Button(actions, text="Cancel", bg="#F5F5F5", fg=COLORS["text_primary"], relief=tk.FLAT, command=self.destroy).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(4, 0))
        self.on_type_change()

    def on_type_change(self):
        dtype = self.discount_type.get()
        if dtype == 1:
            self.hint_label.configure(text="Senior/PWD discount is fixed at 20%")
            self.value_var.set("20")
            self.value_entry.configure(state=tk.DISABLED)
        elif dtype == 2:
            self.hint_label.configure(text="Enter % e.g. 10")
            self.value_entry.configure(state=tk.NORMAL)
            if self.value_var.get() == "20":
                self.value_var.set("")
        else:
            self.hint_label.configure(text="Enter amount e.g. 50")
            self.value_entry.configure(state=tk.NORMAL)
            if self.value_var.get() == "20":
                self.value_var.set("")
        self.preview_discount()

    def _compute_discount(self):
        subtotal = sum(item["price"] * item["qty"] for item in self.state.current_order)
        dtype = self.discount_type.get()
        try:
            if dtype == 1:
                discount = subtotal * 0.20
            elif dtype == 2:
                pct = float(self.value_var.get())
                if pct <= 0 or pct > 100:
                    return None, "Percentage must be between 0 and 100."
                discount = subtotal * (pct / 100.0)
            else:
                amount = float(self.value_var.get())
                if amount <= 0:
                    return None, "Fixed amount must be positive."
                if amount > subtotal:
                    return None, "Fixed amount cannot exceed subtotal."
                discount = amount
        except ValueError:
            return None, "Value must be a positive number."
        return discount, ""

    def preview_discount(self):
        discount, error = self._compute_discount()
        if error:
            self.error_var.set(error)
            self.preview_var.set("Discount: -₱ 0.00")
        else:
            self.error_var.set("")
            self.preview_var.set(f"Discount: -₱ {discount:.2f}")

    def apply_discount(self):
        discount, error = self._compute_discount()
        if error:
            self.error_var.set(error)
            return
        self.state.discount_amount = discount
        self.on_apply_summary()
        self.on_refresh_label()
        self.destroy()
