"""Snapshot tests: run the full pipeline on all samples.

Uses the regex-based extractor (no API call needed) to produce
deterministic, testable output. Validates that ingest → extract →
validate → ack_generate works end-to-end for every sample.

Snapshots are stored in tests/snapshots/ as JSON files.
Run with --update-snapshots to regenerate.
"""

import json
from pathlib import Path

import pytest

from app.services.ack_generator import generate_ack
from app.services.ingest import ingest_file
from app.services.regex_extractor import regex_extract
from app.services.validator import validate_request

SAMPLES_DIR = Path(__file__).resolve().parent.parent.parent / "samples"
SNAPSHOTS_DIR = Path(__file__).resolve().parent / "snapshots"


def _serialize_for_snapshot(request) -> dict:
    """Convert to a dict suitable for snapshot comparison."""
    data = request.model_dump()
    if "source" in data:
        data["source"].pop("raw_text", None)
        data["source"].pop("attachments_text", None)
    return data


def get_sample_files() -> list[Path]:
    """Get sorted list of all sample files."""
    return sorted(
        f for f in SAMPLES_DIR.iterdir()
        if f.is_file() and f.name != "README.md"
    )


@pytest.fixture(scope="session")
def update_snapshots(request):
    """Check if --update-snapshots flag is set."""
    return request.config.getoption("--update-snapshots", default=False)


@pytest.mark.parametrize(
    "sample_file",
    get_sample_files(),
    ids=[f.stem for f in get_sample_files()],
)
def test_pipeline_snapshot(sample_file: Path, update_snapshots):
    """Test full pipeline on each sample and compare to snapshot."""
    SNAPSHOTS_DIR.mkdir(parents=True, exist_ok=True)
    snapshot_path = SNAPSHOTS_DIR / f"{sample_file.stem}.json"

    # Ingest
    source = ingest_file(sample_file)
    assert source.raw_text

    # Extract (regex-based, no LLM)
    request = regex_extract(source)

    # Validate
    request = validate_request(request)

    # Generate ack
    request.ack_message_fr = generate_ack(request)

    # Serialize
    result = _serialize_for_snapshot(request)

    if update_snapshots or not snapshot_path.exists():
        snapshot_path.write_text(
            json.dumps(result, indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )
        return

    expected = json.loads(snapshot_path.read_text(encoding="utf-8"))
    assert result == expected, (
        f"Snapshot mismatch for {sample_file.name}. "
        f"Run with --update-snapshots to update."
    )
