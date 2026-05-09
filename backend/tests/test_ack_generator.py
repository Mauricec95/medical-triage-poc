"""Tests for the French acknowledgement message generator."""

from app.models.request import (
    ExamInfo,
    MedicalRequest,
    MissingField,
    Modality,
    PatientInfo,
    PrescriberInfo,
    Urgency,
)
from app.services.ack_generator import generate_ack


def test_ack_complete_request():
    req = MedicalRequest(
        patient=PatientInfo(full_name="Marie Legrand"),
        prescriber=PrescriberInfo(full_name="Dr Sophie Berger"),
        exam=ExamInfo(modality=Modality.irm, region="thoracique"),
        missing_fields=[],
    )
    ack = generate_ack(req)
    assert "Marie Legrand" in ack
    assert "Dr Sophie Berger" in ack
    assert "IRM" in ack
    assert "thoracique" in ack
    assert "Cordialement" in ack
    assert "complète" in ack.lower() or "complet" in ack.lower()


def test_ack_with_missing_fields():
    req = MedicalRequest(
        patient=PatientInfo(full_name="Test Patient"),
        prescriber=PrescriberInfo(full_name="Dr Test"),
        exam=ExamInfo(modality=Modality.scanner, region="abdominal"),
        missing_fields=[
            MissingField(
                field_path="required_attachments.creatinine",
                reason="Scanner avec injection : créatinine requise",
                suggested_question_fr=(
                    "Pourriez-vous fournir le résultat "
                    "de créatinine ?"
                ),
            ),
        ],
    )
    ack = generate_ack(req)
    assert "créatinine" in ack
    assert "éléments suivants" in ack


def test_ack_uses_vouvoiement():
    req = MedicalRequest(
        patient=PatientInfo(full_name="Test"),
        prescriber=PrescriberInfo(full_name="Dr Test"),
        exam=ExamInfo(modality=Modality.echo, region="abdominale"),
    )
    ack = generate_ack(req)
    assert "vous" in ack.lower() or "votre" in ack.lower()


def test_ack_placeholders_when_missing_info():
    req = MedicalRequest()
    ack = generate_ack(req)
    assert "[Nom du patient]" in ack
    assert "[Nom du prescripteur]" in ack


def test_ack_prescriber_salutation():
    req = MedicalRequest(
        patient=PatientInfo(full_name="Test"),
        prescriber=PrescriberInfo(full_name="Dr Moreau"),
        exam=ExamInfo(modality=Modality.radio, region="thorax"),
        missing_fields=[],
    )
    ack = generate_ack(req)
    assert "Cher Dr Moreau," in ack


def test_ack_generic_salutation_no_prescriber():
    req = MedicalRequest(
        patient=PatientInfo(full_name="Test"),
        exam=ExamInfo(modality=Modality.radio, region="thorax"),
        missing_fields=[],
    )
    ack = generate_ack(req)
    assert "Madame, Monsieur," in ack


def test_ack_urgency_notice_urgent():
    req = MedicalRequest(
        patient=PatientInfo(full_name="Test"),
        prescriber=PrescriberInfo(full_name="Dr Test"),
        exam=ExamInfo(
            modality=Modality.scanner,
            region="cérébral",
            urgency=Urgency.urgent,
        ),
        missing_fields=[],
    )
    ack = generate_ack(req)
    assert "URGENT" in ack


def test_ack_urgency_notice_prioritaire():
    req = MedicalRequest(
        patient=PatientInfo(full_name="Test"),
        prescriber=PrescriberInfo(full_name="Dr Test"),
        exam=ExamInfo(
            modality=Modality.irm,
            region="genou",
            urgency=Urgency.prioritaire,
        ),
        missing_fields=[],
    )
    ack = generate_ack(req)
    assert "prioritaire" in ack


def test_ack_numbered_missing_fields():
    req = MedicalRequest(
        patient=PatientInfo(full_name="Test"),
        prescriber=PrescriberInfo(full_name="Dr Test"),
        exam=ExamInfo(modality=Modality.scanner, region="thorax"),
        missing_fields=[
            MissingField(
                field_path="a",
                reason="r",
                suggested_question_fr="Question 1 ?",
            ),
            MissingField(
                field_path="b",
                reason="r",
                suggested_question_fr="Question 2 ?",
            ),
        ],
    )
    ack = generate_ack(req)
    assert "1. Question 1 ?" in ack
    assert "2. Question 2 ?" in ack


def test_ack_injection_mentioned():
    req = MedicalRequest(
        patient=PatientInfo(full_name="Test"),
        prescriber=PrescriberInfo(full_name="Dr Test"),
        exam=ExamInfo(
            modality=Modality.scanner,
            region="thorax",
            with_injection=True,
        ),
        missing_fields=[],
    )
    ack = generate_ack(req)
    assert "avec injection" in ack


def test_ack_closing():
    req = MedicalRequest(missing_fields=[])
    ack = generate_ack(req)
    assert "Le secrétariat de radiologie" in ack
    assert "disposition" in ack
