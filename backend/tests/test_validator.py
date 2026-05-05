"""Tests for the rule-based validator."""

from app.models.request import (
    ExamInfo,
    MedicalRequest,
    Modality,
    PatientInfo,
    PrescriberInfo,
    Urgency,
)
from app.services.validator import validate_request


def test_complete_request_no_new_missing():
    """A fully-populated request shouldn't gain new missing fields from the validator."""
    req = MedicalRequest(
        patient=PatientInfo(
            full_name="Jean Dupont",
            dob="1965-03-15",
            phone="06 12 34 56 78",
        ),
        prescriber=PrescriberInfo(
            full_name="Dr Martin",
            email="dr.martin@chu.fr",
        ),
        exam=ExamInfo(
            modality=Modality.irm,
            region="cerveau",
            with_injection=False,
            urgency=Urgency.routine,
        ),
        clinical_indication="Céphalées chroniques",
    )
    result = validate_request(req)
    assert len(result.missing_fields) == 0


def test_missing_patient_name():
    req = MedicalRequest(
        patient=PatientInfo(dob="1980-01-01"),
        prescriber=PrescriberInfo(full_name="Dr X", email="dr@chu.fr"),
        exam=ExamInfo(modality=Modality.radio, with_injection=False),
        clinical_indication="Test",
    )
    result = validate_request(req)
    paths = [m.field_path for m in result.missing_fields]
    assert "patient.full_name" in paths


def test_missing_patient_dob():
    req = MedicalRequest(
        patient=PatientInfo(full_name="Marie"),
        prescriber=PrescriberInfo(full_name="Dr X", phone="04 00 00 00 00"),
        exam=ExamInfo(modality=Modality.echo, with_injection=False),
        clinical_indication="Test",
    )
    result = validate_request(req)
    paths = [m.field_path for m in result.missing_fields]
    assert "patient.dob" in paths


def test_missing_prescriber_contact():
    req = MedicalRequest(
        patient=PatientInfo(full_name="Test", dob="2000-01-01"),
        prescriber=PrescriberInfo(full_name="Dr Dupont"),
        exam=ExamInfo(modality=Modality.radio, with_injection=False),
        clinical_indication="Test",
    )
    result = validate_request(req)
    paths = [m.field_path for m in result.missing_fields]
    assert "prescriber.phone" in paths


def test_scanner_injection_requires_creatinine():
    req = MedicalRequest(
        patient=PatientInfo(full_name="Test", dob="1970-01-01"),
        prescriber=PrescriberInfo(full_name="Dr X", email="x@chu.fr"),
        exam=ExamInfo(
            modality=Modality.scanner,
            region="thorax",
            with_injection=True,
        ),
        clinical_indication="Bilan",
    )
    result = validate_request(req)
    paths = [m.field_path for m in result.missing_fields]
    assert "required_attachments.creatinine" in paths


def test_injection_unknown_flagged():
    req = MedicalRequest(
        patient=PatientInfo(full_name="Test", dob="1970-01-01"),
        prescriber=PrescriberInfo(full_name="Dr X", email="x@chu.fr"),
        exam=ExamInfo(
            modality=Modality.scanner,
            region="thorax",
            with_injection=None,
        ),
        clinical_indication="Bilan",
    )
    result = validate_request(req)
    paths = [m.field_path for m in result.missing_fields]
    assert "exam.with_injection" in paths


def test_missing_clinical_indication():
    req = MedicalRequest(
        patient=PatientInfo(full_name="Test", dob="1970-01-01"),
        prescriber=PrescriberInfo(full_name="Dr X", phone="04 00 00 00 00"),
        exam=ExamInfo(modality=Modality.echo, with_injection=False),
    )
    result = validate_request(req)
    paths = [m.field_path for m in result.missing_fields]
    assert "clinical_indication" in paths


def test_routing_set_when_prescriber_missing():
    req = MedicalRequest(
        patient=PatientInfo(full_name="Test", dob="1970-01-01"),
        prescriber=PrescriberInfo(full_name="Dr Dupont"),
        exam=ExamInfo(modality=Modality.radio, with_injection=False),
        clinical_indication="Test",
    )
    result = validate_request(req)
    assert result.routing.next_action.value == "contact_prescriber"
