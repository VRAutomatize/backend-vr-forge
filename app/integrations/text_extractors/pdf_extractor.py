"""PDF text extractor."""

import io

from PyPDF2 import PdfReader

from app.core.exceptions import ProcessingError
from app.core.logging import get_logger
from app.integrations.text_extractors.base import TextExtractor

logger = get_logger(__name__)


class PDFExtractor(TextExtractor):
    """PDF text extractor."""

    @property
    def supported_types(self) -> list[str]:
        """Get supported MIME types."""
        return ["application/pdf"]

    async def extract(self, file_content: bytes) -> str:
        """Extract text from PDF.

        Args:
            file_content: PDF file content as bytes

        Returns:
            Extracted text

        Raises:
            ProcessingError: If extraction fails
        """
        try:
            pdf_file = io.BytesIO(file_content)
            reader = PdfReader(pdf_file)
            text_parts = []

            for page in reader.pages:
                text = page.extract_text()
                if text:
                    text_parts.append(text)

            extracted_text = "\n\n".join(text_parts)
            logger.info("PDF text extracted", pages=len(reader.pages), length=len(extracted_text))
            return extracted_text

        except Exception as e:
            logger.error("PDF extraction failed", error=str(e))
            raise ProcessingError(f"Failed to extract text from PDF: {str(e)}") from e

