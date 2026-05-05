"""OCR service: extract text from PDFs and images.

Uses pdfplumber for text-layer PDFs, falls back to pytesseract for scanned documents.
"""

from pathlib import Path

import pdfplumber
import pytesseract
from PIL import Image

from app.config import settings


def extract_text_from_pdf(file_path: Path) -> str:
    """Extract text from a PDF. Try text layer first, fall back to OCR."""
    text_parts: list[str] = []

    with pdfplumber.open(file_path) as pdf:
        for page in pdf.pages:
            text = page.extract_text()
            if text and text.strip():
                text_parts.append(text)
            else:
                # Fall back to OCR on the page image
                img = page.to_image(resolution=300).original
                ocr_text = pytesseract.image_to_string(img, lang=settings.tesseract_lang)
                if ocr_text.strip():
                    text_parts.append(ocr_text)

    return "\n\n".join(text_parts)


def extract_text_from_image(file_path: Path) -> str:
    """Extract text from an image file via Tesseract OCR."""
    img = Image.open(file_path)
    return pytesseract.image_to_string(img, lang=settings.tesseract_lang)


def extract_text_from_file(file_path: Path) -> str:
    """Dispatch to the appropriate extractor based on file type."""
    suffix = file_path.suffix.lower()
    if suffix == ".pdf":
        return extract_text_from_pdf(file_path)
    if suffix in (".png", ".jpg", ".jpeg", ".tiff", ".tif"):
        return extract_text_from_image(file_path)
    return file_path.read_text(encoding="utf-8", errors="replace")
