from fastapi import APIRouter, Depends, HTTPException
from app.security import get_current_user
from app.services.langsmith_adapter import log_analysis_run, LangSmithNotAvailable

router = APIRouter(prefix="/langsmith", tags=["LangSmith"])


@router.post("/test")
def test_langsmith(current_user: str = Depends(get_current_user)):
    """Create a small test run in LangSmith to verify connectivity.

    Returns the LangSmith run id and status if logging succeeded.
    """
    resume_id = f"test_run_for_{current_user}"
    job_description = "This is a LangSmith connectivity test run from Resume-AI."
    result = {"summary": "test", "engine": "langchain", "ok": True}

    try:
        resp = log_analysis_run(
            engine="langchain",
            resume_id=resume_id,
            job_description=job_description,
            result=result,
            metadata={"tester": current_user},
        )
        return {"status": "ok", "langsmith": resp}

    except LangSmithNotAvailable as e:
        raise HTTPException(status_code=503, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"LangSmith logging failed: {e}")
