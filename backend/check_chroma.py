import chromadb

from app.config import settings


client = chromadb.PersistentClient(
    path=settings.CHROMA_DB
)


collections = client.list_collections()

print("\nCollections:")
for collection in collections:
    print("-", collection.name)


collection = client.get_collection(
    name="resume_embeddings"
)


print("\nCollection:")
print(collection.name)

print("\nTotal documents:")
print(collection.count())


results = collection.get()

print("\nStored IDs:")
print(results["ids"])

print("\nStored documents:")
for document in results["documents"]:
    print("------------------------------")
    print(document)
