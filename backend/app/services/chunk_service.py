from app.models.chunk import ResumeChunk


class ChunkService:

    def __init__(
        self,
        chunk_size: int = 500,
        overlap: int = 100
    ):
        if overlap >= chunk_size:
            raise ValueError(
                "overlap must be smaller than chunk_size"
            )

        self.chunk_size = chunk_size
        self.overlap = overlap

    def create_chunks(
        self,
        text: str,
        resume_id: str
    ) -> list[ResumeChunk]:

        if not text:
            return []

        chunks = []
        start = 0
        chunk_id = 1

        while start < len(text):

            end = min(
                start + self.chunk_size,
                len(text)
            )

            chunk_text = text[start:end].strip()

            if chunk_text:
                chunks.append(
                    ResumeChunk(
                        chunk_id=chunk_id,
                        resume_id=resume_id,
                        content=chunk_text,
                        character_count=len(chunk_text)
                    )
                )

                chunk_id += 1

            if end >= len(text):
                break

            start = end - self.overlap

        return chunks
