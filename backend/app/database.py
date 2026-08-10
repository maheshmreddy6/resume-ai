import chromadb

from app.config import settings


client = chromadb.PersistentClient(
    path=settings.CHROMA_DB
)

collection = client.get_or_create_collection(
    name="resume_embeddings"
)
