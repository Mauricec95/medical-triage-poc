"""Tests for the ingestion service."""

from pathlib import Path

from app.models.request import Channel
from app.services.ingest import detect_channel, ingest_file

SAMPLES_DIR = Path(__file__).resolve().parent.parent.parent / "samples"


def test_detect_channel_txt():
    assert detect_channel(Path("test.txt")) == Channel.email


def test_detect_channel_eml():
    assert detect_channel(Path("test.eml")) == Channel.email


def test_detect_channel_pdf():
    assert detect_channel(Path("test.pdf")) == Channel.fax


def test_detect_channel_image():
    assert detect_channel(Path("test.jpg")) == Channel.fax
    assert detect_channel(Path("test.png")) == Channel.fax


def test_ingest_txt_file():
    sample = SAMPLES_DIR / "01_irm_thoracique.txt"
    if not sample.exists():
        return
    source = ingest_file(sample)
    assert source.channel == Channel.email
    assert source.raw_text is not None
    assert len(source.raw_text) > 50
    assert "LEGRAND" in source.raw_text


def test_ingest_all_100_samples():
    """Verify all 100 sample files can be ingested without errors."""
    sample_files = sorted(
        f for f in SAMPLES_DIR.iterdir()
        if f.is_file() and f.name != "README.md"
    )
    assert len(sample_files) == 100, f"Expected 100 samples, found {len(sample_files)}"

    for f in sample_files:
        source = ingest_file(f)
        assert source.raw_text is not None, f"Failed to ingest {f.name}"
        assert len(source.raw_text) > 10, f"Empty content for {f.name}"
