"""Rule-based validator: checks MedicalRequest for missing/ambiguous fields."""

from app.models.request import (
    MedicalRequest,
    MissingField,
    Modality,
    NextAction,
    Routing,
)


def validate_request(request: MedicalRequest) -> MedicalRequest:
    """Apply business rules on top of LLM output. Mutates and returns the request."""
    missing: list[MissingField] = list(request.missing_fields)

    # Rule: patient name is required
    if not request.patient.full_name:
        missing.append(MissingField(
            field_path="patient.full_name",
            reason="Nom du patient absent",
            suggested_question_fr="Pourriez-vous nous communiquer le nom complet du patient ?",
        ))

    # Rule: patient DOB is required
    if not request.patient.dob:
        missing.append(MissingField(
            field_path="patient.dob",
            reason="Date de naissance absente",
            suggested_question_fr="Quelle est la date de naissance du patient ?",
        ))

    # Rule: prescriber contact needed
    if not request.prescriber.phone and not request.prescriber.email:
        missing.append(MissingField(
            field_path="prescriber.phone",
            reason="Aucun contact du prescripteur (téléphone ou email)",
            suggested_question_fr=(
                "Pourriez-vous nous fournir un numéro de téléphone ou un email "
                "pour joindre le prescripteur ?"
            ),
        ))

    # Rule: scanner with injection requires creatinine
    if (
        request.exam.modality == Modality.scanner
        and request.exam.with_injection is True
    ):
        has_creat = any(
            "créat" in att.name.lower() or "creat" in att.name.lower()
            for att in request.required_attachments
            if att.present
        )
        if not has_creat:
            missing.append(MissingField(
                field_path="required_attachments.creatinine",
                reason="Scanner avec injection : résultat de créatinine requis",
                suggested_question_fr=(
                    "Un scanner avec injection est demandé. "
                    "Pourriez-vous fournir le résultat de créatinine récent du patient ?"
                ),
            ))

    # Rule: injection status unknown for scanner/IRM
    if (
        request.exam.modality in (Modality.scanner, Modality.irm)
        and request.exam.with_injection is None
    ):
        missing.append(MissingField(
            field_path="exam.with_injection",
            reason="Injection non précisée pour cet examen",
            suggested_question_fr="L'examen est-il demandé avec ou sans injection de produit de contraste ?",
        ))

    # Rule: clinical indication should be present
    if not request.clinical_indication:
        missing.append(MissingField(
            field_path="clinical_indication",
            reason="Indication clinique absente",
            suggested_question_fr="Quelle est l'indication clinique justifiant cet examen ?",
        ))

    request.missing_fields = missing

    # Update routing based on missing fields
    if missing:
        prescriber_missing = any("prescriber" in m.field_path for m in missing)
        patient_missing = any("patient" in m.field_path for m in missing)

        if prescriber_missing:
            request.routing = Routing(
                next_action=NextAction.contact_prescriber,
                target_contact=request.prescriber.email or request.prescriber.phone,
                rationale_fr="Informations du prescripteur manquantes — le contacter en priorité.",
            )
        elif patient_missing:
            request.routing = Routing(
                next_action=NextAction.contact_patient,
                target_contact=request.patient.phone or request.patient.email,
                rationale_fr="Informations du patient incomplètes — le contacter.",
            )

    return request
