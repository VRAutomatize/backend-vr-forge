"""Factory for LLM providers."""

from app.core.exceptions import ExternalServiceError
from app.integrations.llm_providers.gemini_provider import GeminiProvider
from app.integrations.llm_providers.openai_provider import OpenAIProvider
from app.integrations.llm_providers.together_provider import TogetherProvider


def get_provider(provider_name: str):
    """Get LLM provider instance.

    Args:
        provider_name: Provider name (openai, gemini, together)

    Returns:
        LLMProvider instance

    Raises:
        ExternalServiceError: If provider not found
    """
    providers = {
        "openai": OpenAIProvider,
        "gemini": GeminiProvider,
        "together": TogetherProvider,
    }

    provider_class = providers.get(provider_name.lower())
    if not provider_class:
        raise ExternalServiceError(
            "ProviderFactory",
            f"Unknown provider: {provider_name}. Supported: {list(providers.keys())}",
        )

    return provider_class()

