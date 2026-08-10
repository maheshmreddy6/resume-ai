from pydantic import BaseModel


class ResumeChunk(BaseModel):
    chunk_id: int
    resume_id: str
    content: str
    character_count: int
