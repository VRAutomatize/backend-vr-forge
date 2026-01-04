"""Together AI LLM provider."""

import json
from typing import Any

import httpx

from app.core.config import get_settings
from app.core.exceptions import ExternalServiceError
from app.core.logging import get_logger
from app.integrations.llm_providers.base import LLMProvider

settings = get_settings()
logger = get_logger(__name__)

TOGETHER_API_URL = "https://api.together.xyz/v1/chat/completions"


class TogetherProvider(LLMProvider):
    """Together AI LLM provider."""

    def __init__(self):
        """Initialize Together client."""
        self.api_key = settings.TOGETHER_API_KEY
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

    async def generate(
        self,
        system_prompt: str,
        user_prompt: str,
        model: str = "meta-llama/Llama-3-8b-chat-hf",
        temperature: float = 0.7,
        max_tokens: int = 2000,
    ) -> str:
        """Generate text using Together AI.

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
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    TOGETHER_API_URL,
                    headers=self.headers,
                    json={
                        "model": model,
                        "messages": [
                            {"role": "system", "content": system_prompt},
                            {"role": "user", "content": user_prompt},
                        ],
                        "temperature": temperature,
                        "max_tokens": max_tokens,
                    },
                    timeout=60.0,
                )
                response.raise_for_status()
                data = response.json()

                content = data["choices"][0]["message"]["content"]
                logger.info("Together generation completed", model=model)
                return content or ""

        except Exception as e:
            logger.error("Together generation failed", error=str(e), model=model)
            raise ExternalServiceError("Together", str(e)) from e

    async def generate_json(
        self,
        system_prompt: str,
        user_prompt: str,
        model: str = "meta-llama/Llama-3-8b-chat-hf",
        temperature: float = 0.7,
    ) -> dict[str, Any]:
        """Generate JSON response using Together AI.

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
            # Add JSON instruction to prompt
            json_prompt = f"{user_prompt}\n\nRespond with valid JSON only."

            async with httpx.AsyncClient() as client:
                response = await client.post(
                    TOGETHER_API_URL,
                    headers=self.headers,
                    json={
                        "model": model,
                        "messages": [
                            {"role": "system", "content": system_prompt},
                            {"role": "user", "content": json_prompt},
                        ],
                        "temperature": temperature,
                        "max_tokens": 2000,
                    },
                    timeout=60.0,
                )
                response.raise_for_status()
                data = response.json()

                content = data["choices"][0]["message"]["content"]
                if content:
                    # Try to extract JSON from response
                    content = content.strip()
                    if content.startswith("```json"):
                        content = content[7:]
                    if content.startswith("```"):
                        content = content[3:]
                    if content.endswith("```"):
                        content = content[:-3]
                    content = content.strip()
                    return json.loads(content)
                return {}

        except Exception as e:
            logger.error("Together JSON generation failed", error=str(e), model=model)
            raise ExternalServiceError("Together", str(e)) from e

