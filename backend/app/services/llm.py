"""Thin LLM wrapper — currently OpenAI, designed to be swappable."""

from pathlib import Path

from openai import OpenAI

from app.config import settings

# Load the extraction prompt from the markdown file
_PROMPT_PATH = Path(__file__).resolve().parent.parent / "prompts" / "extract_request.fr.md"


def _load_system_prompt() -> str:
    """Load the system prompt from the prompts directory."""
    if _PROMPT_PATH.exists():
        return _PROMPT_PATH.read_text(encoding="utf-8")
    return "Tu es un assistant médical. Extrais les informations structurées."


def get_client() -> OpenAI:
    """Return an OpenAI client instance."""
    return OpenAI(api_key=settings.openai_api_key)


def call_llm(user_message: str, system_prompt: str | None = None) -> str:
    """Send a message to the LLM and return the response text.

    This is the single call point — swap this function body
    to switch to Mistral, Claude, or any other provider.
    """
    client = get_client()
    messages = [
        {"role": "system", "content": system_prompt or _load_system_prompt()},
        {"role": "user", "content": user_message},
    ]

    response = client.chat.completions.create(
        model=settings.llm_model,
        messages=messages,
        temperature=0.1,
        max_tokens=4096,
    )

    return response.choices[0].message.content or ""
