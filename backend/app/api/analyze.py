import logging

from fastapi import APIRouter, HTTPException, Depends

from app.models.job import JobRequest, AnalysisResponse
from app.security import get_current_user
from app.services.langsmith_adapter import log_analysis_run
from app.services.rag_service import RAGService
from app.services.llm_service import LLMService


router = APIRouter(
    prefix="/analyze",
    tags=["Analyze"]
)


@router.post(
    "/",
    response_model=AnalysisResponse
)
async def analyze_resume(
    request: JobRequest,
    current_user: str = Depends(get_current_user),
):

    # 1. Retrieve relevant resume context
    rag = RAGService()

    context = rag.retrieve_resume_context(
        job_description=request.job_description,
        resume_id=request.resume_id
    )

    if not context:
        raise HTTPException(
            status_code=404,
            detail=(
                "No indexed resume found "
                f"for resume_id: {request.resume_id}"
            )
        )

    # 2. Analyze using LLM
    llm = LLMService()

    result = llm.analyze_resume(
        request.job_description,
        context
    )

    try:
        log_analysis_run(
            engine="openai",
            resume_id=request.resume_id,
            job_description=request.job_description,
            result=result,
            metadata={"user": current_user},
            retrieved_docs=[context],
            prompt=request.job_description,
            llm_response={"summary": result.get("summary")},
        )
    except Exception as e:
        logging.getLogger("langsmith_adapter").exception(
            "LangSmith logging failed during analysis: %s", e
        )

    # 3. Return structured response
    return AnalysisResponse(
        resume_id=request.resume_id,
        match_score=result.get(
            "match_score",
            "0%"
        ),
        strengths=result.get(
            "strengths",
            []
        ),
        missing_skills=result.get(
            "missing_skills",
            []
        ),
        interview_questions=result.get(
            "interview_questions",
            []
        ),
        summary=result.get(
            "summary",
            ""
        )
    )