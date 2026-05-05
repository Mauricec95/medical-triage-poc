"""LLM-based extraction: raw text → MedicalRequest."""

import logging

from app.models.request import MedicalRequest, SourceInfo
from app.services.llm import call_llm_json

logger = logging.getLogger(__name__)


def build_extraction_prompt(source: SourceInfo) -> str:
    """Build the user-message prompt for the LLM."""
    prompt = (
        "Voici le texte brut d'une demande médicale reçue par le secrétariat.\n\n"
        f"Canal : {source.channel.value}\n\n"
        f"--- TEXTE ---\n{source.raw_text}\n--- FIN ---\n\n"
    )
    if source.attachments_text:
        prompt += f"--- PIÈCES JOINTES ---\n{source.attachments_text}\n--- FIN PJ ---\n\n"

    prompt += (
        "Extrais toutes les informations sous forme JSON conforme au schéma MedicalRequest. "
        "Réponds UNIQUEMENT avec le JSON."
    )
    return prompt


def extract_request(source: SourceInfo) -> MedicalRequest:
    """Use the LLM to extract a structured MedicalRequest from raw text."""
    prompt = build_extraction_prompt(source)

    try:
        data = call_llm_json(prompt)
    except Exception:
        logger.exception("LLM extraction failed")
        data = {}

    request = MedicalRequest.model_validate(data)
    request.source = source
    return request
