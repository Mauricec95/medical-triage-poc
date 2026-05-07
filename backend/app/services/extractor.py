"""LLM-based extraction: raw text → MedicalRequest.

Falls back to regex-based extraction when no OpenAI API key is configured.
"""

import logging

from app.config import settings
from app.models.request import MedicalRequest, SourceInfo
from app.services.regex_extractor import regex_extract

logger = logging.getLogger(__name__)


def build_extraction_prompt(source: SourceInfo) -> str:
    """Build the user-message prompt for the LLM."""
    prompt = (
        "Voici le texte brut d'une demande médicale reçue "
        "par le secrétariat.\n\n"
        f"Canal : {source.channel.value}\n\n"
        f"--- TEXTE ---\n{source.raw_text}\n--- FIN ---\n\n"
    )
    if source.attachments_text:
        prompt += (
            f"--- PIÈCES JOINTES ---\n"
            f"{source.attachments_text}\n--- FIN PJ ---\n\n"
        )

    prompt += (
        "Extrais toutes les informations sous forme JSON "
        "conforme au schéma MedicalRequest. "
        "Réponds UNIQUEMENT avec le JSON."
    )
    return prompt


def extract_request(source: SourceInfo) -> MedicalRequest:
    """Extract a structured MedicalRequest from raw text.

    Uses the LLM when an API key is available, otherwise falls
    back to deterministic regex-based extraction.
    """
    if not settings.openai_api_key:
        logger.info(
            "No OpenAI API key — using regex-based extraction",
        )
        return regex_extract(source)

    from app.services.llm import call_llm_json

    prompt = build_extraction_prompt(source)

    try:
        data = call_llm_json(prompt)
    except Exception:
        logger.exception(
            "LLM extraction failed — falling back to regex",
        )
        return regex_extract(source)

    request = MedicalRequest.model_validate(data)
    request.source = source
    return request
