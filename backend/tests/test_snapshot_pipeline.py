"""Snapshot tests: run the full pipeline on all 100 samples with mocked LLM.

The LLM mock does rule-based extraction (no API call needed) to produce
deterministic, testable output. This validates that ingest → extract →
validate → ack_generate works end-to-end for every sample.

Snapshots are stored in tests/snapshots/ as JSON files.
Run with --update-snapshots to regenerate.
"""

import json
import re
from pathlib import Path

import pytest

from app.models.request import (
    Attachment,
    ExamInfo,
    MedicalRequest,
    Modality,
    PatientInfo,
    PrescriberInfo,
    SourceInfo,
    Urgency,
)
from app.services.ack_generator import generate_ack
from app.services.ingest import ingest_file
from app.services.validator import validate_request

SAMPLES_DIR = Path(__file__).resolve().parent.parent.parent / "samples"
SNAPSHOTS_DIR = Path(__file__).resolve().parent / "snapshots"


def _regex_extract_patient(text: str) -> PatientInfo:
    """Extract patient info using regex patterns."""
    full_name = None
    dob = None
    sex = None
    phone = None
    email = None

    # Patient name patterns
    name_patterns = [
        r"(?:M\.|Mme|Monsieur|Madame)\s+([A-ZÀ-Ü][a-zà-ü]+\s+[A-ZÀ-Ü][A-ZÀ-Ü\s]+)",
        r"(?:M\.|Mme)\s+([A-ZÀ-Ü][a-zà-ü]+\s+[A-ZÀ-Ü]+)",
        r"Patient\s*:\s*(?:M\.|Mme)?\s*([A-ZÀ-Ü][\w\s]+?)(?:\n|$)",
        r"(?:petit|petite)\s+(\w+\s+[A-ZÀ-Ü]+)",
        r"Nom\s*:\s*([A-ZÀ-Ü]+\s+\w+)",
    ]
    for pat in name_patterns:
        m = re.search(pat, text)
        if m:
            full_name = m.group(1).strip()
            break

    # DOB
    dob_m = re.search(
        r"(?:né(?:e)?|Né(?:e)?)\s+le\s+(\d{2}/\d{2}/\d{4})", text
    )
    if not dob_m:
        dob_m = re.search(r"Né(?:e)?\s+le\s*:\s*(\d{2}/\d{2}/\d{4})", text)
    if not dob_m:
        dob_m = re.search(r"\((\d{2}/\d{2}/\d{4})\)", text)
    if dob_m:
        dob = dob_m.group(1)

    # Sex
    if re.search(r"\bM\.\s", text) or re.search(r"Sexe\s*:\s*M\b", text):
        sex = "M"
    elif re.search(r"\bMme\b", text) or re.search(r"Sexe\s*:\s*F\b", text):
        sex = "F"

    # Phone (patient)
    phone_m = re.search(
        r"(?:Tél(?:éphone)?|Tel|Contact)\s*(?:patient(?:e)?)?\s*:\s*(0[67]\s*\d{2}\s*\d{2}\s*\d{2}\s*\d{2})",
        text,
    )
    if not phone_m:
        phone_m = re.search(
            r"(?:joignable|appeler)\s+(?:au\s+)?(0[67]\s*\d{2}\s*\d{2}\s*\d{2}\s*\d{2})",
            text,
        )
    if not phone_m:
        # Look for mobile numbers after "Tél :"
        phone_m = re.search(r"Tél\s*:\s*(0[67]\s*\d{2}\s*\d{2}\s*\d{2}\s*\d{2})", text)
    if phone_m:
        phone = phone_m.group(1).strip()

    # Email (patient)
    email_m = re.search(
        r"Email\s*(?:patient(?:e)?)?\s*:\s*([\w.+-]+@[\w.-]+)",
        text,
    )
    if email_m:
        email = email_m.group(1)

    return PatientInfo(
        full_name=full_name,
        dob=dob,
        sex=sex,
        phone=phone,
        email=email,
    )


def _regex_extract_prescriber(text: str) -> PrescriberInfo:
    """Extract prescriber info using regex patterns."""
    full_name = None
    specialty = None
    hospital = None
    phone = None
    email = None

    # Doctor name
    dr_m = re.search(r"Dr\s+([A-ZÀ-Ü][a-zà-ü-]+(?:\s+[A-ZÀ-Ü][A-ZÀ-Ü]+)?)", text)
    if not dr_m:
        dr_m = re.search(r"Prescripteur\s*:\s*Dr\s+([^\n]+)", text)
    if dr_m:
        full_name = "Dr " + dr_m.group(1).strip()

    # Specialty
    specialties = [
        "Cardiologie", "Pneumologie", "Neurologie", "Gynécologie",
        "Orthopédie", "Rhumatologie", "Urologie", "ORL", "Dermatologie",
        "Chirurgie digestive", "Chirurgie orthopédique", "Chirurgie vasculaire",
        "Oncologie", "Gastro-entérologie", "Endocrinologie", "Neuropédiatrie",
        "Pédiatrie", "Gériatrie", "Médecine générale", "Médecine interne",
        "Médecine du sport", "Gynécologie-Obstétrique", "Hématologie",
        "Néphrologie", "Chirurgie",
    ]
    for spec in specialties:
        if spec.lower() in text.lower():
            specialty = spec
            break

    # Hospital
    hosp_m = re.search(
        r"(?:CHU|Hôpital|Clinique|Centre Hospitalier|CH)\s+[\w\s-]+",
        text,
    )
    if hosp_m:
        hospital = hosp_m.group(0).strip()

    # Phone (prescriber/secrétariat)
    phone_m = re.search(
        r"(?:Tél\s+secrétariat|Tél)\s*:\s*(04\s*\d{2}\s*\d{2}\s*\d{2}\s*\d{2})",
        text,
    )
    if phone_m:
        phone = phone_m.group(1).strip()

    # Email (prescriber)
    email_m = re.search(r"(?:Email|De)\s*:\s*(dr\.[\w.+-]+@[\w.-]+)", text)
    if not email_m:
        email_m = re.search(r"(dr\.[\w.+-]+@[\w.-]+)", text)
    if email_m:
        email = email_m.group(1)

    return PrescriberInfo(
        full_name=full_name,
        specialty=specialty,
        hospital_or_clinic=hospital,
        phone=phone,
        email=email,
    )


