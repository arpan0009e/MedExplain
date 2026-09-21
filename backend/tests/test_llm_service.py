import pytest

from app.services.llm import LLMService


@pytest.mark.integration
@pytest.mark.asyncio
async def test_llm_service_generates_text():
    service = LLMService()

    response = await service.generate(
        system_instruction="You are a concise assistant.",
        user_prompt="Explain what an API is in one sentence.",
    )

    assert response.strip()