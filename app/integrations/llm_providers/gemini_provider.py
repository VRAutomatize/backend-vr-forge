"""Google Gemini LLM provider."""

import json
from typing import Any

import google.generativeai as genai

from app.core.config import get_settings
from app.core.exceptions import ExternalServiceError
from app.core.logging import get_logger
from app.integrations.llm_providers.base import LLMProvider

settings = get_settings()
logger = get_logger(__name__)

# Configure Gemini
genai.configure(api_key=settings.GOOGLE_GEMINI_API_KEY)


class GeminiProvider(LLMProvider):
    """Google Gemini LLM provider."""

    async def generate(
        self,
        system_prompt: str,
        user_prompt: str,
        model: str = "gemini-pro",
        temperature: float = 0.7,
        max_tokens: int = 2000,
    ) -> str:
        """Generate text using Gemini.

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
            model_instance = genai.GenerativeModel(model)
            full_prompt = f"{system_prompt}\n\n{user_prompt}"

            response = await model_instance.generate_content_async(
                full_prompt,
                generation_config={
                    "temperature": temperature,
                    "max_output_tokens": max_tokens,
                },
            )

            content = response.text
            logger.info("Gemini generation completed", model=model)
            return content or ""

        except Exception as e:
            logger.error("Gemini generation failed", error=str(e), model=model)
            raise ExternalServiceError("Gemini", str(e)) from e

    async def generate_json(
        self,
        system_prompt: str,
        user_prompt: str,
        model: str = "gemini-pro",
        temperature: float = 0.7,
    ) -> dict[str, Any]:
        """Generate JSON response using Gemini.

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
            model_instance = genai.GenerativeModel(model)
            full_prompt = f"{system_prompt}\n\n{user_prompt}\n\nRespond with valid JSON only."

            response = await model_instance.generate_content_async(
                full_prompt,
                generation_config={
                    "temperature": temperature,
                },
            )

            content = response.text
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
            logger.error("Gemini JSON generation failed", error=str(e), model=model)
            raise ExternalServiceError("Gemini", str(e)) from e

