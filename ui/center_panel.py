import tkinter as tk
from tkinter import ttk

from config import COLORS, FONTS
from ui.size_select import SizeSelectWindow


class CenterPanel(tk.Frame):
    def __init__(self, parent, db, state, add_to_order_callback):
        super().__init__(parent, bg=COLORS["root_bg"])
        self.db = db
        self.state = state
        self.add_to_order_callback = add_to_order_callback
        self.current_items = []
        self.filtered_items = []
        self.grid_columns = 3
        self._build()

    def _build(self):
        top = tk.Frame(self, bg=COLORS["root_bg"])
        top.pack(fill=tk.X, padx=16, pady=(14, 8))
        self.category_label = tk.Label(
            top,
            text=self.state.selected_category,
            bg=COLORS["root_bg"],
            fg=COLORS["left_bg"],
            font=("Helvetica", 14, "bold"),
        )
        self.category_label.pack(side=tk.LEFT)

        self.search_entry = ttk.Entry(top, width=22, font=FONTS["input"])
        self.search_entry.pack(side=tk.RIGHT)
        self.search_entry.insert(0, "Search item...")
        self.search_entry.configure(foreground="#888888")
        self.search_entry.bind("<FocusIn>", self._on_search_focus_in)
        self.search_entry.bind("<FocusOut>", self._on_search_focus_out)
        self.search_entry.bind("<KeyRelease>", lambda _event: self.filter_menu())
        ttk.Separator(self, orient=tk.HORIZONTAL).pack(fill=tk.X, padx=16, pady=(0, 10))

        container = tk.Frame(self, bg=COLORS["root_bg"])
        container.pack(fill=tk.BOTH, expand=True, padx=12, pady=(0, 10))
        self.canvas = tk.Canvas(container, bg=COLORS["root_bg"], highlightthickness=0)
        self.scrollbar = tk.Scrollbar(container, orient=tk.VERTICAL, command=self.canvas.yview)
        self.menu_frame = tk.Frame(self.canvas, bg=COLORS["root_bg"])
        self.menu_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")),
        )
        self.menu_window = self.canvas.create_window((0, 0), window=self.menu_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.canvas.bind("<Configure>", self._on_canvas_resize)

        self.canvas.bind_all("<MouseWheel>", self._on_mouse_wheel)
        self.canvas.bind_all("<Button-4>", lambda _e: self.canvas.yview_scroll(-1, "units"))
        self.canvas.bind_all("<Button-5>", lambda _e: self.canvas.yview_scroll(1, "units"))

    def _on_search_focus_in(self, _event):
        if self.search_entry.get() == "Search item...":
            self.search_entry.delete(0, tk.END)
            self.search_entry.configure(foreground="#111111")

    def _on_search_focus_out(self, _event):
        if not self.search_entry.get().strip():
            self.search_entry.delete(0, tk.END)
            self.search_entry.insert(0, "Search item...")
            self.search_entry.configure(foreground="#888888")

    def _on_mouse_wheel(self, event):
        delta = -1 * int(event.delta / 120)
        self.canvas.yview_scroll(delta, "units")

    def _on_canvas_resize(self, event):
        self.canvas.itemconfigure(self.menu_window, width=event.width)
        next_columns = max(1, event.width // 220)
        if next_columns != self.grid_columns:
            self.grid_columns = next_columns
            self._build_grid()

    def load_category(self, category):
        self.state.selected_category = category
        self.category_label.configure(text=category)
        self.current_items = self.db.get_menu_items_by_category(category)
        self.filtered_items = list(self.current_items)
        self._build_grid()

    def filter_menu(self):
        term = self.search_entry.get().strip().lower()
        if term == "search item...":
            term = ""
        if not term:
            self.filtered_items = list(self.current_items)
        else:
            self.filtered_items = [item for item in self.current_items if term in item["name"].lower()]
        self._build_grid()

    def _build_grid(self):
        for widget in self.menu_frame.winfo_children():
            widget.destroy()

        if not self.filtered_items:
            tk.Label(
                self.menu_frame,
                text="No items found",
                bg=COLORS["root_bg"],
                fg=COLORS["text_secondary"],
                font=FONTS["summary_lbl"],
            ).grid(row=0, column=0, columnspan=self.grid_columns, pady=24)
            return

        for idx in range(self.grid_columns):
            self.menu_frame.columnconfigure(idx, weight=1, uniform="col")

        for idx, item in enumerate(self.filtered_items):
            row = idx // self.grid_columns
            col = idx % self.grid_columns
            if item["has_sizes"] == 1:
                text = (
                    f'{item["name"]}\n'
                    f'S ₱{item["price_small"]:.0f}  M ₱{item["price_medium"]:.0f}  L ₱{item["price_large"]:.0f}\n'
                    "[ Tap to select size ]"
                )
                command = lambda menu_item=item: self.open_size_select(menu_item)
            else:
                text = f'{item["name"]}\n₱ {item["price_fixed"]:.2f}'
                command = lambda menu_item=item: self.add_to_order(menu_item["name"], "Regular", menu_item["price_fixed"], 1)

            card = tk.Button(
                self.menu_frame,
                text=text,
                command=command,
                bg=COLORS["card_bg"],
                fg=COLORS["text_primary"],
                relief=tk.FLAT,
                bd=0,
                highlightbackground=COLORS["card_border"],
                highlightthickness=1,
                width=20,
                height=4,
                cursor="hand2",
                justify="center",
                wraplength=200,
                font=FONTS["menu_price"],
            )
            card.grid(row=row, column=col, padx=6, pady=6, sticky="nsew")
            self._bind_hover(card)

    def _bind_hover(self, widget):
        widget.bind(
            "<Enter>",
            lambda _e: widget.configure(bg=COLORS["card_hover"], highlightbackground=COLORS["accent"]),
        )
        widget.bind(
            "<Leave>",
            lambda _e: widget.configure(bg=COLORS["card_bg"], highlightbackground=COLORS["card_border"]),
        )

    def open_size_select(self, item):
        SizeSelectWindow(self.winfo_toplevel(), item, self.add_to_order)

    def add_to_order(self, name, size, price, qty=1):
        self.add_to_order_callback(name, size, price, qty)
