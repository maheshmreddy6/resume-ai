import sqlite3
from pathlib import Path

from fastapi import HTTPException

from app.config import settings
from app.security import hash_password


class UserService:

    def __init__(self):
        self.db_path = Path(settings.USERS_DB)
        if self.db_path.parent:
            self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._ensure_tables()
        self._ensure_default_admin()

    def _connect(self):
        return sqlite3.connect(self.db_path)

    def _ensure_tables(self):
        with self._connect() as connection:
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE NOT NULL,
                    password TEXT NOT NULL,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
                """
            )
            connection.commit()

    def _ensure_default_admin(self):
        if not self.get_user("admin"):
            self.create_user("admin", "admin123")

    def get_user(self, username: str):
        with self._connect() as connection:
            cursor = connection.execute(
                "SELECT id, username, password FROM users WHERE username = ?",
                (username,),
            )
            row = cursor.fetchone()

        if not row:
            return None

        return {
            "id": row[0],
            "username": row[1],
            "password": row[2],
        }

    def count_users(self) -> int:
        with self._connect() as connection:
            cursor = connection.execute(
                "SELECT COUNT(1) FROM users"
            )
            row = cursor.fetchone()

        return int(row[0] or 0)

    def create_user(self, username: str, password: str):
        username = username.strip()
        if not username or not password:
            raise HTTPException(
                status_code=400,
                detail="Username and password are required.",
            )

        if self.get_user(username):
            raise HTTPException(
                status_code=400,
                detail="Username already exists.",
            )

        hashed_password = hash_password(password)

        with self._connect() as connection:
            connection.execute(
                "INSERT INTO users (username, password) VALUES (?, ?)",
                (username, hashed_password),
            )
            connection.commit()

        return self.get_user(username)
