"""
LangChain integration helpers for the Resume-AI app.

This module provides example functions that show how to build a simple
retrieval + QA flow using LangChain. The functions are defensive: if
langchain is not installed they fall back to the app's existing LLMService
and VectorStore behaviour or raise a clear ImportError.

Install langchain (already present in requirements) and its OpenAI
support if you want to use these helpers directly:
    pip install langchain openai chromadb

Note: This file is an example integration. The app's existing
RAGIngestion + LLMService pipeline remains the canonical path and
continues to be used by the app unless you wire these helpers into
endpoints explicitly.
"""
from typing import List

from app.services.embedding_service import EmbeddingService
from app.services.vector_store import VectorStore
from app.services.llm_service import LLMService
from app.config import settings


def _get_top_documents_from_vectorstore(resume_id: str, query_embedding: List[float], top_k: int = 5) -> List[str]:
    """Return top-k documents (strings) for a resume using the existing VectorStore."""
    vs = VectorStore()
    results = vs.search(query_embedding, resume_id=resume_id, limit=top_k)

    # chroma returns nested lists for documents; be defensive when extracting
    documents = []
    try:
        # results['documents'] is typically [[doc1, doc2, ...]]
        documents = results.get("documents", [[]])[0]
    except Exception:
        # Fallback: try accessing 'documents' attribute
        try:
            documents = results["documents"][0]
        except Exception:
            documents = []

    return documents


def analyze_with_langchain(resume_id: str, job_description: str, top_k: int = 5):
    """Attempt to use LangChain for retrieval+QA if langchain is available.

    If langchain isn't installed, gracefully fall back to the app's
    LLMService + VectorStore flow.
    """
    try:
        # Local imports to avoid forcing langchain as a hard dependency
        from langchain.llms import OpenAI as LCOpenAI
        from langchain.chains import RetrievalQA
        from langchain.embeddings import OpenAIEmbeddings
        from langchain.vectorstores import Chroma as LCChroma
    except Exception as e:
        # LangChain not available; fallback to LLMService-based analysis
        llm = LLMService()
        emb = EmbeddingService()
        query_emb = emb.create_embedding(job_description)
        docs = _get_top_documents_from_vectorstore(resume_id, query_emb, top_k=top_k)
        # Concatenate docs into context and call existing LLMService
        resume_context = "\n\n".join(docs)
        return llm.analyze_resume(job_description, resume_context)

    # LangChain is available — construct a Chroma-backed retriever and chain.
    # Note: this uses Chroma's disk persistence directory from settings.CHROMA_DB
    try:
        embeddings = OpenAIEmbeddings(openai_api_key=settings.OPENAI_API_KEY)
    except Exception:
        # Fall back to constructing without explicit api key (let env provide it)
        embeddings = OpenAIEmbeddings()

    chroma = LCChroma(persist_directory=settings.CHROMA_DB, collection_name="resume_embeddings", embedding_function=embeddings)

    retriever = chroma.as_retriever(search_kwargs={"k": top_k})

    # Use LangChain's OpenAI wrapper for the LLM
    try:
        lc_llm = LCOpenAI(temperature=0)
    except Exception:
        # If construction fails, fall back to our LLMService wrapper
        llm = LLMService()
        query_emb = EmbeddingService().create_embedding(job_description)
        docs = _get_top_documents_from_vectorstore(resume_id, query_emb, top_k=top_k)
        resume_context = "\n\n".join(docs)
        return llm.analyze_resume(job_description, resume_context)

    # Optionally attach LangSmith tracing via LangChain callbacks if available.
    callbacks = []
    try:
        # LangChain's LangSmith callback name varies by version. Try common handlers.
        try:
            from langchain.callbacks.langsmith import LangSmithTracer  # type: ignore
            tracer = LangSmithTracer(api_key=settings.LANGSMITH_API_KEY)
            callbacks.append(tracer)
        except Exception:
            try:
                from langchain.callbacks import LangSmithCallbackHandler  # type: ignore
                handler = LangSmithCallbackHandler(api_key=settings.LANGSMITH_API_KEY)
                callbacks.append(handler)
            except Exception:
                # No langchain-langsmith callback available in this environment
                pass
    except Exception:
        pass

    chain = RetrievalQA.from_chain_type(llm=lc_llm, chain_type="stuff", retriever=retriever, callbacks=callbacks or None)

    # Pre-fetch retrieved docs using our vectorstore to log them regardless of LangChain internals
    query_emb = EmbeddingService().create_embedding(job_description)
    docs = _get_top_documents_from_vectorstore(resume_id, query_emb, top_k=top_k)

    # Run the chain with a question formed from the job description.
    import time
    start = time.time()
    answer = chain.run(job_description)
    latency_ms = int((time.time() - start) * 1000)

    result = {
        "match_score": "N/A",
        "summary": answer,
        "raw_answer": answer
    }

    # Attempt to log the run to LangSmith if available; failures should not break the response.
    try:
        from app.services.langsmith_adapter import log_analysis_run  # local import optional

        try:
            resp = log_analysis_run(
                engine="langchain",
                resume_id=resume_id,
                job_description=job_description,
                result=result,
                retrieved_docs=docs,
                prompt=job_description,
                llm_response={"text": answer},
                latency_ms=latency_ms,
            )
            # include langsmith run info in the returned result so callers can inspect
            result["langsmith"] = resp
        except Exception as e:
            # Swallow LangSmith errors to avoid breaking main flow but log locally
            try:
                import logging
                logging.getLogger("langsmith_adapter").exception("LangSmith logging failed: %s", e)
            except Exception:
                pass
            result["langsmith"] = {"status": "failed", "error": str(e)}
    except Exception:
        # langsmith_adapter not available or import failed; ignore
        result["langsmith"] = {"status": "not_available"}

    # Return in the same shape as LLMService.analyze_resume where possible
    result["engine_used"] = "langchain"
    result["latency_ms"] = latency_ms
    result["retrieved_docs_preview"] = docs[:5]
    return result
