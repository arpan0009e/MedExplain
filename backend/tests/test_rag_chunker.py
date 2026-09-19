from pathlib import Path

from app.rag.chunker import DocumentChunker
from app.rag.loader import KnowledgeBaseLoader


KNOWLEDGE_BASE_PATH = (
    Path(__file__).resolve().parents[1] / "knowledge_base"
)


def load_hemoglobin_document():
    loader = KnowledgeBaseLoader(KNOWLEDGE_BASE_PATH)

    documents = loader.load_documents()

    return next(
        document
        for document in documents
        if document.document_id == "hemoglobin"
    )


def test_document_is_split_into_chunks():
    document = load_hemoglobin_document()

    chunker = DocumentChunker(
        chunk_size=200,
        chunk_overlap=50,
    )

    chunks = chunker.chunk_document(document)

    assert len(chunks) > 1


def test_chunk_ids_are_sequential():
    document = load_hemoglobin_document()

    chunker = DocumentChunker(
        chunk_size=200,
        chunk_overlap=50,
    )

    chunks = chunker.chunk_document(document)

    assert chunks[0].chunk_id == "hemoglobin_001"
    assert chunks[1].chunk_id == "hemoglobin_002"


def test_chunk_metadata_is_preserved():
    document = load_hemoglobin_document()

    chunker = DocumentChunker(
        chunk_size=200,
        chunk_overlap=50,
    )

    chunks = chunker.chunk_document(document)

    first_chunk = chunks[0]

    assert first_chunk.document_id == "hemoglobin"
    assert first_chunk.metadata["title"] == "Hemoglobin"
    assert first_chunk.metadata["source"] == document.source
    assert first_chunk.metadata["source_url"] == document.source_url


def test_chunks_have_text():
    document = load_hemoglobin_document()

    chunker = DocumentChunker(
        chunk_size=200,
        chunk_overlap=50,
    )

    chunks = chunker.chunk_document(document)

    assert all(chunk.text.strip() for chunk in chunks)


def test_invalid_chunk_configuration_is_rejected():
    try:
        DocumentChunker(
            chunk_size=100,
            chunk_overlap=100,
        )
        assert False
    except ValueError:
        assert True