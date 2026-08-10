import sqlite3
from pathlib import Path
from datetime import datetime

from app.config import settings
from fastapi import HTTPException


class ResumeService:

    def __init__(self):
        self.db_path = Path(settings.RESUMES_DB)
        if self.db_path.parent:
            self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._ensure_tables()

    def _connect(self):
        return sqlite3.connect(self.db_path)

    def _ensure_tables(self):
        with self._connect() as connection:
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS resumes (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    resume_id TEXT UNIQUE NOT NULL,
                    username TEXT NOT NULL,
                    filename TEXT,
                    stored_filename TEXT,
                    file_size INTEGER,
                    upload_time TEXT,
                    characters_extracted INTEGER,
                    chunks_created INTEGER,
                    stored_chunks INTEGER,
                    message TEXT
                )
                """
            )
            connection.commit()

    def create_resume(self, *, resume_id: str, username: str, filename: str, stored_filename: str, file_size: int, upload_time: datetime, characters_extracted: int, chunks_created: int, stored_chunks: int, message: str):
        with self._connect() as connection:
            try:
                connection.execute(
                    "INSERT INTO resumes (resume_id, username, filename, stored_filename, file_size, upload_time, characters_extracted, chunks_created, stored_chunks, message) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                    (
                        resume_id,
                        username,
                        filename,
                        stored_filename,
                        file_size,
                        upload_time.isoformat() if isinstance(upload_time, datetime) else str(upload_time),
                        characters_extracted,
                        chunks_created,
                        stored_chunks,
                        message,
                    ),
                )
                connection.commit()
            except sqlite3.IntegrityError:
                raise HTTPException(status_code=400, detail="Resume ID already exists")

        return self.get_by_resume_id(resume_id)

    def list_by_user(self, username: str):
        with self._connect() as connection:
            cursor = connection.execute(
                "SELECT resume_id, filename, stored_filename, file_size, upload_time, characters_extracted, chunks_created, stored_chunks, message FROM resumes WHERE username = ? ORDER BY upload_time DESC",
                (username,),
            )
            rows = cursor.fetchall()

        result = []
        for row in rows:
            result.append({
                "resume_id": row[0],
                "filename": row[1],
                "stored_filename": row[2],
                "file_size": row[3],
                "upload_time": row[4],
                "characters_extracted": row[5],
                "chunks_created": row[6],
                "stored_chunks": row[7],
                "message": row[8],
            })
        return result

    def get_by_resume_id(self, resume_id: str):
        with self._connect() as connection:
            cursor = connection.execute(
                "SELECT resume_id, username, filename, stored_filename, file_size, upload_time, characters_extracted, chunks_created, stored_chunks, message FROM resumes WHERE resume_id = ?",
                (resume_id,),
            )
            row = cursor.fetchone()

        if not row:
            return None

        return {
            "resume_id": row[0],
            "username": row[1],
            "filename": row[2],
            "stored_filename": row[3],
            "file_size": row[4],
            "upload_time": row[5],
            "characters_extracted": row[6],
            "chunks_created": row[7],
            "stored_chunks": row[8],
            "message": row[9],
        }

    def count_resumes(self):
        with self._connect() as connection:
            cursor = connection.execute("SELECT COUNT(1) FROM resumes")
            row = cursor.fetchone()

        return int(row[0] or 0)
