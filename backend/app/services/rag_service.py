from app.services.embedding_service import EmbeddingService
from app.services.vector_store import VectorStore


class RAGService:

    def __init__(self):
        self.embedding_service = EmbeddingService()
        self.vector_store = VectorStore()

    def retrieve_resume_context(
        self,
        job_description: str,
        resume_id: str
    ):

        query_embedding = self.embedding_service.create_embedding(
            job_description
        )

        results = self.vector_store.search(
            query_embedding=query_embedding,
            resume_id=resume_id,
            limit=5
        )

        documents = results.get("documents", [])

        if not documents:
            return ""

        # ChromaDB typically returns:
        #
        # [
        #     ["chunk1", "chunk2", "chunk3"]
        # ]

        if isinstance(documents[0], list):
            documents = documents[0]

        context = "\n\n".join(documents)

        return context
