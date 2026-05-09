"""Regex-based extraction: raw text → MedicalRequest (no LLM needed).

Used as a fallback when no OpenAI API key is configured,
and for deterministic snapshot testing.
"""

import re

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
    "echographie": Modality.echo,
    "radio": Modality.radio,
    "radiographie": Modality.radio,
    "rx": Modality.radio,
    "panoramique": Modality.radio,
}


def _extract_patient(text: str) -> PatientInfo:
    """Extract patient info using regex patterns."""
    full_name = None
    dob = None
    sex = None
    phone = None
    email_addr = None

    name_patterns = [
        r"(?:M\.|Mme|Monsieur|Madame)\s+"
        r"([A-ZÀ-Ü][a-zà-ü]+\s+[A-ZÀ-Ü][A-ZÀ-Ü\s]+)",
        r"(?:M\.|Mme)\s+([A-ZÀ-Ü][a-zà-ü]+\s+[A-ZÀ-Ü]+)",
        r"Patient(?:e)?\s*:\s*(?:M\.|Mme)?\s*"
        r"([A-ZÀ-Ü][\w\s]+?)(?:\n|$)",
        r"Pour\s*:\s*(?:M\.|Mme)?\s*"
        r"([A-ZÀ-Ü][\w\s]+?)(?:\n|$)",
    ]
    for pat in name_patterns:
        m = re.search(pat, text)
        if m:
            full_name = m.group(1).strip()
            break

    dob_m = re.search(
        r"(?:né(?:e)?|Né(?:e)?|Ne)\s+le\s*:?\s*(\d{2}/\d{2}/\d{4})",
        text,
    )
    if not dob_m:
        dob_m = re.search(r"\((\d{2}/\d{2}/\d{4})\)", text)
    if not dob_m:
        dob_m = re.search(
            r"Date de naissance\s*:\s*(\d{2}/\d{2}/\d{4})", text,
        )
    if dob_m:
        dob = dob_m.group(1)

    if re.search(r"\bM\.\s", text) or re.search(r"Sexe\s*:\s*M\b", text):
        sex = "M"
    elif re.search(r"\bMme\b", text) or re.search(r"Sexe\s*:\s*F\b", text):
        sex = "F"

    phone_patterns = [
        r"(?:Tél(?:éphone)?|Tel|Contact)\s*"
        r"(?:patient(?:e)?)?\s*:\s*"
        r"(0[67]\s*\d{2}\s*\d{2}\s*\d{2}\s*\d{2})",
        r"(?:joignable|appeler)\s+(?:au\s+)?"
        r"(0[67]\s*\d{2}\s*\d{2}\s*\d{2}\s*\d{2})",
        r"Tél\s*:\s*(0[67]\s*\d{2}\s*\d{2}\s*\d{2}\s*\d{2})",
    ]
    for pat in phone_patterns:
        m = re.search(pat, text)
        if m:
            phone = m.group(1).strip()
            break

    email_m = re.search(
        r"Email\s*(?:patient(?:e)?)?\s*:\s*([\w.+-]+@[\w.-]+)",
        text,
    )
    if email_m:
        email_addr = email_m.group(1)

    return PatientInfo(
        full_name=full_name,
        dob=dob,
        sex=sex,
        phone=phone,
        email=email_addr,
    )


