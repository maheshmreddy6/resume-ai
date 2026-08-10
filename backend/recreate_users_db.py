"""
Recreate users.db safely for development: moves existing users.db to a timestamped backup
and creates a fresh users.db by instantiating UserService (which seeds admin/admin123).

Run from backend folder with the same interpreter used for the app/venv:
    python recreate_users_db.py

Warning: this will remove access to existing users unless you restore the backup.
"""
from pathlib import Path
import shutil
from datetime import datetime

BACKEND_DIR = Path(__file__).resolve().parent
USERS_DB = BACKEND_DIR / "users.db"

if USERS_DB.exists():
    ts = datetime.now().strftime("%Y%m%d%H%M%S")
    backup = BACKEND_DIR / f"users.db.bak_{ts}"
    print(f"Backing up existing users.db -> {backup}")
    shutil.move(str(USERS_DB), str(backup))
else:
    print("No existing users.db found; creating a new one.")

# Instantiate UserService to recreate DB and seed default admin
try:
    from app.services.user_service import UserService

    us = UserService()
    print("Created new users.db and seeded default admin (username=admin, ******")
except Exception as e:
    print("Failed to create users.db:", e)
    raise
