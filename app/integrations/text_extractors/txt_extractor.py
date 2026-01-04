"""TXT text extractor."""

import chardet

from app.core.exceptions import ProcessingError
from app.core.logging import get_logger
from app.integrations.text_extractors.base import TextExtractor

logger = get_logger(__name__)


class TXTExtractor(TextExtractor):
    """TXT text extractor."""

    @property
    def supported_types(self) -> list[str]:
        """Get supported MIME types."""
        return ["text/plain", "text/markdown"]

    async def extract(self, file_content: bytes) -> str:
        """Extract text from TXT.

        Args:
            file_content: TXT file content as bytes

        Returns:
            Extracted text

        Raises:
            ProcessingError: If extraction fails
        """
        try:
            # Detect encoding
            detected = chardet.detect(file_content)
            encoding = detected.get("encoding", "utf-8")

            # Decode text
            text = file_content.decode(encoding)
            logger.info("TXT text extracted", encoding=encoding, length=len(text))
            return text

        except Exception as e:
            logger.error("TXT extraction failed", error=str(e))
            raise ProcessingError(f"Failed to extract text from TXT: {str(e)}") from e

