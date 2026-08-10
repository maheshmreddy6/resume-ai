"""
LangSmith adapter for Resume-AI.

This module provides a minimal wrapper around the LangSmith SDK so the
app can log analysis runs and simple evaluation artifacts. The adapter is
optional: if the langsmith package is not installed or no LANGSMITH_API_KEY
is provided in the environment, the adapter functions raise an informative
error or become no-ops.

Install the SDK (optional):
    python -m pip install langsmith

See LangSmith docs for more advanced usage (runs, traces, evaluations).
"""
import os
from inspect import signature
from typing import Any, Dict, Optional
from uuid import uuid4
import logging

from app.config import settings

logger = logging.getLogger("langsmith_adapter")

try:
    import langsmith  # type: ignore
    from langsmith import Client as LangSmithClient  # type: ignore
except Exception:  # pragma: no cover - import-time fallback
    langsmith = None
    LangSmithClient = None


class LangSmithNotAvailable(Exception):
    pass


def _supports_param(func: Any, param_name: str) -> bool:
    try:
        return param_name in signature(func).parameters
    except (TypeError, ValueError):
        return False


def _ensure_client(api_key: Optional[str] = None) -> Any:
    """Return a LangSmith client or raise LangSmithNotAvailable.

    The function uses settings.LANGSMITH_API_KEY when api_key is None and will
    optionally pass endpoint information if settings.LANGSMITH_ENDPOINT is set.
    """
    if not langsmith or LangSmithClient is None:
        raise LangSmithNotAvailable(
            "LangSmith SDK is not installed. Install with: python -m pip install langsmith"
        )

    key = api_key or settings.LANGSMITH_API_KEY
    if not key:
        raise LangSmithNotAvailable(
            "LANGSMITH_API_KEY not set in .env or environment. Set it to enable LangSmith logging."
        )

    client_kwargs: Dict[str, Any] = {}
    if _supports_param(LangSmithClient.__init__, "api_key"):
        client_kwargs["api_key"] = key
    else:
        os.environ.setdefault("LANGSMITH_API_KEY", key)

    if settings.LANGSMITH_ENDPOINT:
        if _supports_param(LangSmithClient.__init__, "api_url"):
            client_kwargs["api_url"] = settings.LANGSMITH_ENDPOINT
        elif _supports_param(LangSmithClient.__init__, "endpoint"):
            client_kwargs["endpoint"] = settings.LANGSMITH_ENDPOINT
        else:
            os.environ.setdefault("LANGSMITH_API_URL", settings.LANGSMITH_ENDPOINT)
            os.environ.setdefault("LANGSMITH_ENDPOINT", settings.LANGSMITH_ENDPOINT)

    try:
        return LangSmithClient(**client_kwargs)
    except TypeError:
        # Older/newer SDKs may expect no args, or may rely on env vars.
        try:
            return LangSmithClient()
        except Exception as exc:
            raise LangSmithNotAvailable(
                "Unable to initialize LangSmith client. Check your SDK version and configuration."
            ) from exc


def log_analysis_run(
    engine: str,
    resume_id: str,
    job_description: str,
    result: Dict[str, Any],
    metadata: Optional[Dict[str, Any]] = None,
    retrieved_docs: Optional[list] = None,
    prompt: Optional[str] = None,
    llm_response: Optional[Dict[str, Any]] = None,
    latency_ms: Optional[int] = None,
    request_id: Optional[str] = None,
    api_key: Optional[str] = None,
) -> Dict[str, Any]:
    """Log an analysis run to LangSmith and return a small summary dict.

    Enhanced logging: logs retrieved docs, prompt, llm response, latency and request id when available.
    Respects settings.LANGSMITH_TRACING to allow toggling tracing on/off.
    """
    # Respect the global tracing toggle; do nothing if disabled
    if not getattr(settings, "LANGSMITH_TRACING", False):
        logger.info(
            "LangSmith tracing is disabled (LANGSMITH_TRACING=False). Skipping log for resume %s",
            resume_id,
        )
        return {"status": "tracing_disabled"}

    client = _ensure_client(api_key=api_key)

    tags = ["resume-ai", engine]
    metadata = {**(metadata or {}), "resume_id": resume_id}
    if settings.LANGSMITH_PROJECT:
        metadata["project"] = settings.LANGSMITH_PROJECT
        tags.append(settings.LANGSMITH_PROJECT)

    run_id = str(uuid4())
    inputs: Dict[str, Any] = {
        "resume_id": resume_id,
        "job_description": job_description,
        "engine": engine,
    }
    if request_id:
        inputs["request_id"] = str(request_id)
    if prompt:
        inputs["prompt"] = prompt
    if metadata:
        inputs["metadata"] = metadata
    if retrieved_docs:
        try:
            docs_text = "\n\n".join(str(d) for d in retrieved_docs)[:50000]
            inputs["retrieved_docs"] = docs_text
        except Exception:
            pass
    if llm_response is not None:
        inputs["llm_response"] = llm_response
    if latency_ms is not None:
        inputs["latency_ms"] = latency_ms

    outputs: Dict[str, Any] = {"analysis_result": result}
    if llm_response is not None:
        outputs["llm_response"] = llm_response
    if latency_ms is not None:
        outputs["latency_ms"] = latency_ms

    run_kwargs: Dict[str, Any] = {
        "id": run_id,
        "name": f"resume_analysis:{resume_id}",
        "run_type": "llm",
        "inputs": inputs,
        "outputs": outputs,
        "tags": tags,
    }
    if settings.LANGSMITH_PROJECT:
        run_kwargs["project_name"] = settings.LANGSMITH_PROJECT

    try:
        create_run_sig = signature(client.create_run)
        create_run_params = create_run_sig.parameters

        if "inputs" in create_run_params and "run_type" in create_run_params:
            client.create_run(**run_kwargs)
            logger.info("Logged LangSmith run %s for resume %s", run_id, resume_id)
            return {"langsmith_run_id": run_id, "status": "logged"}

        fallback_kwargs: Dict[str, Any] = {
            "name": run_kwargs["name"],
            "tags": tags,
            "metadata": metadata,
        }
        if "inputs" in create_run_params:
            fallback_kwargs["inputs"] = inputs
        if "outputs" in create_run_params:
            fallback_kwargs["outputs"] = outputs
        if "project_name" in create_run_params and settings.LANGSMITH_PROJECT:
            fallback_kwargs["project_name"] = settings.LANGSMITH_PROJECT

        run = client.create_run(**fallback_kwargs)
        run_id = getattr(run, "id", run_id)
        logger.info("Logged LangSmith run %s for resume %s", run_id, resume_id)
        return {"langsmith_run_id": run_id, "status": "logged"}

    except Exception as e:
        logger.exception("Failed to log analysis run to LangSmith: %s", e)
        raise
