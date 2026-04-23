import tkinter as tk
from tkinter import messagebox

from config import APP, COLORS, FONTS


def center_window(win, width, height):
    sw = win.winfo_screenwidth()
    sh = win.winfo_screenheight()
    x = (sw - width) // 2
    y = (sh - height) // 2
    win.geometry(f"{width}x{height}+{x}+{y}")


class SizeSelectWindow(tk.Toplevel):
    def __init__(self, parent, item, on_add):
        super().__init__(parent)
        self.item = item
        self.on_add = on_add
        self.selected_size = None
        self.selected_price = 0.0
        self.qty = 1
        self.cards = {}
        self.configure(bg=COLORS["white"])
        center_window(self, 340, 280)
        self.resizable(False, False)
        self.grab_set()
        self.overrideredirect(False)
        self._build()

    def _build(self):
        title = tk.Frame(self, bg=COLORS["title_bar"], height=32)
        title.pack(fill=tk.X)
        title.pack_propagate(False)
        tk.Label(title, text="☕ Select Size", bg=COLORS["title_bar"], fg=COLORS["white"], font=("Helvetica", 11, "bold")).pack(side=tk.LEFT, padx=10)
        tk.Button(
            title,
            text="✕",
            command=self.destroy,
            bg=COLORS["title_bar"],
            fg=COLORS["white"],
            relief=tk.FLAT,
            bd=0,
            cursor="hand2",
        ).pack(side=tk.RIGHT, padx=8)

        tk.Label(
            self,
            text=self.item["name"],
            bg=COLORS["white"],
            fg=COLORS["left_bg"],
            font=("Helvetica", 13, "bold"),
        ).pack(pady=(10, 8))

        card_wrap = tk.Frame(self, bg=COLORS["white"])
        card_wrap.pack(fill=tk.X, padx=12)
        prices = {
            "Small": self.item["price_small"],
            "Medium": self.item["price_medium"],
            "Large": self.item["price_large"],
        }
        for idx, size in enumerate(APP["sizes"]):
            card = tk.Frame(
                card_wrap,
                bg=COLORS["white"],
                highlightthickness=2,
                highlightbackground=COLORS["card_border"],
                cursor="hand2",
                padx=12,
                pady=8,
            )
            card.grid(row=0, column=idx, padx=4, sticky="nsew")
            card_wrap.columnconfigure(idx, weight=1)
            tk.Label(card, text=size, bg=COLORS["white"], fg=COLORS["left_bg"], font=("Helvetica", 12, "bold")).pack()
            tk.Label(card, text=f"₱ {prices[size]:.2f}", bg=COLORS["white"], fg=COLORS["accent"], font=FONTS["size_price"]).pack()
            card.bind("<Button-1>", lambda _e, s=size, p=prices[size]: self.select_size(s, p))
            for child in card.winfo_children():
                child.bind("<Button-1>", lambda _e, s=size, p=prices[size]: self.select_size(s, p))
            self.cards[size] = card

        qty_row = tk.Frame(self, bg=COLORS["white"])
        qty_row.pack(pady=12)
        tk.Label(qty_row, text="Quantity:", bg=COLORS["white"], fg=COLORS["text_primary"], font=FONTS["summary_lbl"]).pack(side=tk.LEFT, padx=(0, 8))
        tk.Button(qty_row, text="–", command=self.decrease_qty, width=3, relief=tk.FLAT, bg=COLORS["size_btn_inactive"]).pack(side=tk.LEFT)
        self.qty_label = tk.Label(qty_row, text=str(self.qty), width=4, bg=COLORS["white"], fg=COLORS["text_primary"], font=("Helvetica", 11, "bold"))
        self.qty_label.pack(side=tk.LEFT)
        tk.Button(qty_row, text="+", command=self.increase_qty, width=3, relief=tk.FLAT, bg=COLORS["size_btn_inactive"]).pack(side=tk.LEFT)

        actions = tk.Frame(self, bg=COLORS["white"])
        actions.pack(fill=tk.X, padx=12, pady=(4, 12))
        tk.Button(
            actions,
            text="Cancel",
            bg="#F5F5F5",
            fg=COLORS["text_primary"],
            relief=tk.FLAT,
            command=self.destroy,
            pady=8,
            cursor="hand2",
        ).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 4))
        tk.Button(
            actions,
            text="☕ Add to Order",
            bg=COLORS["accent"],
            fg=COLORS["white"],
            relief=tk.FLAT,
            command=self.add_item,
            pady=8,
            cursor="hand2",
            font=("Helvetica", 10, "bold"),
        ).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(4, 0))

    def select_size(self, size, price):
        self.selected_size = size
        self.selected_price = price
        for key, card in self.cards.items():
            if key == size:
                card.configure(highlightbackground=COLORS["size_border"], bg=COLORS["accent_light"])
                for child in card.winfo_children():
                    child.configure(bg=COLORS["accent_light"])
            else:
                card.configure(highlightbackground=COLORS["card_border"], bg=COLORS["white"])
                for child in card.winfo_children():
                    child.configure(bg=COLORS["white"])

    def increase_qty(self):
        if self.qty < 99:
            self.qty += 1
            self.qty_label.configure(text=str(self.qty))

    def decrease_qty(self):
        if self.qty > 1:
            self.qty -= 1
            self.qty_label.configure(text=str(self.qty))

    def add_item(self):
        if not self.selected_size:
            messagebox.showwarning("Select size", "Please select a size first.")
            return
        self.on_add(self.item["name"], self.selected_size, self.selected_price, self.qty)
        self.destroy()
