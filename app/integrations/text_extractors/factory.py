"""Factory for text extractors."""

from app.core.exceptions import ProcessingError
from app.integrations.text_extractors.docx_extractor import DOCXExtractor
from app.integrations.text_extractors.pdf_extractor import PDFExtractor
from app.integrations.text_extractors.txt_extractor import TXTExtractor


def get_extractor(content_type: str):
    """Get appropriate text extractor for content type.

    Args:
        content_type: MIME content type

    Returns:
        TextExtractor instance

    Raises:
        ProcessingError: If no extractor found for content type
    """
    extractors = [
        PDFExtractor(),
        DOCXExtractor(),
        TXTExtractor(),
    ]

    for extractor in extractors:
        if content_type in extractor.supported_types:
            return extractor

    raise ProcessingError(f"No extractor found for content type: {content_type}")

