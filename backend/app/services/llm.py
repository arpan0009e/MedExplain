import asyncio
import logging
import random

import httpx

from app.core.config import settings

logger = logging.getLogger(__name__)


class LLMService:
    OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"

    MAX_RETRIES = 2
    INITIAL_BACKOFF_SECONDS = 2.0

    def __init__(self) -> None:
        if not settings.openrouter_api_key.strip():
            raise ValueError("OpenRouter API key is not configured.")

    async def generate(
        self,
        system_instruction: str,
        user_prompt: str,
    ) -> str:
        if not system_instruction.strip():
            raise ValueError("System instruction cannot be empty.")

        if not user_prompt.strip():
            raise ValueError("User prompt cannot be empty.")

        headers = {
            "Authorization": f"Bearer {settings.openrouter_api_key}",
            "Content-Type": "application/json",
        }

        payload = {
            "model": settings.openrouter_model,
            "messages": [
                {
                    "role": "system",
                    "content": system_instruction,
                },
                {
                    "role": "user",
                    "content": user_prompt,
                },
            ],
        }

        timeout = httpx.Timeout(
            connect=10.0,
            read=60.0,
            write=10.0,
            pool=10.0,
        )

        for attempt in range(self.MAX_RETRIES + 1):
            try:
                async with httpx.AsyncClient(
                    timeout=timeout
                ) as client:
                    response = await client.post(
                        self.OPENROUTER_URL,
                        headers=headers,
                        json=payload,
                    )

                if response.status_code >= 400:
                    response_text = response.text[:1000]

                    if response.status_code in {429, 500, 502, 503, 504}:
                        if attempt < self.MAX_RETRIES:
                            delay = (
                                self.INITIAL_BACKOFF_SECONDS * (2**attempt)
                                + random.uniform(0, 0.5)
                            )

                            logger.warning(
                                "OpenRouter returned HTTP %s. "
                                "Retrying in %.2f seconds.",
                                response.status_code,
                                delay,
                            )

                            await asyncio.sleep(delay)
                            continue

                    logger.error(
                        "OpenRouter request failed with HTTP %s: %s",
                        response.status_code,
                        response_text,
                    )

                    raise RuntimeError(
                        f"OpenRouter request failed with HTTP "
                        f"{response.status_code}."
                    )

                data = response.json()

                choices = data.get("choices", [])

                if not choices:
                    raise RuntimeError(
                        "OpenRouter returned no completion choices."
                    )

                message = choices[0].get("message", {})
                content = message.get("content")

                if not content or not content.strip():
                    raise RuntimeError(
                        "OpenRouter returned an empty response."
                    )

                return content.strip()

            except (httpx.TimeoutException, httpx.NetworkError) as exc:
                if attempt >= self.MAX_RETRIES:
                    logger.exception(
                        "OpenRouter request failed after %s attempt(s).",
                        attempt + 1,
                    )
                    raise RuntimeError(
                        "Unable to connect to the OpenRouter service."
                    ) from exc

                delay = (
                    self.INITIAL_BACKOFF_SECONDS * (2**attempt)
                    + random.uniform(0, 0.5)
                )

                logger.warning(
                    "OpenRouter connection failed. "
                    "Retrying in %.2f seconds.",
                    delay,
                )

                await asyncio.sleep(delay)

        raise RuntimeError("OpenRouter generation failed unexpectedly.")