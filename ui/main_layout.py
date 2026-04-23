import tkinter as tk

from config import COLORS
from ui.center_panel import CenterPanel
from ui.left_panel import LeftPanel
from ui.right_panel import RightPanel


class MainLayout(tk.Frame):
    def __init__(self, parent, db, state):
        super().__init__(parent, bg=COLORS["root_bg"])
        self.db = db
        self.state = state
        self._build()

    def _build(self):
        body = tk.Frame(self, bg=COLORS["root_bg"])
        body.pack(fill=tk.BOTH, expand=True)

        self.right_panel = RightPanel(body, self.db, self.state)
        self.right_panel.pack(side=tk.RIGHT, fill=tk.Y)

        self.center_panel = CenterPanel(
            body,
            self.db,
            self.state,
            add_to_order_callback=self.right_panel.add_to_order,
        )
        self.center_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.left_panel = LeftPanel(
            body,
            self.db,
            self.state,
            center_panel=self.center_panel,
            right_panel=self.right_panel,
        )
        self.left_panel.pack(side=tk.LEFT, fill=tk.Y)

        self.center_panel.load_category(self.state.selected_category)
