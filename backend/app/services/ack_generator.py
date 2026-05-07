"""Generate a polite French acknowledgement message (vouvoiement).

The ack message is a draft ready for the secretariat to review
and send to the prescriber or patient. It adapts to:
- Urgency level
- Missing fields (polite itemized request)
- Complete vs incomplete requests
- Prescriber vs generic addressing
"""

from app.models.request import MedicalRequest, Urgency


def _format_prescriber_salutation(request: MedicalRequest) -> str:
    """Build the salutation line."""
    name = request.prescriber.full_name
    if name and name.startswith("Dr"):
        return f"Cher {name},"
    if name:
        return f"Cher Dr {name},"
    return "Madame, Monsieur,"


def _format_exam_description(request: MedicalRequest) -> str:
    """Build a human-readable exam description."""
    parts: list[str] = []

    modality = request.exam.modality
    if modality:
        parts.append(modality.value)
    else:
        parts.append("examen")

    region = request.exam.region
    if region:
        parts.append(region)

    if request.exam.with_injection is True:
        parts.append("avec injection")
    elif request.exam.with_injection is False:
        parts.append("sans injection")

    return " ".join(parts)


def _urgency_prefix(request: MedicalRequest) -> str:
    """Return an urgency notice if applicable."""
    if request.exam.urgency == Urgency.urgent:
        return (
            "Nous avons noté le caractère URGENT de cette demande "
            "et la traiterons en priorité.\n\n"
        )
    if request.exam.urgency == Urgency.prioritaire:
        return (
            "Nous avons pris note du caractère prioritaire "
            "de cette demande.\n\n"
        )
    return ""


def generate_ack(request: MedicalRequest) -> str:
    """Build a draft acknowledgement message in professional French.

    Uses vouvoiement throughout. Adapts content based on completeness
    and urgency.
    """
    patient_name = request.patient.full_name or "[Nom du patient]"
    prescriber_name = (
        request.prescriber.full_name or "[Nom du prescripteur]"
    )
    exam_desc = _format_exam_description(request)
    salutation = _format_prescriber_salutation(request)

    # Subject line
    subject = (
        f"Objet : Accusé de réception — "
        f"Demande {exam_desc} pour {patient_name}"
    )

    lines = [subject, "", salutation, ""]

    # Opening
    lines.append(
        f"Nous accusons bonne réception de votre demande "
        f"d'examen ({exam_desc}) pour le patient "
        f"{patient_name}, adressée par {prescriber_name}."
    )
    lines.append("")

    # Urgency notice
    urgency_note = _urgency_prefix(request)
    if urgency_note:
        lines.append(urgency_note.rstrip())
        lines.append("")

    # Missing fields section
    if request.missing_fields:
        lines.append(
            "Afin de pouvoir traiter votre demande dans les "
            "meilleurs délais, nous aurions besoin des "
            "éléments suivants :"
        )
        lines.append("")
        for i, mf in enumerate(request.missing_fields, 1):
            lines.append(f"  {i}. {mf.suggested_question_fr}")
        lines.append("")
        lines.append(
            "Nous vous serions reconnaissants de bien vouloir "
            "nous transmettre ces informations par retour de "
            "courrier ou par téléphone."
        )
        lines.append("")

    # Complete request
    if not request.missing_fields:
        lines.append(
            "Votre demande est complète et sera traitée dans "
            "les meilleurs délais. Nous vous recontacterons "
            "pour confirmer le créneau de rendez-vous."
        )
        lines.append("")

    # Closing
    lines.extend([
        "Nous restons à votre disposition pour toute "
        "information complémentaire.",
        "",
        "Cordialement,",
        "",
        "Le secrétariat de radiologie",
        "[Service de radiologie — Coordonnées]",
    ])

    return "\n".join(lines)
