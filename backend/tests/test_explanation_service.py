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

@pytest.mark.asyncio
async def test_explanation_service_uses_report_context():
    """Report explanation should include report and RAG context."""

    retrieved_chunk = RetrievedChunk(
        chunk_id="chunk-1",
        document_id="hemoglobin",
        text=(
            "Hemoglobin is a protein in red blood cells "
            "that carries oxygen."
        ),
        score=0.95,
        metadata={
            "title": "Hemoglobin Test",
            "source": "MedlinePlus",
            "source_url": (
                "https://medlineplus.gov/lab-tests/"
                "hemoglobin-test/"
            ),
        },
    )

    retriever = AsyncMock()
    retriever.search.return_value = [retrieved_chunk]

    llm_service = AsyncMock()
    llm_service.generate.return_value = (
        "Your report lists a hemoglobin value of 13.5 g/dL."
    )

    service = ExplanationService(
        retriever=retriever,
        llm_service=llm_service,
    )

    response = await service.explain_report(
        user_question="What does my hemoglobin result mean?",
        report_text=(
            "Patient: Sample Patient\n"
            "Hemoglobin: 13.5 g/dL\n"
            "White Blood Cell Count: 7200 /uL\n"
            "Platelets: 250000 /uL"
        ),
    )

    assert response.answer == (
        "Your report lists a hemoglobin value of 13.5 g/dL."
    )

    assert len(response.sources) == 1
    assert response.sources[0].document_id == "hemoglobin"

    retriever.search.assert_awaited_once_with(
        query="What does my hemoglobin result mean?",
        top_k=5,
    )

    llm_service.generate.assert_awaited_once()

    call_kwargs = llm_service.generate.await_args.kwargs

    assert "Hemoglobin: 13.5 g/dL" in call_kwargs["user_prompt"]
    assert "Hemoglobin is a protein in red blood cells" in (
        call_kwargs["user_prompt"]
    )
    assert "What does my hemoglobin result mean?" in (
        call_kwargs["user_prompt"]
    )