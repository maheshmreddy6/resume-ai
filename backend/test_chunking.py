from app.services.chunk_service import ChunkService


text = """
John Smith

Python Developer

Skills: Python FastAPI Docker AWS

Experience: 5 years developing backend applications.
"""

service = ChunkService(
    chunk_size=50,
    overlap=10
)

chunks = service.create_chunks(
    text
)

for chunk in chunks:
    print("----------------")
    
    print(
        "Chunk:",
        chunk.chunk_id
    )

    print(
        chunk.content
    )
