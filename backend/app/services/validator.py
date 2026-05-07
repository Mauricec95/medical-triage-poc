"""Rule-based validator: checks MedicalRequest for missing/ambiguous fields.

Business rules applied on top of LLM extraction output to catch
inconsistencies, enforce mandatory fields, and route requests.
"""

from datetime import datetime

from app.models.request import (
    MedicalRequest,
    MissingField,
    Modality,
    NextAction,
    Routing,
    Urgency,
)

# Modalities that commonly use contrast injection
INJECTION_MODALITIES = {Modality.scanner, Modality.irm}

# Modalities where injection status must be specified
INJECTION_REQUIRED_MODALITIES = {Modality.scanner, Modality.irm}


def _has_attachment(request: MedicalRequest, keyword: str) -> bool:
    """Check if a specific attachment is present."""
    return any(
        keyword in att.name.lower() and att.present
        for att in request.required_attachments
    )


def _has_attachment_mentioned(request: MedicalRequest, keyword: str) -> bool:
    """Check if a specific attachment is mentioned (present or not)."""
    return any(
        keyword in att.name.lower()
        for att in request.required_attachments
    )


def _parse_dob_age(dob_str: str | None) -> int | None:
    """Try to parse DOB and return age in years, or None."""
    if not dob_str:
        return None
    for fmt in ("%d/%m/%Y", "%Y-%m-%d", "%d-%m-%Y", "%d.%m.%Y"):
        try:
            born = datetime.strptime(dob_str, fmt)
            today = datetime.now()
            age = today.year - born.year
            if (today.month, today.day) < (born.month, born.day):
                age -= 1
            return age
        except ValueError:
            continue
    return None


def _deduplicate_missing(fields: list[MissingField]) -> list[MissingField]:
    """Remove duplicate missing fields by field_path."""
    seen: set[str] = set()
    result: list[MissingField] = []
    for f in fields:
        if f.field_path not in seen:
            seen.add(f.field_path)
            result.append(f)
    return result


def validate_request(request: MedicalRequest) -> MedicalRequest:
    """Apply business rules on top of LLM output.

    Mutates and returns the request with updated missing_fields,
    routing, and status.
    """
    missing: list[MissingField] = list(request.missing_fields)

    # ── Patient identity rules ────────────────────────────────────

    if not request.patient.full_name:
        missing.append(MissingField(
            field_path="patient.full_name",
            reason="Nom du patient absent",
            suggested_question_fr=(
                "Pourriez-vous nous communiquer le nom complet "
                "du patient ?"
            ),
        ))

    if not request.patient.dob:
        missing.append(MissingField(
            field_path="patient.dob",
            reason="Date de naissance absente",
            suggested_question_fr=(
                "Quelle est la date de naissance du patient ?"
            ),
        ))

    # Patient contact needed for scheduling
    if not request.patient.phone and not request.patient.email:
        missing.append(MissingField(
            field_path="patient.contact",
            reason="Aucun moyen de contacter le patient",
            suggested_question_fr=(
                "Pourriez-vous nous fournir un numéro de téléphone "
                "ou une adresse email pour joindre le patient ?"
            ),
        ))

    # ── Prescriber rules ──────────────────────────────────────────

    if not request.prescriber.full_name:
        missing.append(MissingField(
            field_path="prescriber.full_name",
            reason="Nom du prescripteur non identifié",
            suggested_question_fr=(
                "Quel est le nom du médecin prescripteur ?"
            ),
        ))

    if not request.prescriber.phone and not request.prescriber.email:
        missing.append(MissingField(
            field_path="prescriber.contact",
            reason=(
                "Aucun contact du prescripteur "
                "(téléphone ou email)"
            ),
            suggested_question_fr=(
                "Pourriez-vous nous fournir un numéro de téléphone "
                "ou un email pour joindre le prescripteur ?"
            ),
        ))

    # ── Exam rules ────────────────────────────────────────────────

    if not request.exam.modality:
        missing.append(MissingField(
            field_path="exam.modality",
            reason="Type d'examen (modalité) non identifié",
            suggested_question_fr=(
                "Quel type d'examen est demandé "
                "(scanner, IRM, échographie, etc.) ?"
            ),
        ))

    if not request.exam.region:
        missing.append(MissingField(
            field_path="exam.region",
            reason="Région anatomique non précisée",
            suggested_question_fr=(
                "Quelle région anatomique doit être examinée ?"
            ),
        ))

    # Injection status must be specified for scanner/IRM
    if (
        request.exam.modality in INJECTION_REQUIRED_MODALITIES
        and request.exam.with_injection is None
    ):
        missing.append(MissingField(
            field_path="exam.with_injection",
            reason="Injection non précisée pour cet examen",
            suggested_question_fr=(
                "L'examen est-il demandé avec ou sans injection "
                "de produit de contraste ?"
            ),
        ))

    # ── Injection-related rules ───────────────────────────────────

    if (
        request.exam.modality in INJECTION_MODALITIES
        and request.exam.with_injection is True
    ):
        # Creatinine required for contrast injection
        if not _has_attachment(request, "créat") and not _has_attachment(
            request, "creat"
        ):
            missing.append(MissingField(
                field_path="required_attachments.creatinine",
                reason=(
                    f"{request.exam.modality.value} avec injection : "
                    "résultat de créatinine requis"
                ),
                suggested_question_fr=(
                    "Un examen avec injection est demandé. "
                    "Pourriez-vous fournir le résultat de "
                    "créatinine récent du patient ?"
                ),
            ))

    # ── Clinical indication ───────────────────────────────────────

    if not request.clinical_indication:
        missing.append(MissingField(
            field_path="clinical_indication",
            reason="Indication clinique absente",
            suggested_question_fr=(
                "Quelle est l'indication clinique "
                "justifiant cet examen ?"
            ),
        ))

    # ── Ordonnance (prescription) ─────────────────────────────────

    if not _has_attachment(request, "ordonnance"):
        missing.append(MissingField(
            field_path="required_attachments.ordonnance",
            reason="Ordonnance non jointe ou non identifiée",
            suggested_question_fr=(
                "Pourriez-vous joindre l'ordonnance "
                "du médecin prescripteur ?"
            ),
        ))

    # ── Pediatric rules ───────────────────────────────────────────

    age = _parse_dob_age(request.patient.dob)
    if age is not None and age < 18:
        # Flag for coordination if pediatric
        if not any(
            "pédiatr" in m.field_path or "pediatr" in m.field_path
            for m in missing
        ):
            if age < 10:
                missing.append(MissingField(
                    field_path="routing.pediatric_coordination",
                    reason=(
                        f"Patient pédiatrique ({age} ans) — "
                        "coordination spécifique requise"
                    ),
                    suggested_question_fr=(
                        "Ce patient est mineur. Merci de confirmer "
                        "les modalités d'accompagnement et, le cas "
                        "échéant, la nécessité d'une sédation."
                    ),
                ))

    # ── Deduplicate and assign ────────────────────────────────────

    request.missing_fields = _deduplicate_missing(missing)

    # ── Routing logic ─────────────────────────────────────────────

    request.routing = _compute_routing(request)

    # ── Status ────────────────────────────────────────────────────

    request = _compute_status(request)

    return request