def _extract_prescriber(text: str) -> PrescriberInfo:
    """Extract prescriber info using regex patterns."""
    full_name = None
    specialty = None
    hospital = None
    phone = None
    email_addr = None

    dr_m = re.search(
        r"Dr\s+([A-ZÀ-Ü][a-zà-ü-]+(?:\s+[A-ZÀ-Ü][A-ZÀ-Ü]+)?)",
        text,
    )
    if not dr_m:
        dr_m = re.search(
            r"Prescripteur\s*:\s*Dr\s+([^\n]+)", text,
        )
    if dr_m:
        full_name = "Dr " + dr_m.group(1).strip()

    specialties = [
        "Cardiologie", "Pneumologie", "Neurologie", "Gynécologie",
        "Orthopédie", "Rhumatologie", "Urologie", "ORL",
        "Dermatologie", "Chirurgie digestive",
        "Chirurgie orthopédique", "Chirurgie vasculaire",
        "Oncologie", "Gastro-entérologie", "Endocrinologie",
        "Pédiatrie", "Gériatrie", "Médecine générale",
        "Médecine interne", "Médecine du sport",
        "Hématologie", "Néphrologie",
    ]
    for spec in specialties:
        if spec.lower() in text.lower():
            specialty = spec
            break

    hosp_m = re.search(
        r"(?:CHU|Hôpital|Hopital|Clinique|"
        r"Centre Hospitalier|CH)\s+[\w\s'-]+",
        text,
    )
    if hosp_m:
        hospital = hosp_m.group(0).strip()

    phone_m = re.search(
        r"(?:Tél\s+secrétariat|Tél)\s*:\s*"
        r"(04\s*\d{2}\s*\d{2}\s*\d{2}\s*\d{2})",
        text,
    )
    if phone_m:
        phone = phone_m.group(1).strip()

    email_m = re.search(r"(dr\.[\w.+-]+@[\w.-]+)", text)
    if email_m:
        email_addr = email_m.group(1)

    return PrescriberInfo(
        full_name=full_name,
        specialty=specialty,
        hospital_or_clinic=hospital,
        phone=phone,
        email=email_addr,
    )


def _extract_exam(text: str) -> ExamInfo:
    """Extract exam info using regex patterns."""
    modality = None
    region = None
    with_injection = None
    urgency = Urgency.routine

    text_lower = text.lower()

    for keyword, mod in MODALITY_KEYWORDS.items():
        if keyword in text_lower:
            modality = mod
            break

    region_m = re.search(
        r"(?:scanner|IRM|irm|écho|echo|echographie|"
        r"échographie|doppler|radio|rx)"
        r"\s+(?:de\s+(?:l[ae']?\s*)?|du\s+|des\s+)?"
        r"([\w\s'-]+?)"
        r"(?:\s*(?:avec|sans|pour|—|\n|$))",
        text,
        re.IGNORECASE,
    )
    if region_m:
        region = region_m.group(1).strip().rstrip(".")

    if re.search(r"avec\s+injection", text_lower):
        with_injection = True
    elif "sans injection" in text_lower:
        with_injection = False
    elif re.search(r"injection\s*:\s*oui", text_lower):
        with_injection = True
    elif re.search(r"injection\s*:\s*non\b", text_lower):
        with_injection = False

    if (
        re.search(r"\burgent\b", text_lower)
        or "demande urgente" in text_lower
    ):
        urgency = Urgency.urgent
    elif (
        "rapidement" in text_lower
        or "prioritaire" in text_lower
        or "au plus vite" in text_lower
    ):
        urgency = Urgency.prioritaire

    return ExamInfo(
        modality=modality,
        region=region,
        with_injection=with_injection,
        urgency=urgency,
    )


def _extract_indication(text: str) -> str | None:
    """Extract clinical indication."""
    patterns = [
        r"Indication\s*(?:clinique)?\s*:\s*(.+?)(?:\n|$)",
        r"Motif\s*(?:évoqué)?\s*:\s*(.+?)(?:\n|$)",
    ]
    for pat in patterns:
        m = re.search(pat, text, re.IGNORECASE)
        if m:
            return m.group(1).strip().rstrip(".")
    return None


def _extract_attachments(text: str) -> list[Attachment]:
    """Detect attachments mentioned in text."""
    attachments = []
    text_lower = text.lower()
    att_names = [
        "ordonnance", "créatinine", "creatinine", "créat",
        "allergies", "compte-rendu",
    ]
    for att_name in att_names:
        if att_name in text_lower:
            present = (
                "pj" in text_lower
                or "jointe" in text_lower
                or "joint" in text_lower
            )
            attachments.append(
                Attachment(name=att_name, present=present),
            )
    return attachments


def regex_extract(source: SourceInfo) -> MedicalRequest:
    """Deterministic regex-based extraction (no LLM needed)."""
    text = source.raw_text or ""

    return MedicalRequest(
        patient=_extract_patient(text),
        prescriber=_extract_prescriber(text),
        exam=_extract_exam(text),
        clinical_indication=_extract_indication(text),
        required_attachments=_extract_attachments(text),
        confidence=0.5,
        source=source,
    )
