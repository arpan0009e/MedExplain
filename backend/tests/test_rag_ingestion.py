from pathlib import Path

from app.rag.ingestion import KnowledgeBaseIngestion


KNOWLEDGE_BASE_PATH = (
    Path(__file__).resolve().parents[1] / "knowledge_base"
)


def test_prepare_chunks_creates_embedded_chunks():
    ingestion = KnowledgeBaseIngestion(KNOWLEDGE_BASE_PATH)

    embedded_chunks = ingestion.prepare_chunks()

    assert embedded_chunks

    first_chunk = embedded_chunks[0]

    assert first_chunk["document_id"]
    assert first_chunk["chunk_id"]
    assert first_chunk["text"]
    assert len(first_chunk["embedding"]) == 384
    assert first_chunk["metadata"]["source"]