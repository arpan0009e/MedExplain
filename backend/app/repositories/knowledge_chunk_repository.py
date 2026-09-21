from pymongo import ReplaceOne
from pymongo.asynchronous.collection import AsyncCollection


class KnowledgeChunkRepository:
    """Repository for storing RAG knowledge chunks in MongoDB."""

    def __init__(self, collection: AsyncCollection):
        self.collection = collection

    async def upsert_chunks(self, chunks: list[dict]) -> int:
        """Insert new chunks or replace existing chunks."""

        if not chunks:
            return 0

        operations = [
            ReplaceOne(
                {"chunk_id": chunk["chunk_id"]},
                chunk,
                upsert=True,
            )
            for chunk in chunks
        ]

        result = await self.collection.bulk_write(
            operations,
            ordered=False,
        )

        return result.upserted_count + result.modified_count