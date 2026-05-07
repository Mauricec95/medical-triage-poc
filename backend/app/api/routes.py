"""REST API routes."""

import json
import logging
from datetime import UTC, datetime
from pathlib import Path
from tempfile import NamedTemporaryFile

from fastapi import APIRouter, Depends, HTTPException, UploadFile
from sqlmodel import Session, select

from app.database import get_session
from app.models.request import (
    MedicalRequest,
    MedicalRequestDB,
    RequestStatus,
)
from app.services.ack_generator import generate_ack
from app.services.extractor import extract_request
from app.services.ingest import ingest_file
from app.services.validator import validate_request

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/health")
def health():
    return {"status": "ok"}


@router.post("/ingest")
async def ingest_upload(
    file: UploadFile,
    session: Session = Depends(get_session),
):
    """Upload a file, extract a MedicalRequest, persist it."""
    suffix = Path(file.filename or "upload.txt").suffix
    with NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        content = await file.read()
        tmp.write(content)
        tmp_path = Path(tmp.name)

    try:
        source = ingest_file(tmp_path)
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
            source_filename=file.filename,
        )
        session.add(db_record)
        session.commit()
        session.refresh(db_record)

        return {
            "id": db_record.id,
            "status": db_record.status,
            "request": request.model_dump(),
        }
    finally:
        tmp_path.unlink(missing_ok=True)


@router.get("/requests")
def list_requests(
    status: RequestStatus | None = None,
    modality: str | None = None,
    session: Session = Depends(get_session),
):
    """List all requests, optionally filtered."""
    stmt = select(MedicalRequestDB)
    if status:
        stmt = stmt.where(MedicalRequestDB.status == status)
    results = session.exec(stmt).all()

    items = []
    for r in results:
        data = json.loads(r.data_json) if r.data_json else {}
        if modality and data.get("exam", {}).get("modality") != modality:
            continue
        items.append({
            "id": r.id,
            "status": r.status,
            "source_filename": r.source_filename,
            "created_at": r.created_at.isoformat(),
            "patient_name": data.get("patient", {}).get("full_name"),
            "modality": data.get("exam", {}).get("modality"),
            "urgency": data.get("exam", {}).get("urgency"),
            "missing_count": len(data.get("missing_fields", [])),
        })

    return items


@router.get("/requests/{request_id}")
def get_request(
    request_id: str,
    session: Session = Depends(get_session),
):
    """Get a single request by ID."""
    db_record = session.get(MedicalRequestDB, request_id)
    if not db_record:
        raise HTTPException(status_code=404, detail="Demande non trouvée")

    data = json.loads(db_record.data_json) if db_record.data_json else {}
    return {
        "id": db_record.id,
        "status": db_record.status,
        "source_filename": db_record.source_filename,
        "created_at": db_record.created_at.isoformat(),
        "updated_at": db_record.updated_at.isoformat(),
        "request": data,
    }


@router.patch("/requests/{request_id}")
def update_request(
    request_id: str,
    body: dict,
    session: Session = Depends(get_session),
):
    """Update (human-edit) a request."""
    db_record = session.get(MedicalRequestDB, request_id)
    if not db_record:
        raise HTTPException(status_code=404, detail="Demande non trouvée")

    if "request" in body:
        validated = MedicalRequest.model_validate(body["request"])
        db_record.data_json = validated.model_dump_json()

    if "status" in body:
        db_record.status = RequestStatus(body["status"])

    db_record.updated_at = datetime.now(UTC)
    session.add(db_record)
    session.commit()
    session.refresh(db_record)

    return {"id": db_record.id, "status": db_record.status}


@router.post("/requests/{request_id}/send-ack")
def send_ack(
    request_id: str,
    session: Session = Depends(get_session),
):
    """Mock-send the acknowledgement. Logs to console, updates status."""
    db_record = session.get(MedicalRequestDB, request_id)
    if not db_record:
        raise HTTPException(status_code=404, detail="Demande non trouvée")

    data = json.loads(db_record.data_json) if db_record.data_json else {}
    ack = data.get("ack_message_fr", "(Aucun message généré)")

    logger.info("=== ENVOI ACCUSÉ DE RÉCEPTION (MOCK) ===")
    logger.info("Destinataire : %s", data.get("prescriber", {}).get("email", "inconnu"))
    logger.info("Message :\n%s", ack)
    logger.info("=== FIN ENVOI ===")

    db_record.status = RequestStatus.route
    db_record.updated_at = datetime.now(UTC)
    session.add(db_record)
    session.commit()

    return {
        "id": db_record.id,
        "status": db_record.status,
        "ack_sent": True,
        "message": ack,
    }
