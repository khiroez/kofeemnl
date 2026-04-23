import os
import subprocess
import sys
import tempfile
import tkinter as tk

from config import APP, COLORS, FONTS


def center_window(win, width, height):
    sw = win.winfo_screenwidth()
    sh = win.winfo_screenheight()
    x = (sw - width) // 2
    y = (sh - height) // 2
    win.geometry(f"{width}x{height}+{x}+{y}")


def size_abbrev(size):
    return {"Small": "Sml", "Medium": "Med", "Large": "Lrg", "Regular": "Reg"}.get(size, size[:3])


class ReceiptWindow(tk.Toplevel):
    def __init__(self, parent, order_data):
        super().__init__(parent)
        self.order_data = order_data
        self.configure(bg=COLORS["white"])
        self.title("Order Receipt")
        self.resizable(False, False)
        center_window(self, 400, 580)
        self.grab_set()
        self._build()

    def _build(self):
        title = tk.Frame(self, bg=COLORS["title_bar"], height=34)
        title.pack(fill=tk.X)
        title.pack_propagate(False)
        tk.Label(title, text="🧾 Order Receipt", bg=COLORS["title_bar"], fg=COLORS["white"], font=("Helvetica", 11, "bold")).pack(side=tk.LEFT, padx=10)
        tk.Button(title, text="✕ Close", command=self.destroy, bg=COLORS["title_bar"], fg=COLORS["white"], relief=tk.FLAT, bd=0, cursor="hand2").pack(side=tk.RIGHT, padx=8)

        self.text = tk.Text(self, font=FONTS["receipt"], bg=COLORS["white"], relief=tk.FLAT, padx=20, pady=10)
        self.text.pack(fill=tk.BOTH, expand=True)
        self.text.insert("1.0", self.build_receipt_text())
        self.text.tag_configure("centered", justify="center")
        self.text.tag_add("centered", "1.0", "end")
        self.text.configure(state=tk.DISABLED)

        actions = tk.Frame(self, bg=COLORS["white"])
        actions.pack(fill=tk.X, padx=12, pady=10)
        tk.Button(actions, text="🖨️ Print", bg=COLORS["accent"], fg=COLORS["white"], relief=tk.FLAT, command=self.print_receipt, padx=20).pack(side=tk.LEFT, padx=(0, 5))
        tk.Button(actions, text="✕ Close", bg="#F5F5F5", fg=COLORS["text_primary"], relief=tk.FLAT, command=self.destroy, padx=20).pack(side=tk.LEFT, padx=5)

    def build_receipt_text(self):
        order = self.order_data
        lines = [
            "================================",
            f"      ☕ {APP['name']}",
            "    123 Brew St, Coffee City",
            "================================",
            f"Date:    {order['timestamp']}",
            f"Cashier: {order['cashier']}",
            f"Order #: {order['order_id']:04d}",
            f"Type:    {order['order_type']}",
            f"Payment: {order['payment_method']}",
            "--------------------------------",
            "Item            Size  Qty  Price",
            "--------------------------------",
        ]
        for item in order["items"]:
            name = item["name"][:14].ljust(14)
            size = size_abbrev(item["size"]).ljust(4)
            qty = f"x{item['qty']}".ljust(4)
            total = f"₱{item['price'] * item['qty']:.0f}".rjust(6)
            lines.append(f"{name} {size}  {qty} {total}")
        lines.extend(
            [
                "--------------------------------",
                f"Subtotal:             ₱{order['subtotal']:.2f}",
                f"Tax (12%):            ₱{order['tax']:.2f}",
                f"Discount:             ₱{order['discount']:.2f}",
                "================================",
                f"TOTAL:                ₱{order['total']:.2f}",
                "================================",
            ]
        )
        if order["payment_method"] == "Cash":
            lines.extend(
                [
                    f"Cash:                 ₱{order['cash_tendered']:.2f}",
                    f"Change:               ₱{order['change_amount']:.2f}",
                ]
            )
        else:
            lines.append(f"Paid via:             {order['payment_method']}")
        lines.extend(
            [
                "--------------------------------",
                "  Thank you! Come again ☕",
                "================================",
            ]
        )
        return "\n".join(lines)

    def print_receipt(self):
        text = self.build_receipt_text()
        path = os.path.join(tempfile.gettempdir(), f"kofee_receipt_{self.order_data['order_id']}.txt")
        with open(path, "w", encoding="utf-8") as handle:
            handle.write(text)

        try:
            if sys.platform.startswith("win"):
                os.startfile(path)
            else:
                subprocess.run(["lpr", path], check=False)
        except Exception as error:
            print(f"[PRINT ERROR] {error}")
