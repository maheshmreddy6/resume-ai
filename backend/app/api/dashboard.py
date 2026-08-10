from pathlib import Path
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse

from app.config import settings
from app.security import get_current_user
from app.services.user_service import UserService
from app.services.resume_service import ResumeService

router = APIRouter(
    prefix="/dashboard",
    tags=["Dashboard"],
)

user_service = UserService()


@router.get("/list")
def list_resumes(current_user: str = Depends(get_current_user)):
    # Use persisted resume metadata and filter by current user
    resume_service = ResumeService()
    resumes = resume_service.list_by_user(current_user)

    # Ensure upload_time is ISO string if present
    for r in resumes:
        if isinstance(r.get("upload_time"), str):
            continue

    return {"resumes": resumes}


@router.get("/download/{resume_id}")
def download_resume(resume_id: str, current_user: str = Depends(get_current_user)):
    # Use resume service to locate the stored filename and ensure ownership
    resume_service = ResumeService()
    record = resume_service.get_by_resume_id(resume_id)

    if not record:
        raise HTTPException(status_code=404, detail="Resume not found")

    if record["username"] != current_user:
        raise HTTPException(status_code=403, detail="Not authorized to access this resume")

    upload_dir = Path(settings.UPLOAD_FOLDER)
    candidate = upload_dir / record["stored_filename"]

    if not candidate.exists() or not candidate.is_file():
        raise HTTPException(status_code=404, detail="Stored file not found")

    return FileResponse(path=candidate, filename=record.get("stored_filename") or record.get("filename"), media_type="application/pdf")


@router.get("/stats")
def dashboard_stats(current_user: str = Depends(get_current_user)):
    resume_service = ResumeService()
    resume_count = resume_service.count_resumes()

    user_count = user_service.count_users()

    return {
        "resumes": resume_count,
        "users": user_count,
    }
