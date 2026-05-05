"""Demo script: ingest all samples into the database."""

import json
import logging
from pathlib import Path

from app.database import init_db, engine
from app.models.request import MedicalRequestDB, RequestStatus
from app.services.ack_generator import generate_ack
from app.services.ingest import ingest_file
from app.services.extractor import extract_request
from app.services.validator import validate_request

from sqlmodel import Session

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

SAMPLES_DIR = Path(__file__).resolve().parent.parent.parent / "samples"


def main():
    init_db()
    sample_files = sorted(SAMPLES_DIR.glob("*"))
    sample_files = [f for f in sample_files if f.is_file() and f.name != "README.md"]

    logger.info("Found %d sample files in %s", len(sample_files), SAMPLES_DIR)

    with Session(engine) as session:
        for file_path in sample_files:
            logger.info("Ingesting: %s", file_path.name)
            try:
                source = ingest_file(file_path)
                request = extract_request(source)
                request = validate_request(request)
                request.ack_message_fr = generate_ack(request)

                status = (
                    RequestStatus.complet
                    if not request.missing_fields
                    else RequestStatus.incomplet
                )

                db_record = MedicalRequestDB(
                    status=status,
                    data_json=request.model_dump_json(),
                    source_filename=file_path.name,
                )
                session.add(db_record)
                session.commit()
                logger.info("  → %s (status=%s, missing=%d)",
                            db_record.id, status.value, len(request.missing_fields))
            except Exception:
                logger.exception("  ✗ Failed to ingest %s", file_path.name)

    logger.info("Done.")


if __name__ == "__main__":
    main()
