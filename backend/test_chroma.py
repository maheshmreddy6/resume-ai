import chromadb


client = chromadb.PersistentClient(
    path="./chroma_db"
)

collection = client.get_or_create_collection(
    name="resume_embeddings"
)

print("ChromaDB started successfully!")

print(
    "Collection:",
    collection.name
)
