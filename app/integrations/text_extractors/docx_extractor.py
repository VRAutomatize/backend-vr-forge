"""DOCX text extractor."""

import io

from docx import Document

from app.core.exceptions import ProcessingError
from app.core.logging import get_logger
from app.integrations.text_extractors.base import TextExtractor

logger = get_logger(__name__)


class DOCXExtractor(TextExtractor):
    """DOCX text extractor."""

    @property
    def supported_types(self) -> list[str]:
        """Get supported MIME types."""
        return [
            "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            "application/msword",
        ]

    async def extract(self, file_content: bytes) -> str:
        """Extract text from DOCX.

        Args:
            file_content: DOCX file content as bytes

        Returns:
            Extracted text

        Raises:
            ProcessingError: If extraction fails
        """
        try:
            docx_file = io.BytesIO(file_content)
            doc = Document(docx_file)
            text_parts = []

            for paragraph in doc.paragraphs:
                if paragraph.text.strip():
                    text_parts.append(paragraph.text)

            extracted_text = "\n\n".join(text_parts)
            logger.info("DOCX text extracted", paragraphs=len(text_parts), length=len(extracted_text))
            return extracted_text

        except Exception as e:
            logger.error("DOCX extraction failed", error=str(e))
            raise ProcessingError(f"Failed to extract text from DOCX: {str(e)}") from e

