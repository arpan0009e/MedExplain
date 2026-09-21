import asyncio
import logging
import random

from google import genai
from google.genai import types
from google.genai.errors import ServerError

from app.core.config import settings


logger = logging.getLogger(__name__)


class LLMService:
    """Service responsible for interacting with the configured LLM."""

    MAX_RETRIES = 1
    INITIAL_BACKOFF_SECONDS = 2.0

    def __init__(self):
        self.client = genai.Client(
            api_key=settings.gemini_api_key
        )

    async def generate(
        self,
        system_instruction: str,
        user_prompt: str,
    ) -> str:
        """
        Generate a response from the configured LLM.

        Transient server-side errors are retried once with
        exponential backoff and jitter.
        """

        if not system_instruction.strip():
            raise ValueError("System instruction cannot be empty.")

        if not user_prompt.strip():
            raise ValueError("User prompt cannot be empty.")

        for attempt in range(self.MAX_RETRIES + 1):
            try:
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

            except ServerError:
                if attempt >= self.MAX_RETRIES:
                    logger.exception(
                        "Gemini service failed after %s attempt(s).",
                        attempt + 1,
                    )
                    raise

                delay = (
                    self.INITIAL_BACKOFF_SECONDS * (2**attempt)
                    + random.uniform(0, 0.5)
                )

                logger.warning(
                    "Gemini service temporarily unavailable. "
                    "Retrying in %.2f seconds.",
                    delay,
                )

                await asyncio.sleep(delay)

        raise RuntimeError("LLM generation failed unexpectedly.")