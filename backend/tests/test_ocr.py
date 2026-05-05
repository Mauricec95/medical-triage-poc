"""Tests for the OCR pipeline.

Tests cover:
- Text-layer PDF extraction via pdfplumber
- Image-based PDF extraction via OCR fallback
- PNG image extraction via pytesseract
- Full ingest pipeline for PDF/image files
"""

from pathlib import Path

import pytest

from app.services.ingest import ingest_file
from app.services.ocr import extract_text_from_file

SAMPLES_DIR = Path(__file__).resolve().parent.parent.parent / "samples"


def _skip_if_missing(filename: str) -> Path:
    """Return the sample path or skip if the file doesn't exist."""
    path = SAMPLES_DIR / filename
    if not path.exists():
        pytest.skip(f"Sample {filename} not found")
    return path


# ── Text-layer PDF tests ──────────────────────────────────────────────


class TestTextLayerPDF:
    def test_extract_text_from_pdf_scanner(self):
        path = _skip_if_missing("04_fax_scanner.pdf")
        text = extract_text_from_file(path)
        assert len(text) > 50
        assert "EL FASSI" in text or "FASSI" in text
        assert "Scanner" in text or "scanner" in text

    def test_extract_text_from_pdf_irm(self):
        path = _skip_if_missing("101_fax_irm_lombaire.pdf")
        text = extract_text_from_file(path)
        assert len(text) > 50
        assert "ROUSSEAU" in text
        assert "IRM" in text
        assert "lombaire" in text

    def test_pdf_contains_prescriber(self):
        path = _skip_if_missing("101_fax_irm_lombaire.pdf")
        text = extract_text_from_file(path)
        assert "LEBLANC" in text or "Leblanc" in text

    def test_pdf_contains_patient_dob(self):
        path = _skip_if_missing("04_fax_scanner.pdf")
        text = extract_text_from_file(path)
        assert "14/03/1958" in text


# ── Image-based PDF tests (OCR fallback) ──────────────────────────────


class TestImagePDF:
    def test_ocr_echo_pdf(self):
        path = _skip_if_missing("102_fax_image_echo.pdf")
        text = extract_text_from_file(path)
        assert len(text) > 30
        assert "BENALI" in text or "Benali" in text

    def test_ocr_echo_pdf_modality(self):
        path = _skip_if_missing("102_fax_image_echo.pdf")
        text = extract_text_from_file(path)
        assert "echographie" in text.lower() or "échographie" in text.lower()

    def test_ocr_doppler_pdf(self):
        path = _skip_if_missing("103_fax_image_doppler.pdf")
        text = extract_text_from_file(path)
        assert len(text) > 30
        assert "CHEVALIER" in text or "Chevalier" in text

    def test_ocr_doppler_pdf_urgency(self):
        path = _skip_if_missing("103_fax_image_doppler.pdf")
        text = extract_text_from_file(path)
        assert "URGENT" in text or "urgent" in text


# ── PNG image tests ───────────────────────────────────────────────────


class TestPNGImage:
    def test_ocr_ordonnance_png(self):
        path = _skip_if_missing("104_ordonnance_radio.png")
        text = extract_text_from_file(path)
        assert len(text) > 30
        assert "LAMBERT" in text or "Lambert" in text

    def test_ocr_ordonnance_modality(self):
        path = _skip_if_missing("104_ordonnance_radio.png")
        text = extract_text_from_file(path)
        assert "Radio" in text or "radio" in text
        assert "thorax" in text

    def test_ocr_walkin_png(self):
        path = _skip_if_missing("105_note_walkin.png")
        text = extract_text_from_file(path)
        assert len(text) > 30
        assert "MARTINEZ" in text or "Martinez" in text

    def test_ocr_walkin_phone(self):
        path = _skip_if_missing("105_note_walkin.png")
        text = extract_text_from_file(path)
        assert "06 33 44 55 66" in text or "0633445566" in text


# ── Full ingest pipeline for PDF/image ────────────────────────────────


class TestIngestPDFImage:
    def test_ingest_text_pdf(self):
        path = _skip_if_missing("04_fax_scanner.pdf")
        source = ingest_file(path)
        assert source.channel.value == "fax"
        assert source.raw_text is not None
        assert len(source.raw_text) > 50

    def test_ingest_image_pdf(self):
        path = _skip_if_missing("102_fax_image_echo.pdf")
        source = ingest_file(path)
        assert source.channel.value == "fax"
        assert source.raw_text is not None
        assert len(source.raw_text) > 30

    def test_ingest_png(self):
        path = _skip_if_missing("104_ordonnance_radio.png")
        source = ingest_file(path)
        assert source.channel.value == "fax"
        assert source.raw_text is not None
        assert len(source.raw_text) > 30

    def test_ingest_all_pdf_image_samples(self):
        """All PDF and image samples ingest without errors."""
        pdf_image_files = [
            f for f in SAMPLES_DIR.iterdir()
            if f.is_file() and f.suffix.lower() in (".pdf", ".png", ".jpg")
        ]
        assert len(pdf_image_files) >= 4, (
            f"Expected at least 4 PDF/image samples, found {len(pdf_image_files)}"
        )
        for f in pdf_image_files:
            source = ingest_file(f)
            assert source.raw_text, f"Empty OCR result for {f.name}"
            assert len(source.raw_text) > 20, (
                f"OCR result too short for {f.name}: {len(source.raw_text)} chars"
            )
