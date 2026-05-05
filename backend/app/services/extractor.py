"""LLM-based extraction: raw text → MedicalRequest."""

import json
import logging

from app.models.request import MedicalRequest, SourceInfo
from app.services.llm import call_llm

logger = logging.getLogger(__name__)


def extract_request(source: SourceInfo) -> MedicalRequest:
    """Use the LLM to extract a structured MedicalRequest from raw text."""
    prompt = (
        "Voici le texte brut d'une demande médicale reçue par le secrétariat.\n\n"
        f"Canal : {source.channel.value}\n\n"
        f"--- TEXTE ---\n{source.raw_text}\n--- FIN ---\n\n"
    )
    if source.attachments_text:
        prompt += f"--- PIÈCES JOINTES ---\n{source.attachments_text}\n--- FIN PJ ---\n\n"

    prompt += (
        "Extrais toutes les informations sous forme JSON conforme au schéma MedicalRequest. "
        "Réponds UNIQUEMENT avec le JSON, sans commentaire."
    )

    raw_response = call_llm(prompt)

    # Strip markdown code fences if present
    cleaned = raw_response.strip()
    if cleaned.startswith("```"):
        cleaned = cleaned.split("\n", 1)[1] if "\n" in cleaned else cleaned[3:]
    if cleaned.endswith("```"):
        cleaned = cleaned[:-3]
    cleaned = cleaned.strip()

    try:
        data = json.loads(cleaned)
    except json.JSONDecodeError:
        logger.error("LLM returned invalid JSON: %s", raw_response[:500])
        data = {}

    request = MedicalRequest.model_validate(data)
    request.source = source
    return request
