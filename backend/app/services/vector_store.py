from app.database import collection


class VectorStore:

    def add_documents(
        self,
        chunks,
        embeddings
    ):
        documents = []
        ids = []
        metadatas = []

        for chunk in chunks:

            # Unique ChromaDB ID
            vector_id = (
                f"{chunk.resume_id}"
                f"_chunk_{chunk.chunk_id}"
            )

            documents.append(
                chunk.content
            )

            ids.append(
                vector_id
            )

            metadatas.append(
                {
                    "resume_id": chunk.resume_id,
                    "chunk_id": chunk.chunk_id
                }
            )

        if not documents:
            return {
                "stored_chunks": 0
            }

        collection.add(
            documents=documents,
            embeddings=embeddings,
            ids=ids,
            metadatas=metadatas
        )

        return {
            "stored_chunks": len(documents)
        }

    def search(
        self,
        query_embedding,
        resume_id: str,
        limit: int = 5
    ):
        """
        Search only inside the specified resume.
        """

        results = collection.query(
            query_embeddings=[
                query_embedding
            ],
            n_results=limit,
            where={
                "resume_id": resume_id
            }
        )

        return results
