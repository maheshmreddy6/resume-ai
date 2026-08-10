from pathlib import Path
import shutil

from fastapi import UploadFile, HTTPException

from app.config import settings


ALLOWED_EXTENSIONS = {".pdf"}
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5 MB


class FileService:

    @staticmethod
    async def save_upload(
        file: UploadFile,
        resume_id: str
    ) -> tuple[str, int]:

        # 1. Validate filename
        if not file.filename:
            raise HTTPException(
                status_code=400,
                detail="Filename is required."
            )

        # 2. Validate extension
        extension = Path(file.filename).suffix.lower()

        if extension not in ALLOWED_EXTENSIONS:
            raise HTTPException(
                status_code=400,
                detail="Only PDF files are allowed."
            )

        # 3. Create upload directory
        upload_dir = Path(settings.UPLOAD_FOLDER)

        upload_dir.mkdir(
            parents=True,
            exist_ok=True
        )

        # 4. Generate server-side filename
        safe_filename = f"{resume_id}{extension}"

        destination = upload_dir / safe_filename

        # 5. Determine file size
        file.file.seek(0, 2)
        size = file.file.tell()
        file.file.seek(0)

        # 6. Validate empty file
        if size == 0:
            raise HTTPException(
                status_code=400,
                detail="Uploaded file is empty."
            )

        # 7. Validate maximum file size
        if size > MAX_FILE_SIZE:
            raise HTTPException(
                status_code=400,
                detail="File exceeds 5 MB limit."
            )

        # 8. Save file
        with destination.open("wb") as buffer:
            shutil.copyfileobj(
                file.file,
                buffer
            )

        return str(destination), size