def _compute_routing(request: MedicalRequest) -> Routing:
    """Determine next action based on missing fields and urgency."""
    missing = request.missing_fields

    if not missing:
        # Complete request
        if request.exam.urgency == Urgency.urgent:
            return Routing(
                next_action=NextAction.await_radiologist_validation,
                target_contact=(
                    request.prescriber.email
                    or request.prescriber.phone
                ),
                rationale_fr=(
                    "Demande urgente complète — "
                    "soumise au radiologue pour validation."
                ),
            )
        return Routing(
            next_action=NextAction.schedule,
            target_contact=(
                request.patient.phone or request.patient.email
            ),
            rationale_fr=(
                "Demande complète — à programmer."
            ),
        )

    # Classify what's missing
    prescriber_info_missing = any(
        "prescriber" in m.field_path for m in missing
    )
    patient_info_missing = any(
        m.field_path in (
            "patient.full_name", "patient.dob", "patient.contact",
        )
        for m in missing
    )
    clinical_missing = any(
        m.field_path in (
            "clinical_indication", "exam.modality",
            "exam.region", "exam.with_injection",
        )
        for m in missing
    )
    attachment_missing = any(
        "required_attachments" in m.field_path for m in missing
    )

    # Priority: prescriber > clinical > patient > attachments
    if prescriber_info_missing and clinical_missing:
        return Routing(
            next_action=NextAction.contact_prescriber,
            target_contact=(
                request.prescriber.email
                or request.prescriber.phone
            ),
            rationale_fr=(
                "Informations du prescripteur et cliniques "
                "manquantes — contacter le prescripteur."
            ),
        )

    if prescriber_info_missing:
        return Routing(
            next_action=NextAction.contact_prescriber,
            target_contact=(
                request.prescriber.email
                or request.prescriber.phone
            ),
            rationale_fr=(
                "Informations du prescripteur manquantes — "
                "le contacter en priorité."
            ),
        )

    if clinical_missing or attachment_missing:
        return Routing(
            next_action=NextAction.contact_prescriber,
            target_contact=(
                request.prescriber.email
                or request.prescriber.phone
            ),
            rationale_fr=(
                "Informations cliniques ou pièces jointes "
                "manquantes — contacter le prescripteur."
            ),
        )

    if patient_info_missing:
        return Routing(
            next_action=NextAction.contact_patient,
            target_contact=(
                request.patient.phone or request.patient.email
            ),
            rationale_fr=(
                "Informations du patient incomplètes — "
                "le contacter."
            ),
        )

    # Fallback: radiologist review
    return Routing(
        next_action=NextAction.await_radiologist_validation,
        rationale_fr=(
            "Éléments manquants — à soumettre au radiologue "
            "pour décision."
        ),
    )


def _compute_status(request: MedicalRequest) -> MedicalRequest:
    """Set request status based on completeness and routing."""
    # Update confidence score based on completeness
    request.confidence = max(
        request.confidence,
        _compute_confidence(request),
    )
    return request


def _compute_confidence(request: MedicalRequest) -> float:
    """Compute a confidence score based on completeness."""
    score = 1.0
    n_missing = len(request.missing_fields)

    if n_missing == 0:
        return 0.95

    # Deduct per missing field, with diminishing returns
    deduction = min(n_missing * 0.1, 0.6)
    score -= deduction

    # Extra deduction for critical missing fields
    critical_paths = {
        "patient.full_name", "patient.dob",
        "prescriber.full_name", "exam.modality",
    }
    critical_missing = sum(
        1 for m in request.missing_fields
        if m.field_path in critical_paths
    )
    score -= critical_missing * 0.05

    return max(round(score, 2), 0.1)
