# Interview Prep Memo — Medical Triage POC

> **Read this 1-2 hours before your interview. It covers everything you need to confidently present and answer deep technical questions.**

---

## Table of Contents

1. [Your Opening Pitch (30 seconds)](#1-your-opening-pitch-30-seconds)
2. [The Problem — Know It Cold](#2-the-problem--know-it-cold)
3. [Solution Overview — The Elevator Version](#3-solution-overview--the-elevator-version)
4. [Architecture Deep Dive](#4-architecture-deep-dive)
5. [Technical Decisions — Why You Made Each Choice](#5-technical-decisions--why-you-made-each-choice)
6. [The 13 Business Rules — Be Ready to Explain Any](#6-the-13-business-rules--be-ready-to-explain-any)
7. [Numbers to Cite](#7-numbers-to-cite)
8. [How to Walk Through the Demo](#8-how-to-walk-through-the-demo)
9. [Likely Interview Questions & Answers](#9-likely-interview-questions--answers)
10. [Tricky Follow-Up Questions](#10-tricky-follow-up-questions)
11. [What You'd Do Differently in Production](#11-what-youd-do-differently-in-production)
12. [Quick Vocabulary Reference](#12-quick-vocabulary-reference)

---

## 1. Your Opening Pitch (30 seconds)

> *"I built an AI-powered triage system for French hospital radiology departments. The problem is that secretariats receive over 150 unstructured requests per day — emails, scanned faxes, phone notes — and must manually extract patient info, detect missing fields, route each request, and send acknowledgements. My system automates that entire pipeline: it ingests raw documents, runs OCR on scanned PDFs, uses GPT-4o to extract structured medical data, validates it against 13 domain-specific business rules, generates professional French acknowledgements, and presents everything in a review UI where humans make the final call. It's a full-stack POC with 180 automated tests and 105 synthetic French samples."*

**Key phrases to hit:**
- "AI-powered triage" — frames it as AI, not just CRUD
- "13 business rules" — shows it's not just an LLM wrapper
- "human-in-the-loop" — shows mature thinking about AI deployment
- "180 tests" — shows engineering discipline

---

## 2. The Problem — Know It Cold

### Who has this problem?
Radiology secretariats in French hospitals and private clinics. Every imaging department (Scanner, IRM, Doppler, Echo, Radio) has secretaries who process incoming exam requests.

### Daily volume (per secretary):
- **~100-150 emails/day**
- **~50 faxes/week** (yes, French hospitals still use fax — scanned and received as email attachments)
- **~50 phone calls/day**
- Walk-in patients with handwritten notes

### Why it's painful:
1. **Formats vary wildly** — free-text emails, scanned PDFs (sometimes upside down), handwritten prescriptions, lab results
2. **Information is almost always incomplete** — the most common: injection status for Scanner/IRM not specified, no creatinine result, prescriber contact missing
3. **Manual triage takes ~5 minutes per request** — multiply by 150 = nearly the entire day
4. **Back-and-forth phone tag** — secretary calls prescriber's office, leaves voicemail, waits, calls back
5. **Urgency misclassification risk** — a routine request that's actually urgent can delay care
6. **No audit trail** — no one knows the status of a request until someone asks

### The specific task the secretary does:
For each incoming request, they must:
1. **Triage** — classify by exam type, urgency, modality
2. **Extract** — pull out patient identity, prescriber info, exam details, clinical indication
3. **Detect gaps** — find missing or ambiguous fields
4. **Route** — determine who to contact next (prescriber? patient? radiologist?)
5. **Acknowledge** — send a professional response confirming receipt
6. **Prepare** — format for scheduling in the RIS

### Emotional anchor (use this in the interview):
> *"Imagine doing data entry 150 times a day, where each input is in a different format, half the fields are missing, and a mistake could mean a patient doesn't get their urgent scan on time."*

---

## 3. Solution Overview — The Elevator Version

**What I built:**
A full-stack application that takes raw medical documents (emails, faxes, images), extracts structured information using AI + OCR, validates it against hospital-specific rules, and presents it to the secretariat in a review-and-edit UI.

**The pipeline in one sentence:**
> *"Raw input → OCR if needed → LLM extraction → rule-based validation → French acknowledgement → human review UI."*

**The AI angle:**
- **GPT-4o** for structured extraction from unstructured French medical text
- **Dual extraction strategy**: LLM when API key is available, deterministic regex fallback for offline/testing
- **The LLM does not get the final say** — 13 business rules are applied on top of LLM output to catch hallucinations and enforce domain requirements
- **Confidence scoring** (0.1–0.95) — the system is transparent about its uncertainty

---

## 4. Architecture Deep Dive

### The Pipeline (6 steps):

```
Input File (.txt, .eml, .pdf, .png)
    │
    ▼
1. INGEST — Normalize to { channel, raw_text, attachments_text }
    │
    ▼
2. OCR — pdfplumber for text PDFs, Tesseract (fra) for scanned images
    │       Image preprocessing: grayscale → sharpen → OCR
    ▼
3. LLM EXTRACTION — GPT-4o with French system prompt → MedicalRequest
    │                 OR regex fallback (30+ patterns)
    ▼
4. VALIDATION — 13 business rules, missing field detection, routing logic
    │
    ▼
5. ACK GENERATION — Professional French message (vouvoiement)
    │
    ▼
6. PERSIST — SQLite via SQLModel ORM, exposed via 5 REST endpoints
```

### Backend Architecture:

```
backend/
├── app/
│   ├── main.py              ← FastAPI entrypoint
│   ├── config.py             ← pydantic-settings (env vars)
│   ├── database.py           ← SQLite + SQLModel session
│   ├── models/
│   │   └── request.py        ← MedicalRequest (Pydantic) + MedicalRequestDB (SQLModel)
│   ├── services/
│   │   ├── ingest.py         ← File normalization (.txt, .eml, .pdf, .png)
│   │   ├── ocr.py            ← pdfplumber + pytesseract fallback
│   │   ├── llm.py            ← Thin OpenAI wrapper (swappable)
│   │   ├── extractor.py      ← LLM extraction → MedicalRequest
│   │   ├── regex_extractor.py ← Deterministic fallback (30+ regex patterns)
│   │   ├── validator.py      ← 13 business rules + routing + confidence
│   │   └── ack_generator.py  ← French acknowledgement generator
│   ├── api/
│   │   └── routes.py         ← 5 REST endpoints
│   └── prompts/
│       └── extract_request.fr.md ← LLM system prompt (iterate without code changes)
└── tests/                    ← 180 tests
```

### Frontend Architecture:

```
frontend/
└── src/app/
    ├── layout.tsx             ← Root layout with French title
    ├── page.tsx               ← Inbox view (table, filters, upload)
    ├── globals.css            ← Tailwind + custom styles
    └── requests/[id]/
        └── page.tsx           ← Detail view (two-column: raw | form)
```

### The 5 REST Endpoints:

| Method | Path | Purpose |
|--------|------|---------|
| `POST` | `/ingest` | Upload file → extract → validate → persist |
| `GET` | `/requests` | List all (filter by status, modality) |
| `GET` | `/requests/{id}` | Full request detail |
| `PATCH` | `/requests/{id}` | Human edits (update data or status) |
| `POST` | `/requests/{id}/send-ack` | Mock-send acknowledgement |

---

## 5. Technical Decisions — Why You Made Each Choice

These are the questions interviewers love. For each decision, know the **what**, **why**, and **what you'd change in production**.

### Why Pydantic as the source of truth?
- **What:** `MedicalRequest` is a Pydantic `BaseModel` with nested sub-models (PatientInfo, PrescriberInfo, ExamInfo, etc.)
- **Why:** Pydantic validates at the boundary — if the LLM returns malformed data, it fails fast with clear error messages. Enums enforce domain vocabulary (Modality, Urgency, NextAction). Optional fields everywhere because real medical documents are always incomplete.
- **Production:** Same approach, possibly with Pydantic V2 model validators for cross-field validation.

### Why SQLite + JSON blob for storage?
- **What:** `MedicalRequestDB` stores the full `MedicalRequest` as a JSON string in a `data_json` column.
- **Why:** For a POC, this avoids complex migrations when the schema evolves. Adding a new field to `MedicalRequest` doesn't require an `ALTER TABLE`. SQLite is zero-config — `make demo` just works.
- **Production:** PostgreSQL with proper relational schema. The JSON blob approach doesn't scale for queries like "find all requests missing creatinine."

### Why LLM + regex fallback?
- **What:** The extractor tries OpenAI first. If no API key is set, it falls back to a deterministic regex-based extractor with 30+ French patterns.
- **Why:** Three reasons:
  1. **Testability** — All 180 tests run without an API key. CI never hits OpenAI.
  2. **Resilience** — If the LLM provider goes down, the system still works (degraded but functional).
  3. **Cost awareness** — For a POC demo, you don't want to burn API credits on every `make test`.
- **Production:** Keep the fallback for resilience. Add an evaluation harness comparing LLM extraction vs. regex vs. ground truth.

### Why a thin LLM wrapper?
- **What:** `llm.py` is ~30 lines. It calls `openai.ChatCompletion.create()` with `response_format={"type": "json_object"}`.
- **Why:** Swappable. You can replace with Mistral, Claude, or a local model by changing one file. The extraction logic in `extractor.py` doesn't know which LLM is behind the wrapper.
- **Production:** Add retry logic, circuit breaker, token counting, cost tracking.

### Why FastAPI?
- **What:** Python 3.11 + FastAPI for the backend.
- **Why:** Async-native, auto-generates OpenAPI docs, first-class Pydantic support (request/response validation), and it's the standard for Python AI backends.
- **Production:** Same choice. Add middleware for auth, rate limiting, structured logging.

### Why Next.js App Router?
- **What:** Next.js with App Router, Tailwind CSS, TypeScript.
- **Why:** Server components reduce client-side JS bundle. App Router is the modern Next.js standard. Tailwind keeps styling fast and consistent.
- **Production:** Same stack. Add authentication, i18n (though the POC is already fully French).

### Why OCR with pdfplumber + Tesseract?
- **What:** Two-tier OCR. `pdfplumber` extracts text from PDFs that have a text layer (fast, no OCR needed). Falls back to Tesseract for image-based PDFs and raw images.
- **Why:** Most hospital PDFs are generated digitally and have text layers. Only scanned faxes need actual OCR. This two-tier approach means ~80% of PDFs process in milliseconds.
- **Production:** Add GPU-accelerated OCR (docTR or EasyOCR) for higher accuracy on degraded scans. Consider layout analysis for tables.

### Why the confidence score never reaches 1.0?
- **What:** Confidence ranges from 0.1 to 0.95, computed from field completeness.
- **Why:** A system that says "100% confident" about unstructured text extraction is lying. Capping at 0.95 forces the human to always review. It's a UX decision as much as a technical one.
- **Production:** Calibrate confidence against ground truth. Use model logprobs if available.

---

## 6. The 13 Business Rules — Be Ready to Explain Any

| # | Rule | Why It Matters |
|---|------|----------------|
| 1 | Patient name required | Can't schedule without knowing who |
| 2 | Patient DOB required | Age affects protocol (pediatric, renal) |
| 3 | Patient contact (phone/email) required | Need to reach patient for scheduling |
| 4 | Prescriber name required | Legal: every exam needs a prescribing doctor |
| 5 | Prescriber contact required | To chase missing info |
| 6 | Exam modality required | Scanner vs IRM vs Echo = different equipment |
| 7 | Exam region required | "IRM" of what? Brain? Knee? |
| 8 | Injection status for Scanner/IRM | Changes protocol, prep, and duration |
| 9 | Creatinine for injection exams | Contrast agent can damage kidneys — creatinine is mandatory |
| 10 | Ordonnance (prescription) attached | Legal requirement in France |
| 11 | Clinical indication required | Radiologist needs it to interpret results |
| 12 | Pediatric flag (age < 10) | Special coordination: sedation, parental consent, adapted protocol |
| 13 | Urgency-aware routing | Urgent → radiologist for validation; routine → direct scheduling |

### The creatinine rule is the best example to give:
> *"If someone requests a Scanner or IRM with contrast injection, we automatically check for a creatinine lab result. Injected contrast agent can damage the kidneys, so French radiology departments require a recent creatinine result before injecting. If it's missing, the system flags it and generates a French question for the secretary to send to the prescriber: 'Pourriez-vous fournir le résultat de créatinine récent du patient?' This is a real patient safety rule, not just a data quality check."*

---

## 7. Numbers to Cite

Keep these in your head — interviewers love concrete metrics.

| Metric | Value |
|--------|-------|
| **Automated tests** | 180 (all passing) |
| **Synthetic samples** | 105 French medical documents |
| **Snapshot tests** | 100 (one per sample, full pipeline) |
| **Business rules** | 13 deterministic validation rules |
| **API endpoints** | 5 REST endpoints |
| **OCR tests** | 16 (text PDF, image PDF, PNG) |
| **API tests** | 14 integration tests |
| **E2E scenarios** | 8 manual test scenarios (all passed) |
| **Regex patterns** | 30+ French-specific extraction patterns |
| **Confidence range** | 0.1 – 0.95 (never reaches 1.0) |
| **Modalities** | 6 (Scanner, IRM, Doppler, Echo, Radio, Autre) |
| **Urgency levels** | 3 (Routine, Prioritaire, Urgent) |
| **Routing actions** | 5 (contact prescriber, patient, radiologist, schedule, reject) |

---

## 8. How to Walk Through the Demo

### Option A: Live demo (recommended if you have time)

1. **Start:** `make demo` from the repo root — this ingests all 105 samples and starts the app
2. **Inbox:** Show the table with 105 requests. Point out:
   - Status color coding (green = Complet, orange = Incomplet)
   - Urgency labels (red URGENT badge)
   - Missing fields count column
3. **Filter:** Click "Scanner" modality filter → show it narrows down. Reset. Click "Incomplet" status → show only requests with missing fields.
4. **Detail:** Click on any "Incomplet" request. Show:
   - Left side: raw text from the original document
   - Right side: structured form with all extracted fields
   - Missing fields section with red cards and French suggested questions
   - Confidence bar
5. **Edit:** Change the patient name, click "Sauvegarder" → show it persists
6. **Send ack:** Click "Envoyer (mock)" → show status changes to "Routé", button disables
7. **Upload:** Go back to inbox, upload a new .txt file → show it appears in the list

### Option B: Slides + recording

Use the presentation slides (10 slides, ~10-15 min) and reference the E2E test recording if they want to see the app live.

### Demo talking track:
> *"Let me walk you through the end-to-end flow. When a file comes in — say this email from a cardiologist requesting a coroscanner — the system ingests it, runs the extraction pipeline, and produces this structured view. Notice how it flagged that the injection status is unspecified — the system generated a French question the secretary can send back: 'L'examen est-il demandé avec ou sans injection de produit de contraste?' The confidence is at 0.55 because three fields are missing. Once the secretary fills in the gaps and clicks save, the confidence updates. When everything's complete, they send the acknowledgement — a professional French email in vouvoiement — and the request is routed for scheduling."*

---

## 9. Likely Interview Questions & Answers

### "Why did you build this?"
> *"I saw this problem firsthand in the French healthcare system. Radiology secretariats are bottlenecked by manual triage of unstructured requests. I wanted to show that a relatively simple pipeline — LLM extraction + rule validation + human review — can automate 80% of the repetitive work while keeping humans in the loop for safety."*

### "What's the AI part?"
> *"Three things. First, GPT-4o extracts structured data from unstructured French medical text — it understands abbreviations like 'coroscanner', medical terminology, and varied document formats. Second, the system does intelligent gap detection — it doesn't just check for empty fields, it applies domain-specific rules like 'if Scanner with injection, then creatinine is required.' Third, it generates contextual French acknowledgement messages that adapt to the specific request — mentioning the patient, the exam, and what's missing."*

### "Why not just use the LLM for everything?"
> *"LLMs hallucinate. In healthcare, a hallucinated field can lead to the wrong protocol. That's why I layer 13 deterministic business rules on top of LLM output. The rules catch things the LLM might miss — like the creatinine requirement for contrast injection, or the pediatric coordination flag. Rules are also auditable and testable. I have 180 unit tests that run without an API key using the regex fallback."*

### "How would you evaluate extraction accuracy?"
> *"In the POC, I use 105 synthetic samples with known expected values. For production, I'd build an evaluation harness: annotate a test set of ~500 real documents with ground truth, run both the LLM and regex extractors, and compute precision/recall per field. I'd also track confidence calibration — does 0.8 confidence actually mean 80% of fields are correct? And I'd set up drift monitoring to alert when extraction accuracy drops, which could indicate a change in input format."*

### "How does the OCR work?"
> *"Two tiers. For PDFs with a text layer — which is most hospital-generated documents — I use pdfplumber, which extracts text directly without OCR. For scanned faxes and images, I first do preprocessing — convert to grayscale, apply sharpening — then run Tesseract OCR with the French language pack. This two-tier approach means ~80% of documents process in milliseconds."*

### "Why not use a more advanced OCR like Azure Document Intelligence?"
> *"For the POC, Tesseract is sufficient and keeps it self-contained — no cloud dependencies for OCR. For production, I'd absolutely evaluate Azure Document Intelligence or Google Cloud Vision for their layout analysis capabilities, especially for forms and tables that Tesseract struggles with. But the architecture is designed for this — the OCR service is a single function, swapping the implementation is a one-file change."*

### "How does the confidence scoring work?"
> *"It's based on field completeness. I start at 0.95 (max) and deduct based on what's missing. Critical fields like patient name and modality cause larger deductions. The score never reaches 1.0 because I don't think any automated extraction system should claim 100% confidence on unstructured text. In production, I'd calibrate this against ground truth and potentially incorporate LLM logprobs."*

### "Tell me about the frontend."
> *"Next.js App Router with Tailwind. Two main views: an inbox with a table listing all requests — filterable by status and modality — and a detail view with a two-column layout: original raw text on the left, editable structured form on the right. Everything is in French with proper vouvoiement. The key UX decision was making everything editable before sending — the AI extracts, the human reviews and corrects, then sends the acknowledgement. Human-in-the-loop by design."*

### "How would this handle real patient data?"
> *"The POC uses 100% synthetic data. For production: GDPR and HDS (Hébergeur de Données de Santé) compliance. All data at rest encrypted, TLS in transit, audit logging on every access, role-based access control, data retention policies, and deployment on an HDS-certified cloud provider. The LLM calls would also need to be evaluated for data residency — French hospitals may require that patient data stays in EU data centers."*

### "What would you change for production?"
> *"Five things: (1) PostgreSQL instead of SQLite — proper relational schema, concurrent access. (2) Real email integration via IMAP for ingestion. (3) Authentication — SSO with hospital Active Directory. (4) Async processing — Celery for batch ingestion of large volumes. (5) Monitoring — extraction accuracy drift alerts, confidence calibration dashboards, and proper structured logging."*

---

## 10. Tricky Follow-Up Questions

### "What if the LLM hallucinates a patient name?"
> *"Good question. The validator can't know if a name is hallucinated — it only checks if it's present. This is exactly why the human-in-the-loop design matters. The raw text is displayed alongside the extracted form so the secretary can visually verify. In production, I'd also cross-reference extracted patient names against the hospital's patient registry (HIS) to flag unknown patients."*

### "What about latency? Can a secretary wait 2-3 seconds per request?"
> *"For the triage workflow, yes — they're processing one at a time and the extraction happens at upload time, not at view time. But for batch ingestion of 100+ files, I'd make it async. The demo already handles batch ingestion synchronously, but production would use a job queue. The regex fallback path is near-instant if the LLM is too slow."*

### "Why 105 samples? Is that enough?"
> *"For a POC, yes. It covers every edge case I identified: clean requests, ambiguous exams, missing fields, faxes, pediatric cases, lab results, walk-ins, and unsigned emails. Each sample tests a specific scenario. In production, I'd need 500-1000 annotated real documents to properly evaluate extraction accuracy."*

### "What's the most complex business rule?"
> *"The routing priority logic. When multiple fields are missing, the system has to decide who to contact first: prescriber (for clinical info), patient (for scheduling), or radiologist (for urgent validation). The priority order is: prescriber clinical info > prescriber contact > patient contact > attachments. And if the request is urgent and complete, it skips straight to radiologist validation. This mirrors how experienced secretaries actually triage."*

### "How do you handle edge cases in French medical text?"
> *"The regex extractor has specific patterns for French conventions — date formats (DD/MM/YYYY), phone numbers (06/07 prefix for mobile, 04 for landline in southern France), abbreviations ('M.' for Monsieur, 'Mme' for Madame), and medical terminology mapping ('coroscanner' → Scanner, 'remnance' → IRM, 'rx' → Radio). The LLM handles these naturally because it's trained on French text, but the regex fallback needs explicit patterns."*

---

## 11. What You'd Do Differently in Production

Use this to show you think beyond POC:

| POC | Production |
|-----|------------|
| SQLite | PostgreSQL (concurrent access, proper schema) |
| JSON blob storage | Relational schema with indexed fields |
| Mock email send | Hospital-approved secure email relay |
| OpenAI API | Evaluate Mistral (French-first), self-hosted models for data residency |
| 105 synthetic samples | 500+ annotated real documents + evaluation harness |
| No auth | SSO with hospital Active Directory |
| Synchronous processing | Celery/Redis for async batch ingestion |
| No audit log | Full audit trail (GDPR, HDS compliance) |
| Confidence = completeness | Confidence calibrated against ground truth |
| Manual prompt iteration | Prompt versioning + A/B testing framework |

---

## 12. Quick Vocabulary Reference

In case they ask about French medical terms:

| French | English |
|--------|---------|
| Ordonnance | Medical prescription/order |
| Créatinine | Creatinine (kidney function test) |
| Injection de produit de contraste | Contrast agent injection |
| Vouvoiement | Formal "you" (vous) — mandatory in hospital communication |
| Secrétariat | Administrative office/reception |
| IRM | MRI (Imagerie par Résonance Magnétique) |
| Coroscanner | Coronary CT scan |
| Prise de sang | Blood test |
| RIS | Radiology Information System |
| HDS | Hébergeur de Données de Santé (health data hosting certification) |
| Demande d'examen | Exam request |
| Accusé de réception | Acknowledgement of receipt |

---

## Final Reminders

1. **Lead with the problem**, not the solution. Paint the picture of the overwhelmed secretary first.
2. **The key narrative**: "AI extracts, rules validate, humans decide." This shows mature AI thinking.
3. **Don't apologize for it being a POC** — 180 tests, 105 samples, full pipeline, working UI. That's more than many production systems.
4. **If they ask about something you didn't build** (e.g., real email integration), pivot to the architecture: "The ingest service is a single function — swapping file ingestion for IMAP polling is a one-file change because the downstream pipeline only sees normalized text."
5. **Show the code**: the repo is public at `github.com/Mauricec95/medical-triage-poc`. If they want to see code, the best files to show are:
   - `models/request.py` — the Pydantic schema (136 lines, clean)
   - `services/validator.py` — the 13 business rules (397 lines, well-commented)
   - `services/regex_extractor.py` — the French regex patterns (278 lines)
   - `prompts/extract_request.fr.md` — the LLM system prompt
6. **Confidence**: You built this. You know every line. Own it.
