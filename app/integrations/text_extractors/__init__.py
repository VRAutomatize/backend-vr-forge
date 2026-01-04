"""Text extractors for different file formats."""

from app.integrations.text_extractors.base import TextExtractor
from app.integrations.text_extractors.docx_extractor import DOCXExtractor
from app.integrations.text_extractors.factory import get_extractor
from app.integrations.text_extractors.pdf_extractor import PDFExtractor
from app.integrations.text_extractors.txt_extractor import TXTExtractor

__all__ = [
    "TextExtractor",
    "PDFExtractor",
    "DOCXExtractor",
    "TXTExtractor",
    "get_extractor",
]

