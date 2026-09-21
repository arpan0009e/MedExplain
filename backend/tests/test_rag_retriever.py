import asyncio

import pytest

from app.core.database import (
    close_database,
    initialize_database,
)
from app.rag.retriever import KnowledgeRetriever


@pytest.mark.integration
def test_retriever_returns_relevant_chunks():
    asyncio.run(_test_retriever_returns_relevant_chunks())


async def _test_retriever_returns_relevant_chunks():
    await initialize_database()

    try:
        retriever = KnowledgeRetriever()

        results = await retriever.search(
            query="What does LDL mean?",
            top_k=3,
        )

        assert results
        assert len(results) <= 3

        for result in results:
            assert result.chunk_id
            assert result.document_id
            assert result.text
            assert result.score >= 0
            assert isinstance(result.metadata, dict)

    finally:
        await close_database()