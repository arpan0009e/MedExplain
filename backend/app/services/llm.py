from google import genai
from google.genai import types

from app.core.config import settings


class LLMService:
    """Service responsible for interacting with the configured LLM."""

    def __init__(self):
        self.client = genai.Client(
            api_key=settings.gemini_api_key
        )

    async def generate(
        self,
        system_instruction: str,
        user_prompt: str,
    ) -> str:
        """Generate a response from the configured LLM."""

        response = await self.client.aio.models.generate_content(
            model=settings.gemini_model,
            contents=user_prompt,
            config=types.GenerateContentConfig(
                system_instruction=system_instruction,
            ),
        )

        if not response.text:
            raise RuntimeError("LLM returned an empty response.")

        return response.text.strip()