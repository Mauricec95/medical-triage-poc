# 🏥 Medical Triage POC — Tri des demandes de secrétariat médical

[English below](#english)

---

## Français

### Description

POC de tri automatisé des demandes entrantes pour un secrétariat de radiologie hospitalière. Le système ingère des emails et fax (PDF/images), extrait les informations structurées via un LLM, détecte les champs manquants, propose un routage et génère un accusé de réception en français.

### Fonctionnalités

- **Ingestion** : emails (.eml/.txt) et fax (PDF/images scannées)
- **OCR** : `pdfplumber` pour les PDF texte, `pytesseract` pour les images/fax scannés
- **Extraction LLM** : extraction structurée via OpenAI (gpt-4o / gpt-4.1), prompt en français
- **Validation** : règles métier (créatinine requise pour scanner avec injection, contacts manquants, etc.)
- **Routage** : suggestion automatique de l'action suivante (contacter prescripteur, patient, radiologue, etc.)
- **Accusé de réception** : message professionnel en français (vouvoiement) prêt à envoyer
- **Interface web** : boîte de réception, vue détaillée avec formulaire éditable, envoi d'accusé de réception

### Prérequis

- Python 3.11+
- Node.js 18+
- Docker & Docker Compose (optionnel)
- Clé API OpenAI

### Démarrage rapide

```bash
# 1. Cloner et configurer
cp .env.template .env
# Remplir OPENAI_API_KEY dans .env

# 2. Installer les dépendances
make install

# 3. Lancer en mode développement
# Terminal 1 :
make dev-backend
# Terminal 2 :
make dev-frontend

# 4. Ou via Docker
make docker-up
```

### Démo

```bash
make demo
```
Ingère les 10 échantillons du dossier `/samples` et ouvre l'interface pré-remplie.

### Structure du projet

```
medical-triage-poc/
├── backend/          # FastAPI + Python
├── frontend/         # Next.js (App Router) + Tailwind
├── samples/          # 10 échantillons synthétiques
├── data/             # SQLite (créé au démarrage)
├── docker-compose.yml
├── Makefile
└── CONFIG.md         # Variables d'environnement
```

Voir [CONFIG.md](CONFIG.md) pour la liste complète des variables d'environnement.

---

## English

### Description

Automated triage POC for incoming requests in a hospital radiology secretariat. The system ingests emails and faxes (PDF/images), extracts structured information via LLM, detects missing fields, suggests routing, and generates a French acknowledgement message.

### Features

- **Ingestion**: emails (.eml/.txt) and faxes (scanned PDFs/images)
- **OCR**: `pdfplumber` for text PDFs, `pytesseract` fallback for scanned images
- **LLM extraction**: structured extraction via OpenAI (gpt-4o / gpt-4.1), French prompt
- **Validation**: business rules (creatinine required for CT with injection, missing contacts, etc.)
- **Routing**: automatic next-action suggestion (contact prescriber, patient, radiologist, etc.)
- **Acknowledgement**: professional French message (vouvoiement) ready to send
- **Web UI**: inbox view, detail view with editable form, acknowledgement sending

### Prerequisites

- Python 3.11+
- Node.js 18+
- Docker & Docker Compose (optional)
- OpenAI API key

### Quick Start

```bash
cp .env.template .env
# Fill in OPENAI_API_KEY in .env

make install
# Terminal 1:
make dev-backend
# Terminal 2:
make dev-frontend

# Or via Docker:
make docker-up
```

### Demo

```bash
make demo
```

See [CONFIG.md](CONFIG.md) for all environment variables.
