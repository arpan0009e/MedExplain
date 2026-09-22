import pytest

from app.services.llm import LLMService


@pytest.mark.integration
@pytest.mark.asyncio
async def test_openrouter_generation():
    service = LLMService()

    response = await service.generate(
        system_instruction=(
            "You are a helpful assistant. "
            "Answer briefly and clearly."
        ),
        user_prompt="Explain what hemoglobin is in one sentence.",
    )

    assert response
    assert isinstance(response, str)
    assert len(response.strip()) > 0