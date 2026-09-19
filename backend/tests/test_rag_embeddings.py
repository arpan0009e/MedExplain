from app.rag.embeddings import EmbeddingService


def test_document_embedding_has_expected_dimensions():
    service = EmbeddingService()

    embeddings = service.embed_documents(
        ["Hemoglobin is a protein in red blood cells."]
    )

    assert len(embeddings) == 1
    assert len(embeddings[0]) == 384


def test_query_embedding_has_expected_dimensions():
    service = EmbeddingService()

    embedding = service.embed_query(
        "What is hemoglobin?"
    )

    assert len(embedding) == 384


def test_document_embedding_is_normalized():
    service = EmbeddingService()

    embedding = service.embed_query(
        "What is hemoglobin?"
    )

    magnitude = sum(value * value for value in embedding) ** 0.5

    assert abs(magnitude - 1.0) < 1e-5


def test_empty_query_is_rejected():
    service = EmbeddingService()

    try:
        service.embed_query("   ")
        assert False
    except ValueError:
        assert True