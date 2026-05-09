"""OCR service: extract text from PDFs and images.

Strategy:
  1. Text-layer PDFs → pdfplumber (fast, accurate)
  2. Image-based PDFs → pdfplumber renders page to image → pytesseract OCR
  3. Standalone images (PNG/JPG/TIFF) → pytesseract OCR

Tesseract uses the French language pack (fra) by default.
"""

import logging
from pathlib import Path

import pdfplumber
import pytesseract
from PIL import Image, ImageFilter

from app.config import settings

logger = logging.getLogger(__name__)

SUPPORTED_IMAGE_EXTENSIONS = {".png", ".jpg", ".jpeg", ".tiff", ".tif", ".bmp"}
OCR_DPI = 300
MIN_TEXT_LENGTH = 20


def _preprocess_image(img: Image.Image) -> Image.Image:
    """Apply basic preprocessing to improve OCR accuracy."""
    # Convert to grayscale
    if img.mode != "L":
        img = img.convert("L")
    # Sharpen slightly
    img = img.filter(ImageFilter.SHARPEN)
    return img


def extract_text_from_pdf(file_path: Path) -> str:
    """Extract text from a PDF.

    For each page: try the embedded text layer first (pdfplumber).
    If the text layer is empty or too short, render the page as an image
    and run Tesseract OCR.
    """
    text_parts: list[str] = []

    try:
        with pdfplumber.open(file_path) as pdf:
            for page_num, page in enumerate(pdf.pages, 1):
                # Try text layer
                text = page.extract_text()
                if text and len(text.strip()) >= MIN_TEXT_LENGTH:
                    logger.debug(
                        "Page %d: extracted %d chars from text layer",
                        page_num, len(text),
                    )
                    text_parts.append(text)
                else:
                    # Fall back to OCR
                    logger.info(
                        "Page %d: no text layer, falling back to OCR",
                        page_num,
                    )
                    try:
                        img = page.to_image(resolution=OCR_DPI).original
                        img = _preprocess_image(img)
                        ocr_text = pytesseract.image_to_string(
                            img, lang=settings.tesseract_lang,
                        )
                        if ocr_text.strip():
                            text_parts.append(ocr_text.strip())
                            logger.debug(
                                "Page %d: OCR extracted %d chars",
                                page_num, len(ocr_text),
                            )
                    except Exception:
                        logger.exception("OCR failed on page %d", page_num)
    except Exception:
        logger.exception("Failed to open PDF: %s", file_path)

    return "\n\n".join(text_parts)


def extract_text_from_image(file_path: Path) -> str:
    """Extract text from an image file via Tesseract OCR."""
    try:
        img = Image.open(file_path)
        img = _preprocess_image(img)
        text = pytesseract.image_to_string(img, lang=settings.tesseract_lang)
        logger.debug(
            "Image OCR: %s → %d chars", file_path.name, len(text),
        )
        return text.strip()
    except Exception:
        logger.exception("OCR failed on image: %s", file_path)
        return ""


def extract_text_from_file(file_path: Path) -> str:
    """Dispatch to the appropriate extractor based on file type."""
    suffix = file_path.suffix.lower()

    if suffix == ".pdf":
        return extract_text_from_pdf(file_path)

    if suffix in SUPPORTED_IMAGE_EXTENSIONS:
        return extract_text_from_image(file_path)

    # Plain text fallback
    return file_path.read_text(encoding="utf-8", errors="replace")
