from dataclasses import dataclass

from app.rag.loader import KnowledgeDocument


@dataclass(frozen=True)
class DocumentChunk:
    """Represents a chunk of a knowledge-base document."""

    chunk_id: str
    document_id: str
    text: str
    metadata: dict[str, str]


class DocumentChunker:
    """Splits knowledge documents into overlapping text chunks."""

    def __init__(
        self,
        chunk_size: int = 800,
        chunk_overlap: int = 120,
    ):
        if chunk_size <= 0:
            raise ValueError("chunk_size must be greater than zero.")

        if chunk_overlap < 0:
            raise ValueError("chunk_overlap cannot be negative.")

        if chunk_overlap >= chunk_size:
            raise ValueError(
                "chunk_overlap must be smaller than chunk_size."
            )

        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

    def chunk_document(
        self,
        document: KnowledgeDocument,
    ) -> list[DocumentChunk]:
        """Split one knowledge document into overlapping chunks."""

        text = document.content.strip()

        if not text:
            return []

        chunks: list[DocumentChunk] = []

        start = 0
        chunk_number = 1

        while start < len(text):
            end = min(start + self.chunk_size, len(text))

            chunk_text = text[start:end].strip()

            if chunk_text:
                chunks.append(
                    DocumentChunk(
                        chunk_id=(
                            f"{document.document_id}_"
                            f"{chunk_number:03d}"
                        ),
                        document_id=document.document_id,
                        text=chunk_text,
                        metadata={
                            "title": document.title,
                            "topic": document.topic,
                            "category": document.category,
                            "source": document.source,
                            "source_url": document.source_url,
                            "file_name": document.file_name,
                        },
                    )
                )

            if end >= len(text):
                break

            start = end - self.chunk_overlap
            chunk_number += 1

        return chunks

    def chunk_documents(
        self,
        documents: list[KnowledgeDocument],
    ) -> list[DocumentChunk]:
        """Chunk multiple knowledge documents."""

        chunks: list[DocumentChunk] = []

        for document in documents:
            chunks.extend(self.chunk_document(document))

        return chunks