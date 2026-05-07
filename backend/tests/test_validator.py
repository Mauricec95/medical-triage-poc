"""Tests for the rule-based validator."""

from app.models.request import (
    Attachment,
    ExamInfo,
    MedicalRequest,
    Modality,
    NextAction,
    PatientInfo,
    PrescriberInfo,
    Urgency,
)
from app.services.validator import validate_request


def _make_complete_request(**overrides) -> MedicalRequest:
    """Helper to build a complete request with sensible defaults."""
    defaults = dict(
        patient=PatientInfo(
            full_name="Jean Dupont",
            dob="15/03/1965",
            phone="06 12 34 56 78",
        ),
        prescriber=PrescriberInfo(
            full_name="Dr Sophie Martin",
            email="dr.martin@chu.fr",
        ),
        exam=ExamInfo(
            modality=Modality.irm,
            region="cerveau",
            with_injection=False,
            urgency=Urgency.routine,
        ),
        clinical_indication="Céphalées chroniques",
        required_attachments=[
            Attachment(name="ordonnance", present=True),
        ],
    )
    defaults.update(overrides)
    return MedicalRequest(**defaults)


# ── Patient rules ─────────────────────────────────────────────────


def test_complete_request_no_new_missing():
    req = _make_complete_request()
    result = validate_request(req)
    assert len(result.missing_fields) == 0


def test_missing_patient_name():
    req = _make_complete_request(
        patient=PatientInfo(dob="01/01/1980", phone="06 00 00 00 00"),
    )
    result = validate_request(req)
    paths = [m.field_path for m in result.missing_fields]
    assert "patient.full_name" in paths


def test_missing_patient_dob():
    req = _make_complete_request(
        patient=PatientInfo(full_name="Marie", phone="06 00 00 00 00"),
    )
    result = validate_request(req)
    paths = [m.field_path for m in result.missing_fields]
    assert "patient.dob" in paths


def test_missing_patient_contact():
    req = _make_complete_request(
        patient=PatientInfo(full_name="Test", dob="01/01/2000"),
    )
    result = validate_request(req)
    paths = [m.field_path for m in result.missing_fields]
    assert "patient.contact" in paths


# ── Prescriber rules ──────────────────────────────────────────────


def test_missing_prescriber_name():
    req = _make_complete_request(
        prescriber=PrescriberInfo(email="dr@chu.fr"),
    )
    result = validate_request(req)
    paths = [m.field_path for m in result.missing_fields]
    assert "prescriber.full_name" in paths


def test_missing_prescriber_contact():
    req = _make_complete_request(
        prescriber=PrescriberInfo(full_name="Dr Dupont"),
    )
    result = validate_request(req)
    paths = [m.field_path for m in result.missing_fields]
    assert "prescriber.contact" in paths


# ── Exam rules ────────────────────────────────────────────────────


def test_missing_modality():
    req = _make_complete_request(
        exam=ExamInfo(region="thorax", with_injection=False),
    )
    result = validate_request(req)
    paths = [m.field_path for m in result.missing_fields]
    assert "exam.modality" in paths


def test_missing_region():
    req = _make_complete_request(
        exam=ExamInfo(modality=Modality.scanner, with_injection=False),
    )
    result = validate_request(req)
    paths = [m.field_path for m in result.missing_fields]
    assert "exam.region" in paths


def test_injection_unknown_flagged():
    req = _make_complete_request(
        exam=ExamInfo(
            modality=Modality.scanner,
            region="thorax",
            with_injection=None,
        ),
    )
    result = validate_request(req)
    paths = [m.field_path for m in result.missing_fields]
    assert "exam.with_injection" in paths


def test_injection_unknown_not_flagged_for_echo():
    """Injection status only required for scanner/IRM."""
    req = _make_complete_request(
        exam=ExamInfo(
            modality=Modality.echo,
            region="abdominale",
            with_injection=None,
        ),
    )
    result = validate_request(req)
    paths = [m.field_path for m in result.missing_fields]
    assert "exam.with_injection" not in paths


# ── Injection + creatinine rules ──────────────────────────────────


def test_scanner_injection_requires_creatinine():
    req = _make_complete_request(
        exam=ExamInfo(
            modality=Modality.scanner,
            region="thorax",
            with_injection=True,
        ),
    )
    result = validate_request(req)
    paths = [m.field_path for m in result.missing_fields]
    assert "required_attachments.creatinine" in paths


