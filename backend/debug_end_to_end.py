"""
Debug script: end-to-end flow (login -> upload -> analyze) using FastAPI TestClient.
Run from the backend folder using the virtualenv Python:

D:\resume-ai\backend\venv\Scripts\python.exe debug_end_to_end.py [optional-pdf-path]

If an optional PDF path is provided, it will be uploaded; otherwise a small synthetic PDF-like bytes object is used.

The script prints HTTP responses and inspects the resumes and users SQLite DBs.
"""

from pathlib import Path
import io
import sys
import sqlite3
import json
import traceback

from fastapi.testclient import TestClient
from app.main import app

# Configuration
USERNAME = "admin"
PASSWORD = "admin123"
JOB_DESCRIPTION = (
    "We need a senior Python developer with experience in FastAPI, Docker, and machine learning."
)
BACKEND_DIR = Path(__file__).resolve().parent
USERS_DB = BACKEND_DIR / "users.db"
RESUMES_DB = BACKEND_DIR / "resumes.db"

client = TestClient(app)


def pretty(obj):
    try:
        return json.dumps(obj, indent=2, default=str)
    except Exception:
        return str(obj)


def query_db(db_path: Path, query: str, params=()):
    if not db_path.exists():
        print(f"DB not found: {db_path}")
        return []
    try:
        conn = sqlite3.connect(str(db_path))
        cur = conn.execute(query, params)
        rows = cur.fetchall()
        cols = [d[0] for d in cur.description] if cur.description else []
        conn.close()
        result = [dict(zip(cols, row)) for row in rows]
        return result
    except Exception:
        print("Failed to query DB:")
        traceback.print_exc()
        return []


def main(pdf_path_arg=None):
    try:
        print("1) Logging in...")
        r = client.post(
            "/auth/login",
            data={"username": USERNAME, "password": PASSWORD},
        )
        print("/auth/login ->", r.status_code)
        print(r.text)

        if r.status_code != 200:
            print("Login failed; aborting.")
            return

        token = r.json().get("access_token")
        headers = {"Authorization": f"******"}

        # Prepare file
        if pdf_path_arg and Path(pdf_path_arg).exists():
            file_obj = open(pdf_path_arg, "rb")
            filename = Path(pdf_path_arg).name
            print(f"Using provided file: {pdf_path_arg}")
        else:
            # Minimal PDF-like bytes (not a full PDF, but our extraction handles small samples in tests)
            file_obj = io.BytesIO(b"%PDF-1.4\n%\xe2\xe3\xcf\xd3\n1 0 obj\n<< /Type /Catalog >>\nendobj\n")
            filename = "sample_resume.pdf"
            print("Using synthetic PDF bytes")

        print("2) Uploading file...")
        files = {"file": (filename, file_obj, "application/pdf")}
        r2 = client.post("/upload/", headers=headers, files=files)
        print("/upload/ ->", r2.status_code)
        try:
            print(pretty(r2.json()))
        except Exception:
            print(r2.text)

        if r2.status_code != 200:
            print("Upload failed; aborting.")
            return

        resume_resp = r2.json()
        resume_id = resume_resp.get("resume_id")
        print(f"Uploaded resume_id = {resume_id}")

        print("3) Calling analyze endpoint...")
        r3 = client.post(
            "/analyze/",
            headers={"Authorization": f"******", "Content-Type": "application/json"},
            json={"resume_id": resume_id, "job_description": JOB_DESCRIPTION},
        )
        print("/analyze/ ->", r3.status_code)
        try:
            print(pretty(r3.json()))
        except Exception:
            print(r3.text)

        # Inspect databases
        print("\n4) Users DB rows (users.db):")
        users = query_db(USERS_DB, "SELECT id, username, created_at FROM users ORDER BY id DESC LIMIT 10")
        print(pretty(users))

        print("\n5) Resumes DB rows (resumes.db) for this user:")
        resumes = query_db(
            RESUMES_DB,
            "SELECT resume_id, username, filename, stored_filename, file_size, upload_time, characters_extracted, chunks_created FROM resumes WHERE username = ? ORDER BY upload_time DESC LIMIT 10",
            (USERNAME,),
        )
        print(pretty(resumes))

    except Exception:
        print("Unhandled exception during debug run:")
        traceback.print_exc()
    finally:
        try:
            if hasattr(file_obj, "close"):
                file_obj.close()
        except Exception:
            pass


if __name__ == "__main__":
    arg = sys.argv[1] if len(sys.argv) > 1 else None
    main(arg)
