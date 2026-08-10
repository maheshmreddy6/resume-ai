from pydantic import BaseModel, Field


class JobRequest(BaseModel):
    resume_id: str = Field(
        ..., 
        min_length=1,
        description="ID of the uploaded resume"
    )

    job_description: str = Field(
        ..., 
        min_length=20,
        description="Job description to compare against the resume"
    )


class AnalysisResponse(BaseModel):
    resume_id: str
    match_score: str
    strengths: list[str]
    missing_skills: list[str]
    interview_questions: list[str]
    summary: str
