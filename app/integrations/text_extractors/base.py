"""Base text extractor interface."""

from abc import ABC, abstractmethod


class TextExtractor(ABC):
    """Abstract base class for text extractors."""

    @abstractmethod
    async def extract(self, file_content: bytes) -> str:
        """Extract text from file content.

        Args:
            file_content: File content as bytes

        Returns:
            Extracted text

        Raises:
            ProcessingError: If extraction fails
        """
        pass

    @property
    @abstractmethod
    def supported_types(self) -> list[str]:
        """Get list of supported MIME types."""
        pass

