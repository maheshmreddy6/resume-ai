from datetime import datetime
from pydantic import BaseModel


class ResumeResponse(BaseModel):
    resume_id: str
    filename: str
    file_size: int
    upload_time: datetime
    characters_extracted: int
    chunks_created: int
    stored_chunks: int
    message: str


class ResumeContextResponse(BaseModel):
    resume_id: str
    filename: str
