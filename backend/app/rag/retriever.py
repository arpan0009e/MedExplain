import re
from dataclasses import dataclass

from app.db.mongodb import get_knowledge_chunks_collection
from app.rag.embeddings import EmbeddingService


VECTOR_INDEX_NAME = "knowledge_chunks_vector_index"


@dataclass(frozen=True)
class RetrievedChunk:
    chunk_id: str
    document_id: str
    text: str
    score: float
    metadata: dict[str, str]


class KnowledgeRetriever:
    def __init__(
        self,
        embedding_service: EmbeddingService | None = None,
    ) -> None:
        self.embedding_service = embedding_service or EmbeddingService()

    async def search(
        self,
        query: str,
        top_k: int = 3,
    ) -> list[RetrievedChunk]:
        if not query.strip():
            raise ValueError("Query cannot be empty.")

        if top_k <= 0:
            raise ValueError("top_k must be greater than zero.")

        query_embedding = self.embedding_service.embed_query(query)

        collection = get_knowledge_chunks_collection()

        # Retrieve a larger candidate set first.
        # We will rerank these candidates before returning the final results.
        candidate_limit = max(top_k * 3, 10)

        pipeline = [
            {
                "$vectorSearch": {
                    "index": VECTOR_INDEX_NAME,
                    "path": "embedding",
                    "queryVector": query_embedding,
                    "numCandidates": max(candidate_limit * 10, 50),
                    "limit": candidate_limit,
                }
            },
            {
                "$project": {
                    "_id": 0,
                    "chunk_id": 1,
                    "document_id": 1,
                    "text": 1,
                    "metadata": 1,
                    "score": {"$meta": "vectorSearchScore"},
                }
            },
        ]

        cursor = await collection.aggregate(pipeline)

        candidates: list[RetrievedChunk] = []

        async for document in cursor:
            candidates.append(
                RetrievedChunk(
                    chunk_id=document["chunk_id"],
                    document_id=document["document_id"],
                    text=document["text"],
                    score=float(document["score"]),
                    metadata=document.get("metadata", {}),
                )
            )

        return self._rerank(
            query=query,
            chunks=candidates,
            top_k=top_k,
        )

    @staticmethod
    def _tokenize(text: str) -> set[str]:
        return set(
            re.findall(
                r"\b[a-z0-9]+\b",
                text.lower(),
            )
        )

    def _rerank(
        self,
        query: str,
        chunks: list[RetrievedChunk],
        top_k: int,
    ) -> list[RetrievedChunk]:
        if not chunks:
            return []

        query_tokens = self._tokenize(query)

        ranked_chunks: list[tuple[float, RetrievedChunk]] = []

        for chunk in chunks:
            title = chunk.metadata.get("title", "")
            title_tokens = self._tokenize(title)

            text_tokens = self._tokenize(chunk.text)

            title_overlap = len(query_tokens & title_tokens)
            text_overlap = len(query_tokens & text_tokens)

            # Base semantic similarity from MongoDB Vector Search.
            semantic_score = chunk.score

            # Exact title matches are more valuable than generic
            # semantic similarity for medical terminology queries.
            title_bonus = title_overlap * 0.20

            # Small lexical relevance signal from the chunk content.
            text_bonus = min(text_overlap * 0.02, 0.10)

            final_score = (
                semantic_score
                + title_bonus
                + text_bonus
            )

            ranked_chunks.append(
                (final_score, chunk)
            )

        ranked_chunks.sort(
            key=lambda item: item[0],
            reverse=True,
        )

        return [
            chunk
            for _, chunk in ranked_chunks[:top_k]
        ]