"""
LangGraph integration adapter (example).

LangGraph is a separate project with its own APIs. This file provides a
lightweight adapter that attempts to import langgraph and exposes
placeholder functions for ingestion and analysis. If langgraph is not
installed, the functions raise an informative ImportError.

To enable LangGraph integration, install the library the project
maintainers provide (example):
    pip install langgraph

Because LangGraph APIs vary over time, this adapter deliberately keeps
implementation minimal and focuses on clear error messages and examples
for how to wire a LangGraph pipeline into this app.
"""
from typing import List

from app.config import settings


class LangGraphNotAvailable(Exception):
    pass


try:
    import langgraph  # type: ignore
except Exception:
    langgraph = None


def _ensure_available():
    if not langgraph:
        raise LangGraphNotAvailable(
            "LangGraph is not installed. Install it with `pip install langgraph` "
            "and consult its docs for configuration."
        )


def ingest_with_langgraph(chunks: List[str], resume_id: str):
    """Example placeholder: show how an ingestion step could be called.

    This does not implement a concrete LangGraph pipeline because the
    library's API is external to this repo and subject to change.
    """
    _ensure_available()

    # Example pseudo-code for a LangGraph ingestion pipeline
    # The real API will differ; consult LangGraph docs and replace this
    # block with the correct calls.
    
    # graph = langgraph.Client(api_key=settings.LANGGRAPH_API_KEY)
    # for i, chunk in enumerate(chunks):
    #     graph.create_node(
    #         type="resume_chunk",
    #         id=f"{resume_id}_chunk_{i}",
    #         text=chunk,
    #         metadata={"resume_id": resume_id, "chunk_id": i}
    #     )
    
    return {"stored_chunks": len(chunks), "note": "Placeholder: implement LangGraph API calls"}


def analyze_with_langgraph(resume_id: str, job_description: str):
    """Example placeholder for running a LangGraph-powered analysis.

    Replace with concrete LangGraph query/agent code after installing
    and reading LangGraph's docs.
    """
    _ensure_available()

    # Pseudo-code:
    # graph = langgraph.Client(api_key=settings.LANGGRAPH_API_KEY)
    # nodes = graph.query_nodes(type="resume_chunk", where={"resume_id": resume_id})
    # response = graph.run_agent(prompt=job_description, nodes=nodes)
    
    return {"summary": "Placeholder: LangGraph analysis not implemented in adapter."}
