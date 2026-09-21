from dataclasses import dataclass

from app.db.mongodb import get_knowledge_chunks_collection
from app.rag.embeddings import EmbeddingService


VECTOR_INDEX_NAME = "knowledge_chunks_vector_index"


@dataclass(frozen=True)
class RetrievedChunk:
    """A knowledge chunk returned by vector search."""

    chunk_id: str
    document_id: str
    text: str
    score: float
    metadata: dict[str, str]


class KnowledgeRetriever:
    """Retrieves medically relevant knowledge using vector search."""

    def __init__(
        self,
        embedding_service: EmbeddingService | None = None,
    ):
        self.embedding_service = (
            embedding_service or EmbeddingService()
        )

    async def search(
        self,
        query: str,
        top_k: int = 5,
    ) -> list[RetrievedChunk]:
        """
        Search the medical knowledge base using semantic similarity.

        Args:
            query: User's natural-language question.
            top_k: Maximum number of chunks to retrieve.

        Returns:
            Relevant chunks ordered by vector-search score.
        """

        if not query.strip():
            raise ValueError("Query cannot be empty.")

        if top_k <= 0:
            raise ValueError("top_k must be greater than zero.")

        query_embedding = self.embedding_service.embed_query(query)

        collection = get_knowledge_chunks_collection()

        pipeline = [
            {
                "$vectorSearch": {
                    "index": VECTOR_INDEX_NAME,
                    "path": "embedding",
                    "queryVector": query_embedding,
                    "numCandidates": max(top_k * 10, 50),
                    "limit": top_k,
                }
            },
            {
                "$project": {
                    "_id": 0,
                    "chunk_id": 1,
                    "document_id": 1,
                    "text": 1,
                    "metadata": 1,
                    "score": {
                        "$meta": "vectorSearchScore"
                    },
                }
            },
        ]

        # AsyncCollection.aggregate() returns a coroutine
        # that must be awaited to obtain the async cursor.
        cursor = await collection.aggregate(pipeline)

        results: list[RetrievedChunk] = []

        async for document in cursor:
            results.append(
                RetrievedChunk(
                    chunk_id=document["chunk_id"],
                    document_id=document["document_id"],
                    text=document["text"],
                    score=float(document["score"]),
                    metadata=document.get("metadata", {}),
                )
            )

        return results