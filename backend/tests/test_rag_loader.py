from pathlib import Path

from app.rag.loader import KnowledgeBaseLoader


KNOWLEDGE_BASE_PATH = (
    Path(__file__).resolve().parents[1] / "knowledge_base"
)


def test_loads_all_knowledge_documents():
    loader = KnowledgeBaseLoader(KNOWLEDGE_BASE_PATH)

    documents = loader.load_documents()

    assert len(documents) == 3


def test_document_metadata_is_loaded():
    loader = KnowledgeBaseLoader(KNOWLEDGE_BASE_PATH)

    documents = loader.load_documents()

    hemoglobin = next(
        document
        for document in documents
        if document.document_id == "hemoglobin"
    )

    assert hemoglobin.title == "Hemoglobin"
    assert hemoglobin.topic == "Blood Test"
    assert hemoglobin.category == "Blood Tests"
    assert "MedlinePlus" in hemoglobin.source
    assert hemoglobin.source_url.startswith("https://")
    assert "Hemoglobin is" in hemoglobin.content