def test_irm_injection_requires_creatinine():
    """IRM with injection also requires creatinine."""
    req = _make_complete_request(
        exam=ExamInfo(
            modality=Modality.irm,
            region="hépatique",
            with_injection=True,
        ),
    )
    result = validate_request(req)
    paths = [m.field_path for m in result.missing_fields]
    assert "required_attachments.creatinine" in paths


def test_creatinine_present_no_flag():
    req = _make_complete_request(
        exam=ExamInfo(
            modality=Modality.scanner,
            region="thorax",
            with_injection=True,
        ),
        required_attachments=[
            Attachment(name="ordonnance", present=True),
            Attachment(name="créatinine", present=True),
        ],
    )
    result = validate_request(req)
    paths = [m.field_path for m in result.missing_fields]
    assert "required_attachments.creatinine" not in paths


# ── Clinical indication ──────────────────────────────────────────


def test_missing_clinical_indication():
    req = _make_complete_request(clinical_indication=None)
    result = validate_request(req)
    paths = [m.field_path for m in result.missing_fields]
    assert "clinical_indication" in paths


# ── Ordonnance ────────────────────────────────────────────────────


def test_missing_ordonnance():
    req = _make_complete_request(required_attachments=[])
    result = validate_request(req)
    paths = [m.field_path for m in result.missing_fields]
    assert "required_attachments.ordonnance" in paths


def test_ordonnance_present_no_flag():
    req = _make_complete_request()
    result = validate_request(req)
    paths = [m.field_path for m in result.missing_fields]
    assert "required_attachments.ordonnance" not in paths


# ── Pediatric rules ───────────────────────────────────────────────


def test_pediatric_child_flagged():
    req = _make_complete_request(
        patient=PatientInfo(
            full_name="Léa Petit",
            dob="15/06/2020",  # ~4 years old
            phone="06 00 00 00 00",
        ),
    )
    result = validate_request(req)
    paths = [m.field_path for m in result.missing_fields]
    assert "routing.pediatric_coordination" in paths


def test_adolescent_not_flagged():
    req = _make_complete_request(
        patient=PatientInfo(
            full_name="Léa Petit",
            dob="15/06/2012",  # ~13 years old
            phone="06 00 00 00 00",
        ),
    )
    result = validate_request(req)
    paths = [m.field_path for m in result.missing_fields]
    assert "routing.pediatric_coordination" not in paths


# ── Routing rules ─────────────────────────────────────────────────


def test_routing_schedule_when_complete():
    req = _make_complete_request()
    result = validate_request(req)
    assert result.routing.next_action == NextAction.schedule


def test_routing_radiologist_when_urgent_complete():
    req = _make_complete_request(
        exam=ExamInfo(
            modality=Modality.scanner,
            region="cérébral",
            with_injection=False,
            urgency=Urgency.urgent,
        ),
    )
    result = validate_request(req)
    assert result.routing.next_action == (
        NextAction.await_radiologist_validation
    )


def test_routing_contact_prescriber_when_prescriber_missing():
    req = _make_complete_request(
        prescriber=PrescriberInfo(full_name="Dr Dupont"),
    )
    result = validate_request(req)
    assert result.routing.next_action == NextAction.contact_prescriber


def test_routing_contact_patient_when_patient_contact_missing():
    req = _make_complete_request(
        patient=PatientInfo(full_name="Test", dob="01/01/1970"),
    )
    result = validate_request(req)
    assert result.routing.next_action == NextAction.contact_patient


# ── Confidence ────────────────────────────────────────────────────


def test_confidence_high_when_complete():
    req = _make_complete_request()
    result = validate_request(req)
    assert result.confidence >= 0.9


def test_confidence_lower_when_missing():
    req = _make_complete_request(
        patient=PatientInfo(),
        prescriber=PrescriberInfo(),
    )
    result = validate_request(req)
    assert result.confidence < 0.8


# ── Deduplication ─────────────────────────────────────────────────


def test_no_duplicate_missing_fields():
    req = _make_complete_request(
        patient=PatientInfo(),
        prescriber=PrescriberInfo(),
        clinical_indication=None,
        required_attachments=[],
    )
    result = validate_request(req)
    paths = [m.field_path for m in result.missing_fields]
    assert len(paths) == len(set(paths)), "Duplicate missing fields found"
