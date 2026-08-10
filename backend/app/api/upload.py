from datetime import datetime, timezone
from uuid import uuid4
from pathlib import Path
import re

from fastapi import APIRouter, UploadFile, File, Depends

from app.models.resume import ResumeResponse
from app.security import get_current_user
from app.services.file_service import FileService
from app.services.pdf_parser import PDFParser
from app.services.chunk_service import ChunkService
from app.services.rag_ingestion import RAGIngestion


router = APIRouter(
    prefix="/upload",
    tags=["Upload"]
)


@router.post(
    "/",
    response_model=ResumeResponse
)
async def upload_resume(
    file: UploadFile = File(...),
    current_user: str = Depends(get_current_user),
):

    # 1. Generate unique resume ID based on the uploaded filename
    original_name = Path(file.filename).stem if file.filename else "resume"
    safe_name = re.sub(r'[^a-zA-Z0-9_-]', '_', original_name).lower()
    resume_id = f"{safe_name}_{uuid4().hex}"

    # 2. Save PDF
    file_path, file_size = await FileService.save_upload(
        file,
        resume_id
    )

    # 3. Extract PDF text
    resume_text = PDFParser.extract_text(
        file_path
    )

    # 4. Handle PDF with no extractable text
    if not resume_text:
        return ResumeResponse(
            resume_id=resume_id,
            filename=file.filename,
            file_size=file_size,
            upload_time=datetime.now(timezone.utc),
            characters_extracted=0,
            chunks_created=0,
            stored_chunks=0,
            message=(
                "PDF uploaded, but no "
                "extractable text was found."
            )
        )

    # 5. Create chunks
    chunks = ChunkService().create_chunks(
        text=resume_text,
        resume_id=resume_id
    )

    # 6. Generate embeddings + store vectors
    storage_result = RAGIngestion().process_chunks(
        chunks
    )

    # 6.5 Persist resume metadata with owner
    from app.services.resume_service import ResumeService

    resume_service = ResumeService()

    resume_record = resume_service.create_resume(
        resume_id=resume_id,
        username=current_user,
        filename=file.filename,
        stored_filename=Path(file_path).name,
        file_size=file_size,
        upload_time=datetime.now(timezone.utc),
        characters_extracted=len(resume_text),
        chunks_created=len(chunks),
        stored_chunks=0,
        message="Resume uploaded and indexed successfully."
    )

    # 7. Return API response
    return ResumeResponse(
        resume_id=resume_id,
        filename=file.filename,
        file_size=file_size,
        upload_time=datetime.now(timezone.utc),
        characters_extracted=len(resume_text),
        chunks_created=len(chunks),
        stored_chunks=storage_result["stored_chunks"],
        message="Resume uploaded and indexed successfully."
    )