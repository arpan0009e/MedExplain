from app.rag.context_builder import RAGContextBuilder
from app.rag.retriever import RetrievedChunk


def test_context_builder_formats_sources():
    chunks = [
        RetrievedChunk(
            chunk_id="ldl_001",
            document_id="ldl",
            text="LDL is a type of cholesterol.",
            score=0.92,
            metadata={
                "title": "LDL",
                "source": "MedlinePlus",
                "source_url": "https://medlineplus.gov/cholesterol.html",
            },
        )
    ]

    builder = RAGContextBuilder()

    context = builder.build(chunks)

    assert "Source 1" in context
    assert "LDL" in context
    assert "MedlinePlus" in context
    assert "LDL is a type of cholesterol." in context