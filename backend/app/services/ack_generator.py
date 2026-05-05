"""Generate a polite French acknowledgement message (vouvoiement)."""

from app.models.request import MedicalRequest


def generate_ack(request: MedicalRequest) -> str:
    """Build a draft acknowledgement message in professional French."""
    patient_name = request.patient.full_name or "[Nom du patient]"
    prescriber_name = request.prescriber.full_name or "[Nom du prescripteur]"
    exam_type = request.exam.modality.value if request.exam.modality else "[Type d'examen]"
    region = request.exam.region or "[Région anatomique]"

    lines = [
        f"Objet : Accusé de réception — Demande d'examen {exam_type} ({region})",
        "",
        f"Madame, Monsieur,",
        "",
        f"Nous accusons bonne réception de votre demande d'examen "
        f"{exam_type} pour le patient {patient_name}, "
        f"adressée par le Dr {prescriber_name}.",
        "",
    ]

    if request.missing_fields:
        lines.append("Afin de pouvoir traiter votre demande dans les meilleurs délais, "
                      "nous aurions besoin des éléments suivants :")
        lines.append("")
        for mf in request.missing_fields:
            lines.append(f"  - {mf.suggested_question_fr}")
        lines.append("")

    if not request.missing_fields:
        lines.append("Votre demande est complète et sera traitée dans les meilleurs délais. "
                      "Nous vous recontacterons pour confirmer le créneau de rendez-vous.")
        lines.append("")

    lines.extend([
        "Nous restons à votre disposition pour toute information complémentaire.",
        "",
        "Cordialement,",
        "[Nom du secrétariat]",
        "[Service de radiologie]",
        "[Coordonnées]",
    ])

    return "\n".join(lines)
