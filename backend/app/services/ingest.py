"""Ingestion service: normalize raw input files to { channel, raw_text, attachments_text }."""

import email
from pathlib import Path

from app.models.request import Channel, SourceInfo
from app.services.ocr import extract_text_from_file


def detect_channel(file_path: Path) -> Channel:
    """Detect the input channel based on file extension and content."""
    suffix = file_path.suffix.lower()
    if suffix == ".eml":
        return Channel.email
    if suffix in (".pdf", ".png", ".jpg", ".jpeg", ".tiff", ".tif"):
        return Channel.fax
    return Channel.email


def parse_eml(file_path: Path) -> str:
    """Parse an .eml file and return the plain-text body."""
    with open(file_path, "r", encoding="utf-8", errors="replace") as f:
        msg = email.message_from_file(f)

    body_parts: list[str] = []
    if msg.is_multipart():
        for part in msg.walk():
            if part.get_content_type() == "text/plain":
                payload = part.get_payload(decode=True)
                if payload:
                    body_parts.append(payload.decode("utf-8", errors="replace"))
    else:
        payload = msg.get_payload(decode=True)
        if payload:
            body_parts.append(payload.decode("utf-8", errors="replace"))

    return "\n".join(body_parts)


def ingest_file(file_path: Path) -> SourceInfo:
    """Read a file and return a normalized SourceInfo."""
    channel = detect_channel(file_path)
    suffix = file_path.suffix.lower()

    if suffix == ".eml":
        raw_text = parse_eml(file_path)
    elif suffix == ".txt":
        raw_text = file_path.read_text(encoding="utf-8", errors="replace")
    elif suffix in (".pdf", ".png", ".jpg", ".jpeg", ".tiff", ".tif"):
        raw_text = extract_text_from_file(file_path)
    else:
        raw_text = file_path.read_text(encoding="utf-8", errors="replace")

    return SourceInfo(
        channel=channel,
        raw_text=raw_text,
        attachments_text=None,
    )
