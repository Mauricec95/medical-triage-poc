# Configuration — Variables d'environnement / Environment Variables

| Variable | Required | Default | Description (FR) | Description (EN) |
|---|---|---|---|---|
| `OPENAI_API_KEY` | **Oui** | — | Clé API OpenAI pour l'extraction LLM | OpenAI API key for LLM extraction |
| `LLM_MODEL` | Non | `gpt-4o` | Modèle LLM à utiliser | LLM model to use |
| `BACKEND_HOST` | Non | `0.0.0.0` | Adresse d'écoute du backend | Backend listen address |
| `BACKEND_PORT` | Non | `8000` | Port d'écoute du backend | Backend listen port |
| `DATABASE_URL` | Non | `sqlite:///./data/medical_triage.db` | URL de connexion SQLite | SQLite connection URL |
| `NEXT_PUBLIC_API_URL` | Non | `http://localhost:8000` | URL de l'API pour le frontend | API URL for frontend |
| `TESSERACT_LANG` | Non | `fra` | Langues Tesseract OCR (séparées par des virgules) | Tesseract OCR languages (comma-separated) |
| `LOG_LEVEL` | Non | `INFO` | Niveau de log (`DEBUG`, `INFO`, `WARNING`, `ERROR`) | Log level |

## Setup

1. Copy `.env.template` to `.env`:
   ```bash
   cp .env.template .env
   ```
2. Fill in your `OPENAI_API_KEY`.
3. Adjust other values as needed.
