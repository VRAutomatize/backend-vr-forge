"""OpenAI LLM provider."""

import json
from typing import Any

from openai import AsyncOpenAI

from app.core.config import get_settings
from app.core.exceptions import ExternalServiceError
from app.core.logging import get_logger
from app.integrations.llm_providers.base import LLMProvider

settings = get_settings()
logger = get_logger(__name__)


class OpenAIProvider(LLMProvider):
    """OpenAI LLM provider."""

    def __init__(self):
        """Initialize OpenAI client."""
        self.client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)

    async def generate(
        self,
        system_prompt: str,
        user_prompt: str,
        model: str = "gpt-4-turbo-preview",
        temperature: float = 0.7,
        max_tokens: int = 2000,
    ) -> str:
        """Generate text using OpenAI.

        Args:
            system_prompt: System prompt
            user_prompt: User prompt
            model: Model identifier
            temperature: Sampling temperature
            max_tokens: Maximum tokens to generate

        Returns:
            Generated text

        Raises:
            ExternalServiceError: If generation fails
        """
        try:
            response = await self.client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                temperature=temperature,
                max_tokens=max_tokens,
            )

            content = response.choices[0].message.content
            logger.info("OpenAI generation completed", model=model, tokens=response.usage.total_tokens)
            return content or ""

        except Exception as e:
            logger.error("OpenAI generation failed", error=str(e), model=model)
            raise ExternalServiceError("OpenAI", str(e)) from e

    async def generate_json(
        self,
        system_prompt: str,
        user_prompt: str,
        model: str = "gpt-4-turbo-preview",
        temperature: float = 0.7,
    ) -> dict[str, Any]:
        """Generate JSON response using OpenAI.

        Args:
            system_prompt: System prompt
            user_prompt: User prompt
            model: Model identifier
            temperature: Sampling temperature

        Returns:
            Generated JSON as dict

        Raises:
            ExternalServiceError: If generation fails
        """
        try:
            response = await self.client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                temperature=temperature,
                response_format={"type": "json_object"},
            )

            content = response.choices[0].message.content
            if content:
                return json.loads(content)
            return {}

        except Exception as e:
            logger.error("OpenAI JSON generation failed", error=str(e), model=model)
            raise ExternalServiceError("OpenAI", str(e)) from e

