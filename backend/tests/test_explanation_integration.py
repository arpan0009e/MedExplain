import pytest

from app.core.database import close_database, initialize_database
from app.services.explanation import ExplanationService


@pytest.mark.integration
@pytest.mark.asyncio
async def test_real_medical_explanation_pipeline():
    """Test the complete RAG + Gemini medical explanation pipeline."""

    await initialize_database()

    try:
        service = ExplanationService()

        result = await service.explain(
            "What does LDL mean?"
        )

        # Verify that the LLM generated an explanation.
        assert result.answer
        assert isinstance(result.answer, str)
        assert result.answer.strip()

        # Verify that RAG returned medical knowledge sources.
        assert isinstance(result.sources, list)
        assert len(result.sources) > 0

        # Verify that every retrieved source contains the
        # metadata required for source attribution.
        for source in result.sources:
            assert source.metadata.get("title")
            assert source.metadata.get("source")
            assert source.metadata.get("source_url")

    finally:
        await close_database()