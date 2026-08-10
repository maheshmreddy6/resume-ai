from app.services.embedding_service import EmbeddingService
from app.services.vector_store import VectorStore


class RAGIngestion:

    def __init__(self):
        self.embedding_service = EmbeddingService()
        self.vector_store = VectorStore()

    def process_chunks(self, chunks):

        if not chunks:
            return {
                "stored_chunks": 0
            }

        texts = [
            chunk.content
            for chunk in chunks
        ]

        embeddings = self.embedding_service.create_embeddings(
            texts
        )

        result = self.vector_store.add_documents(
            chunks,
            embeddings
        )

        return result
