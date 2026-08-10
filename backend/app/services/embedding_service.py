from openai import OpenAI

from app.config import settings


class EmbeddingService:

    def __init__(self):
        self.client = OpenAI(
            api_key=settings.OPENAI_API_KEY
        )

    def create_embedding(
        self,
        text: str
    ) -> list[float]:
        """
        Convert text into vector embedding.
        """

        response = self.client.embeddings.create(
            model=settings.EMBEDDING_MODEL,
            input=text
        )

        return response.data[0].embedding

    def create_embeddings(
        self,
        texts: list[str]
    ) -> list[list[float]]:
        """
        Generate embeddings for multiple chunks.
        """

        response = self.client.embeddings.create(
            model=settings.EMBEDDING_MODEL,
            input=texts
        )

        return [
            item.embedding
            for item in response.data
        ]
