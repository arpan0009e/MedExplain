from pathlib import Path

from app.rag.chunker import DocumentChunker
from app.rag.embeddings import EmbeddingService
from app.rag.loader import KnowledgeBaseLoader
from app.db.mongodb import get_knowledge_chunks_collection
from app.repositories.knowledge_chunk_repository import (
    KnowledgeChunkRepository,
)


class KnowledgeBaseIngestion:
    """Orchestrates knowledge-base loading, chunking, embedding, and storage."""

    def __init__(
        self,
        knowledge_base_path: Path,
        chunker: DocumentChunker | None = None,
        embedding_service: EmbeddingService | None = None,
    ):
        self.loader = KnowledgeBaseLoader(knowledge_base_path)

        self.chunker = chunker or DocumentChunker()

        self.embedding_service = (
            embedding_service or EmbeddingService()
        )

    def prepare_chunks(self) -> list[dict]:
        """
        Load documents, create chunks, and generate embeddings.

        This method does not interact with MongoDB.
        """

        documents = self.loader.load_documents()

        chunks = self.chunker.chunk_documents(documents)

        if not chunks:
            return []

        texts = [chunk.text for chunk in chunks]

        embeddings = self.embedding_service.embed_documents(
            texts
        )

        embedded_chunks = []

        for chunk, embedding in zip(chunks, embeddings):
            embedded_chunks.append(
                {
                    "document_id": chunk.document_id,
                    "chunk_id": chunk.chunk_id,
                    "text": chunk.text,
                    "embedding": embedding,
                    "metadata": chunk.metadata,
                }
            )

        return embedded_chunks

    async def ingest(self) -> int:
        """
        Prepare the knowledge chunks and store them in MongoDB.

        Returns:
            Number of chunks inserted or updated.
        """

        embedded_chunks = self.prepare_chunks()

        if not embedded_chunks:
            return 0

        collection = get_knowledge_chunks_collection()

        repository = KnowledgeChunkRepository(collection)

        return await repository.upsert_chunks(embedded_chunks)