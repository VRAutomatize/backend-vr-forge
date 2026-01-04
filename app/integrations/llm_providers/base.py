"""Base LLM provider interface."""

from abc import ABC, abstractmethod
from typing import Any


class LLMProvider(ABC):
    """Abstract base class for LLM providers."""

    @abstractmethod
    async def generate(
        self,
        system_prompt: str,
        user_prompt: str,
        model: str,
        temperature: float = 0.7,
        max_tokens: int = 2000,
    ) -> str:
        """Generate text using LLM.

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
        pass

    @abstractmethod
    async def generate_json(
        self,
        system_prompt: str,
        user_prompt: str,
        model: str,
        temperature: float = 0.7,
    ) -> dict[str, Any]:
        """Generate JSON response using LLM.

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
        pass

