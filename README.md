# Coffee POS System

A desktop Point-of-Sale (POS) system for a coffee shop built with Python, Tkinter, and SQLite.

## Features

- Secure login with role support (admin/cashier)
- Category-based menu browsing (Hot Drinks, Cold Drinks, Snacks, Desserts, Meals)
- Responsive menu layout that adjusts to available space
- Current order panel with scrolling and quantity controls
- Payment methods: Cash, E-Wallet, Card
- Receipt generation with payment method details
- Reopen and print the latest receipt after closing it
- Order history view
- Admin menu management tools

## Tech Stack

- Python 3
- Tkinter (GUI)
- SQLite

## Project Structure

```text
coffee_pos/
|- main.py
|- config.py
|- database.py
|- order_history.py
|- coffee_pos.db
|- ui/
|  |- login.py
|  |- main_layout.py
|  |- left_panel.py
|  |- center_panel.py
|  |- right_panel.py
|  |- receipt.py
|  |- discount.py
|  |- size_select.py
|  |- admin.py
|- .gitignore
|- README.md
```

## Requirements

- Python 3.10+ recommended
- Tkinter included in Python installation

Check Tkinter support:

```bash
python -m tkinter
```

If a small test window appears, Tkinter is working.

## Run Locally

1. Open terminal in the project folder.
2. Create a virtual environment:

```powershell
python -m venv .venv
```

3. Activate it:

```powershell
.venv\Scripts\Activate.ps1
```

4. (Optional) Install dependencies if you have `requirements.txt`:

```powershell
pip install -r requirements.txt
```

5. Start the app:

```powershell
python main.py
```

## Default Login Credentials

- Admin
  - Username: `admin`
  - PIN: `1234`
- Cashier
  - Username: `cashier1`
  - PIN: `0000`

Change these before production use.

## Database

- Database file: `coffee_pos.db`
- If missing, tables are initialized automatically at startup by `database.py`.

## Publish to GitHub

After creating an empty repository on GitHub, run:

```powershell
git init
git add .
git commit -m "Initial commit: Coffee POS system"
git branch -M main
git remote add origin https://github.com/khiroez/coffee_pos.git
git push -u origin main
```

## Notes

- The main POS window uses native OS controls (minimize, maximize, close).
- Receipts include payment method details for tracking Cash, E-Wallet, and Card orders.

# Coffee POS System

A desktop Point-of-Sale (POS) system for a coffee shop built with Python, Tkinter, and SQLite.

## Features

- Secure login (admin/cashier roles)
- Menu by category (Hot Drinks, Cold Drinks, Snacks, Desserts, Meals)
- Responsive menu grid based on available space
- Current order management (add/remove/update quantities)
- Payment methods:
  - Cash
  - E-Wallet
  - Card
- Receipt generation and printing
- Reopen last receipt after order placement
- Order history view
- Admin panel for menu management

## Tech Stack

- Python 3.x
- Tkinter (GUI)
- SQLite (`coffee_pos.db`)

## Project Structure

```text
coffee_pos/
├── main.py
├── config.py
├── database.py
├── order_history.py
├── coffee_pos.db
├── ui/
│   ├── login.py
│   ├── main_layout.py
│   ├── left_panel.py
│   ├── center_panel.py
│   ├── right_panel.py
│   ├── receipt.py
│   ├── discount.py
│   ├── size_select.py
│   └── admin.py
└── README.md

##Requirements

Python 3.10+ recommended
Tkinter available in your Python installation

Check Tkinter:
python -m tkinter
If a small window opens, Tkinter is installed.

Setup (Local)
Clone the repository:
git clone https://github.com/khiroez/coffee_pos.git
cd coffee_pos
Create and activate virtual environment:
Windows (PowerShell)
python -m venv .venv
.venv\Scripts\Activate.ps1
Windows (CMD)
python -m venv .venv
.venv\Scripts\activate.bat
Install dependencies (if requirements.txt exists):
pip install -r requirements.txt
Run the app:
python main.py
Default Login Accounts
Change these immediately in production use.

Admin

Username: admin
PIN: 1234
Cashier

Username: cashier1
PIN: 0000
Database
The system uses SQLite with file:

coffee_pos.db
If the DB is missing, tables are initialized automatically on startup by database.py.

GitHub Publish Steps
From project root:
