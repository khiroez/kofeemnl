import hashlib
import sqlite3
from datetime import datetime

from config import APP


class Database:
    def __init__(self, db_file=None):
        self.db_file = db_file or APP["db_file"]
        self.init_db()

    def connect(self):
        conn = sqlite3.connect(self.db_file)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON")
        return conn

    def init_db(self):
        try:
            with self.connect() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    """
                    CREATE TABLE IF NOT EXISTS users (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        username TEXT NOT NULL,
                        pin TEXT NOT NULL,
                        role TEXT NOT NULL CHECK(role IN ('admin', 'cashier'))
                    )
                    """
                )
                cursor.execute(
                    """
                    CREATE TABLE IF NOT EXISTS menu_items (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        name TEXT NOT NULL,
                        category TEXT NOT NULL,
                        has_sizes INTEGER DEFAULT 0,
                        price_small REAL DEFAULT 0,
                        price_medium REAL DEFAULT 0,
                        price_large REAL DEFAULT 0,
                        price_fixed REAL DEFAULT 0,
                        available INTEGER DEFAULT 1
                    )
                    """
                )
                cursor.execute(
                    """
                    CREATE TABLE IF NOT EXISTS orders (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        cashier TEXT,
                        order_type TEXT CHECK(order_type IN ('Dine-in', 'Takeout')),
                        payment_method TEXT CHECK(payment_method IN ('Cash','E-Wallet','Card')),
                        subtotal REAL,
                        tax REAL,
                        discount REAL,
                        total REAL,
                        cash_tendered REAL,
                        change_amount REAL,
                        timestamp TEXT
                    )
                    """
                )
                cursor.execute(
                    """
                    CREATE TABLE IF NOT EXISTS order_items (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        order_id INTEGER,
                        item_name TEXT,
                        size TEXT CHECK(size IN ('Small','Medium','Large','Regular')),
                        quantity INTEGER,
                        unit_price REAL,
                        total_price REAL,
                        FOREIGN KEY(order_id) REFERENCES orders(id) ON DELETE CASCADE
                    )
                    """
                )
                cursor.execute(
                    """
                    CREATE TABLE IF NOT EXISTS item_sizes (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        item_id INTEGER,
                        size_label TEXT CHECK(size_label IN ('Small','Medium','Large')),
                        price REAL,
                        FOREIGN KEY(item_id) REFERENCES menu_items(id) ON DELETE CASCADE
                    )
                    """
                )
                conn.commit()
                self.seed_data(conn)
        except sqlite3.Error as error:
            print(f"[DB INIT ERROR] {error}")

    def _hash_pin(self, pin):
        return hashlib.sha256(pin.encode("utf-8")).hexdigest()

    def seed_data(self, conn):
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM users")
        users_count = cursor.fetchone()[0]
        if users_count == 0:
            users = [
                ("admin", self._hash_pin("1234"), "admin"),
                ("cashier1", self._hash_pin("0000"), "cashier"),
            ]
            cursor.executemany("INSERT INTO users(username, pin, role) VALUES(?, ?, ?)", users)

        cursor.execute("SELECT COUNT(*) FROM menu_items")
        menu_count = cursor.fetchone()[0]
        if menu_count > 0:
            conn.commit()
            return

        menu_items = [
            ("Cafe Latte", "Hot Drinks", 1, 100, 120, 140, 0, 1),
            ("Americano", "Hot Drinks", 1, 80, 100, 120, 0, 1),
            ("Cappuccino", "Hot Drinks", 1, 110, 130, 150, 0, 1),
            ("Espresso", "Hot Drinks", 1, 80, 90, 100, 0, 1),
            ("Mocha", "Hot Drinks", 1, 115, 135, 155, 0, 1),
            ("Hot Chocolate", "Hot Drinks", 1, 90, 110, 130, 0, 1),
            ("Matcha Latte", "Hot Drinks", 1, 120, 140, 160, 0, 1),
            ("Chai Latte", "Hot Drinks", 1, 100, 120, 140, 0, 1),
            ("Iced Latte", "Cold Drinks", 1, 110, 130, 150, 0, 1),
            ("Iced Americano", "Cold Drinks", 1, 90, 110, 130, 0, 1),
            ("Frappe", "Cold Drinks", 1, 130, 150, 170, 0, 1),
            ("Iced Matcha", "Cold Drinks", 1, 120, 140, 160, 0, 1),
            ("Strawberry Smoothie", "Cold Drinks", 1, 130, 150, 170, 0, 1),
            ("Iced Chocolate", "Cold Drinks", 1, 110, 130, 150, 0, 1),
            ("Croissant", "Snacks", 0, 0, 0, 0, 85, 1),
            ("Chocolate Muffin", "Snacks", 0, 0, 0, 0, 75, 1),
            ("Cheese Bread", "Snacks", 0, 0, 0, 0, 60, 1),
            ("Banana Bread", "Snacks", 0, 0, 0, 0, 70, 1),
            ("Egg Sandwich", "Snacks", 0, 0, 0, 0, 90, 1),
            ("Cheesecake", "Desserts", 0, 0, 0, 0, 150, 1),
            ("Chocolate Cake", "Desserts", 0, 0, 0, 0, 140, 1),
            ("Waffles", "Desserts", 0, 0, 0, 0, 130, 1),
            ("Crepe", "Desserts", 0, 0, 0, 0, 120, 1),
            ("Pasta", "Meals", 0, 0, 0, 0, 180, 1),
            ("Club Sandwich", "Meals", 0, 0, 0, 0, 160, 1),
            ("Rice Meal", "Meals", 0, 0, 0, 0, 150, 1),
            ("Chicken Wrap", "Meals", 0, 0, 0, 0, 165, 1),
        ]

        cursor.executemany(
            """
            INSERT INTO menu_items (
                name, category, has_sizes, price_small, price_medium,
                price_large, price_fixed, available
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            menu_items,
        )
        conn.commit()

        cursor.execute("SELECT id, has_sizes, price_small, price_medium, price_large FROM menu_items")
        sized_records = cursor.fetchall()
        size_rows = []
        for record in sized_records:
            if record["has_sizes"] == 1:
                size_rows.extend(
                    [
                        (record["id"], "Small", record["price_small"]),
                        (record["id"], "Medium", record["price_medium"]),
                        (record["id"], "Large", record["price_large"]),
                    ]
                )
        if size_rows:
            cursor.executemany(
                "INSERT INTO item_sizes(item_id, size_label, price) VALUES (?, ?, ?)",
                size_rows,
            )
        conn.commit()

    def validate_user(self, username, hashed_pin):
        try:
            with self.connect() as conn:
                row = conn.execute(
                    "SELECT username, role FROM users WHERE username = ? AND pin = ?",
                    (username, hashed_pin),
                ).fetchone()
                return dict(row) if row else None
        except sqlite3.Error as error:
            print(f"[DB USER VALIDATION ERROR] {error}")
            return None

    def get_menu_items_by_category(self, category):
        try:
            with self.connect() as conn:
                rows = conn.execute(
                    "SELECT * FROM menu_items WHERE category = ? AND available = 1 ORDER BY name",
                    (category,),
                ).fetchall()
                return [dict(row) for row in rows]
        except sqlite3.Error as error:
            print(f"[DB MENU FETCH ERROR] {error}")
            return []

    def get_all_menu_items(self):
        try:
            with self.connect() as conn:
                rows = conn.execute("SELECT * FROM menu_items ORDER BY category, name").fetchall()
                return [dict(row) for row in rows]
        except sqlite3.Error as error:
            print(f"[DB ALL MENU FETCH ERROR] {error}")
            return []

    def insert_order(self, payload):
        try:
            with self.connect() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    """
                    INSERT INTO orders (
                        cashier, order_type, payment_method, subtotal, tax, discount,
                        total, cash_tendered, change_amount, timestamp
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        payload["cashier"],
                        payload["order_type"],
                        payload["payment_method"],
                        payload["subtotal"],
                        payload["tax"],
                        payload["discount"],
                        payload["total"],
                        payload["cash_tendered"],
                        payload["change_amount"],
                        payload.get("timestamp") or datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    ),
                )
                order_id = cursor.lastrowid
                for item in payload["items"]:
                    cursor.execute(
                        """
                        INSERT INTO order_items (
                            order_id, item_name, size, quantity, unit_price, total_price
                        ) VALUES (?, ?, ?, ?, ?, ?)
                        """,
                        (
                            order_id,
                            item["name"],
                            item["size"],
                            item["qty"],
                            item["price"],
                            item["price"] * item["qty"],
                        ),
                    )
                conn.commit()
                return order_id
        except sqlite3.Error as error:
            print(f"[DB INSERT ORDER ERROR] {error}")
            return None

    def get_order_items(self, order_id):
        try:
            with self.connect() as conn:
                rows = conn.execute(
                    "SELECT * FROM order_items WHERE order_id = ? ORDER BY id",
                    (order_id,),
                ).fetchall()
                return [dict(row) for row in rows]
        except sqlite3.Error as error:
            print(f"[DB ORDER ITEMS ERROR] {error}")
            return []

    def get_recent_orders(self, limit=100):
        try:
            with self.connect() as conn:
                rows = conn.execute(
                    """
                    SELECT o.*, COALESCE(SUM(oi.quantity), 0) AS item_count
                    FROM orders o
                    LEFT JOIN order_items oi ON o.id = oi.order_id
                    GROUP BY o.id
                    ORDER BY o.id DESC
                    LIMIT ?
                    """,
                    (limit,),
                ).fetchall()
                return [dict(row) for row in rows]
        except sqlite3.Error as error:
            print(f"[DB RECENT ORDERS ERROR] {error}")
            return []

    def get_filtered_orders(self, filter_key):
        where_clause = ""
        if filter_key == "Today":
            where_clause = "WHERE DATE(timestamp) = DATE('now', 'localtime')"
        elif filter_key == "This Week":
            where_clause = "WHERE timestamp >= DATETIME('now', '-7 days', 'localtime')"
        elif filter_key == "This Month":
            where_clause = "WHERE timestamp >= DATETIME('now', '-30 days', 'localtime')"

        query = f"""
            SELECT o.*, COALESCE(SUM(oi.quantity), 0) AS item_count
            FROM orders o
            LEFT JOIN order_items oi ON o.id = oi.order_id
            {where_clause}
            GROUP BY o.id
            ORDER BY o.id DESC
        """
        try:
            with self.connect() as conn:
                rows = conn.execute(query).fetchall()
                return [dict(row) for row in rows]
        except sqlite3.Error as error:
            print(f"[DB FILTERED ORDERS ERROR] {error}")
            return []

    def sales_summary_today(self):
        result = {"sales": 0.0, "orders": 0, "top_item": "N/A"}
        try:
            with self.connect() as conn:
                sales = conn.execute(
                    "SELECT COALESCE(SUM(total), 0) FROM orders WHERE DATE(timestamp) = DATE('now', 'localtime')"
                ).fetchone()[0]
                orders = conn.execute(
                    "SELECT COUNT(id) FROM orders WHERE DATE(timestamp) = DATE('now', 'localtime')"
                ).fetchone()[0]
                top_item_row = conn.execute(
                    """
                    SELECT item_name, SUM(quantity) AS qty
                    FROM order_items
                    GROUP BY item_name
                    ORDER BY qty DESC
                    LIMIT 1
                    """
                ).fetchone()
                result["sales"] = float(sales or 0.0)
                result["orders"] = int(orders or 0)
                if top_item_row:
                    result["top_item"] = top_item_row["item_name"]
        except sqlite3.Error as error:
            print(f"[DB SALES SUMMARY ERROR] {error}")
        return result

    def add_menu_item(self, payload):
        try:
            with self.connect() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    """
                    INSERT INTO menu_items (
                        name, category, has_sizes, price_small, price_medium, price_large,
                        price_fixed, available
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        payload["name"],
                        payload["category"],
                        payload["has_sizes"],
                        payload["price_small"],
                        payload["price_medium"],
                        payload["price_large"],
                        payload["price_fixed"],
                        payload["available"],
                    ),
                )
                item_id = cursor.lastrowid
                cursor.execute("DELETE FROM item_sizes WHERE item_id = ?", (item_id,))
                if payload["has_sizes"] == 1:
                    cursor.executemany(
                        "INSERT INTO item_sizes(item_id, size_label, price) VALUES (?, ?, ?)",
                        [
                            (item_id, "Small", payload["price_small"]),
                            (item_id, "Medium", payload["price_medium"]),
                            (item_id, "Large", payload["price_large"]),
                        ],
                    )
                conn.commit()
                return True
        except sqlite3.Error as error:
            print(f"[DB ADD MENU ITEM ERROR] {error}")
            return False

    def update_menu_item(self, item_id, payload):
        try:
            with self.connect() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    """
                    UPDATE menu_items
                    SET name = ?, category = ?, has_sizes = ?, price_small = ?, price_medium = ?,
                        price_large = ?, price_fixed = ?, available = ?
                    WHERE id = ?
                    """,
                    (
                        payload["name"],
                        payload["category"],
                        payload["has_sizes"],
                        payload["price_small"],
                        payload["price_medium"],
                        payload["price_large"],
                        payload["price_fixed"],
                        payload["available"],
                        item_id,
                    ),
                )
                cursor.execute("DELETE FROM item_sizes WHERE item_id = ?", (item_id,))
                if payload["has_sizes"] == 1:
                    cursor.executemany(
                        "INSERT INTO item_sizes(item_id, size_label, price) VALUES (?, ?, ?)",
                        [
                            (item_id, "Small", payload["price_small"]),
                            (item_id, "Medium", payload["price_medium"]),
                            (item_id, "Large", payload["price_large"]),
                        ],
                    )
                conn.commit()
                return True
        except sqlite3.Error as error:
            print(f"[DB UPDATE MENU ITEM ERROR] {error}")
            return False

    def delete_menu_item(self, item_id):
        try:
            with self.connect() as conn:
                conn.execute("DELETE FROM menu_items WHERE id = ?", (item_id,))
                conn.commit()
                return True
        except sqlite3.Error as error:
            print(f"[DB DELETE MENU ITEM ERROR] {error}")
            return False
