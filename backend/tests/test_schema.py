"""Smoke tests for the MedicalRequest schema."""

from app.models.request import (
    ExamInfo,
    MedicalRequest,
    Modality,
    PatientInfo,
    PrescriberInfo,
    Urgency,
)


def test_medical_request_defaults():
    """MedicalRequest can be instantiated with defaults."""
    req = MedicalRequest()
    assert req.confidence == 0.0
    assert req.missing_fields == []
    assert req.patient.full_name is None


def test_medical_request_full():
    """MedicalRequest can be populated with all fields."""
    req = MedicalRequest(
        patient=PatientInfo(full_name="Jean Dupont", dob="1965-03-15", sex="M"),
        prescriber=PrescriberInfo(
            full_name="Dr Marie Martin",
            specialty="Cardiologie",
            email="m.martin@hopital.fr",
        ),
        exam=ExamInfo(
            modality=Modality.scanner,
            region="thorax",
            with_injection=True,
            urgency=Urgency.urgent,
        ),
        clinical_indication="Douleur thoracique persistante",
        confidence=0.85,
    )
    assert req.patient.full_name == "Jean Dupont"
    assert req.exam.modality == Modality.scanner
    assert req.exam.urgency == Urgency.urgent
    assert req.confidence == 0.85


def test_medical_request_json_roundtrip():
    """MedicalRequest serializes and deserializes correctly."""
    req = MedicalRequest(
        patient=PatientInfo(full_name="Test Patient"),
        exam=ExamInfo(modality=Modality.irm, region="cerveau"),
    )
    json_str = req.model_dump_json()
    restored = MedicalRequest.model_validate_json(json_str)
    assert restored.patient.full_name == "Test Patient"
    assert restored.exam.modality == Modality.irm