MODALITY_KEYWORDS = {
    "scanner": Modality.scanner,
    "tdm": Modality.scanner,
    "tomodensito": Modality.scanner,
    "scann": Modality.scanner,
    "coroscanner": Modality.scanner,
    "coro": Modality.scanner,
    "irm": Modality.irm,
    "remnance": Modality.irm,
    "rmn": Modality.irm,
    "doppler": Modality.doppler,
    "écho-doppler": Modality.doppler,
    "echo": Modality.echo,
    "écho": Modality.echo,
    "échographie": Modality.echo,
    "radio": Modality.radio,
    "radiographie": Modality.radio,
    "rx": Modality.radio,
    "panoramique": Modality.radio,
}


def _regex_extract_exam(text: str) -> ExamInfo:
    """Extract exam info using regex patterns."""
    modality = None
    region = None
    with_injection = None
    urgency = Urgency.routine

    text_lower = text.lower()

    # Modality detection
    for keyword, mod in MODALITY_KEYWORDS.items():
        if keyword in text_lower:
            modality = mod
            break

    # Region
    region_m = re.search(
        r"(?:scanner|IRM|irm|écho|echo|doppler|radio|rx)\s+(?:de\s+(?:l[ae']?\s*)?|du\s+|des\s+)?([\w\s'-]+?)(?:\s*(?:avec|sans|pour|—|\n|$))",
        text,
        re.IGNORECASE,
    )
    if region_m:
        region = region_m.group(1).strip().rstrip(".")

    # Injection
    if re.search(r"avec\s+injection", text_lower) or re.search(r"avec\s+pdc", text_lower):
        with_injection = True
    elif "sans injection" in text_lower or "sans pdc" in text_lower:
        with_injection = False
    elif re.search(r"injection\s*:\s*oui", text_lower):
        with_injection = True
    elif re.search(r"injection\s*:\s*non\b", text_lower):
        with_injection = False

    # Urgency
    if re.search(r"\burgent\b", text_lower) or "demande urgente" in text_lower:
        urgency = Urgency.urgent
    elif "rapidement" in text_lower or "prioritaire" in text_lower or "au plus vite" in text_lower:
        urgency = Urgency.prioritaire

    return ExamInfo(
        modality=modality,
        region=region,
        with_injection=with_injection,
        urgency=urgency,
    )


def _regex_extract_indication(text: str) -> str | None:
    """Extract clinical indication."""
    patterns = [
        r"Indication\s*(?:clinique)?\s*:\s*(.+?)(?:\n|$)",
        r"Motif\s*(?:évoqué)?\s*:\s*(.+?)(?:\n|$)",
        r"Motif\s*:\s*(.+?)(?:\n|$)",
    ]
    for pat in patterns:
        m = re.search(pat, text, re.IGNORECASE)
        if m:
            return m.group(1).strip().rstrip(".")
    return None


def mock_extract(source: SourceInfo) -> MedicalRequest:
    """Deterministic regex-based extraction (no LLM) for testing."""
    text = source.raw_text or ""

    patient = _regex_extract_patient(text)
    prescriber = _regex_extract_prescriber(text)
    exam = _regex_extract_exam(text)
    indication = _regex_extract_indication(text)

    # Detect attachments mentioned
    attachments = []
    text_lower = text.lower()
    att_names = [
        "ordonnance", "créatinine", "creatinine", "créat",
        "allergies", "cr ", "compte-rendu",
    ]
    for att_name in att_names:
        if att_name in text_lower:
            present = "pj" in text_lower or "jointe" in text_lower or "joint" in text_lower
            attachments.append(Attachment(name=att_name, present=present))

    return MedicalRequest(
        patient=patient,
        prescriber=prescriber,
        exam=exam,
        clinical_indication=indication,
        required_attachments=attachments,
        confidence=0.7,
        source=source,
    )


def _serialize_for_snapshot(req: MedicalRequest) -> dict:
    """Convert to a dict suitable for snapshot comparison (exclude source raw text)."""
    data = req.model_dump()
    if "source" in data:
        data["source"].pop("raw_text", None)
        data["source"].pop("attachments_text", None)
    return data


def get_sample_files() -> list[Path]:
    """Get sorted list of all sample files."""
    files = sorted(
        f for f in SAMPLES_DIR.iterdir()
        if f.is_file() and f.name != "README.md"
    )
    return files


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

    # Extract (mocked — regex-based, no LLM)
    request = mock_extract(source)

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
