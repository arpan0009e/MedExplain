from unittest.mock import AsyncMock

import pytest

from app.rag.retriever import RetrievedChunk
from app.services.explanation import ExplanationService


@pytest.mark.asyncio
async def test_explanation_service_orchestrates_rag_and_llm():
    retrieved_chunk = RetrievedChunk(
        chunk_id="chunk-1",
        document_id="doc-1",
        text="LDL is commonly described as low-density lipoprotein.",
        score=0.95,
        metadata={
            "title": "LDL",
            "source": "MedlinePlus",
            "source_url": "https://medlineplus.gov/cholesterol.html",
        },
    )

    retriever = AsyncMock()
    retriever.search.return_value = [retrieved_chunk]

    llm_service = AsyncMock()
    llm_service.generate.return_value = (
        "LDL stands for low-density lipoprotein."
    )

    service = ExplanationService(
        retriever=retriever,
        llm_service=llm_service,
    )

    response = await service.explain(
        "What does LDL mean?"
    )

    assert response.answer == "LDL stands for low-density lipoprotein."
    assert len(response.sources) == 1
    assert response.sources[0].metadata["source"] == "MedlinePlus"

    retriever.search.assert_awaited_once_with(
        query="What does LDL mean?",
        top_k=5,
    )

    llm_service.generate.assert_awaited_once()

    call_kwargs = llm_service.generate.await_args.kwargs

    assert "LDL" in call_kwargs["user_prompt"]
    assert "MedlinePlus" in call_kwargs["user_prompt"]