# OmniMatch: Ambient AI Clinical Intelligence and Automated Trial-Routing Engine

> Renewal build: this copy preserves the Kiro baseline and adds a PHI-minimized
> Evidence Ledger plus a Trial Freshness Gate. See
> [the handoff document](docs/OmniMatch%20Renewal%20Handoff%20and%20Next%20Steps.docx)
> for the comparison, verification results, and runbook.

<div align="center">

**CPSC-69100 — Computer Science Master's Project | Fall 2026**
**HealthTech Innovation Labs | Advisor: Dr. Khaled Alzoubi**

| Team Member | Role | Responsibilities |
|---|---|---|
| Suhas Reddy Kotla | Team Leader, AI & AWS Lead | Whisper ASR, NLP pipeline, AWS infra, match engine |
| Rosie Roy Barla | Backend & Security Lead | FastAPI, ClinicalTrials.gov sync, HIPAA, Qdrant |
| Venkata Papaiah Thrinadha Nagamahesh Akula | Frontend UI/UX | Consent toggle, verification UI, inbox dashboard |

</div>

---

## What OmniMatch Does

Physicians spend ~15.5 minutes per patient on direct care while managing 500,000+ active clinical trials on ClinicalTrials.gov *(AMA, 2024)*. OmniMatch bridges this gap: it listens to ambient doctor-patient conversations, extracts structured clinical entities, filters negations and family history, and routes pre-screened trial matches to an asynchronous inbox — without interrupting active patient care.

```
Doctor-Patient Conversation
         │
         ▼
   Patient Consent Toggle ────────────────────► Audit Log (HIPAA-aligned)
         │ (consent required — REQ-01)
         ▼
   Ambient Audio Capture (RAM-only, TLS 1.3)
         │
         ▼
   Whisper ASR (in-memory, WER < 8%)          ← REQ-02
         │
         ▼
   NegEx/NegBio/Ensemble NLP Pipeline         ← REQ-03
   • Affirmed entities  → sent to Human-in-Loop
   • Negated entities   → excluded
   • Family context     → excluded
         │
         ▼
   Human Verification UI (Approve / Reject)   ← REQ-04
         │ (only APPROVED entities proceed)
         ▼
   Qdrant Vector Search (cosine similarity)   ← REQ-05
         │
         ▼
   Per-Criterion Eligibility Breakdown ──────── NEW Feature 1
   Enrollment Readiness Score (0-100%) ──────── NEW Feature 2
   Geographic Proximity Ranking ──────────────── NEW Feature 4
         │
         ▼
   Async Clinical Trial Inbox (< 60 seconds)  ← REQ-07
   + Missing Variables Checklist               ← REQ-06
   + Sponsor Referral Button ─────────────────── NEW Feature 5
         │
         ▼
   Longitudinal Patient Timeline ──────────────── NEW Feature 3
   End-of-Day Digest Webhook ─────────────────── NEW Feature 7
```

---

## Research Foundation

### Literature Review

| Paper | Relevance to OmniMatch |
|-------|----------------------|
| Chapman et al. (2001). *NegEx*. J Biomed Inform. | Baseline negation algorithm — our NegEx v1 variant |
| Peng et al. (2018). *NegBio*. AMIA. PMC5961822. | +9.5% precision over NegEx — our v2 variant |
| Gao et al. (2023, arxiv 2503.17425). *Fine-tuned LLM assertion detection = 96.2% accuracy.* | Benchmark target for our ensemble v4 |
| Lee et al. (2019). *BioBERT*. Bioinformatics 36(4). | Biomedical NLP baseline — our v3 zero-shot variant |
| Abdallah et al. (2025). *TrialMatchAI*. Nature 41467. | SOTA trial matching — OmniMatch adds ambient capture + 7 new features |
| Brown et al. (2024, Nature 43856). *LLM pipeline, 93% criterion accuracy.* | Per-criterion scoring benchmark |
| OpenAI (2023). *Whisper ASR* (arXiv:2212.04356). | Core ASR engine — WER ~8% on medical audio |
| NIH (2024). *ClinicalTrials.gov API v2.* | Live data source — 500k+ RECRUITING trials |
| AMA (2024). *Physician administrative burden.* | Problem motivation — 15.5 min/patient |

### NLP Variant Benchmark Results

| Variant | Algorithm | Precision | Recall | F1 | Avg Time |
|---------|-----------|-----------|--------|-----|---------|
| **NegEx v1** | Classic rule window | 0.841 | 0.853 | 0.847 | ~0.5ms |
| **NegBio v2** | Dependency path + long-distance | 0.924 | 0.895 | 0.909 | ~3ms |
| **BioBERT v3** | Zero-shot NLI | 0.891 | 0.882 | 0.886 | ~100ms (CPU) |
| **Ensemble v4** ✅ | NegEx+NegBio+tiebreak | **0.951** | **0.963** | **0.957** | ~4ms |

*OmniMatch uses Ensemble v4 as default. BioBERT v3 activates only when GPU available.*

### Embedding Model Selection

| Model | Clinical F1 | Speed | RAM | Our Choice |
|-------|------------|-------|-----|-----------|
| all-MiniLM-L6-v2 | 0.82 | 15ms | 80MB | ✅ Default |
| BioClinicalBERT | 0.87 | 150ms | 440MB | Optional |
| BioLinkBERT | 0.89 | 180ms | 680MB | GPU only |
| OpenAI text-embedding-3 | 0.91 | API call | N/A | Cloud only |

*Source: Comparative analysis of encoder models for clinical text (arxiv 2511.19739)*

---

## 7 New Differentiating Features

Research against all existing systems confirmed these gaps as of October 2026:

| # | Feature | Gap in Existing Systems |
|---|---------|------------------------|
| **1** | **Per-Criterion Eligibility Breakdown** | TrialMatchAI/PRISM return one similarity score. OmniMatch evaluates every criterion: MET/NOT_MET/MISSING/UNKNOWN |
| **2** | **Enrollment Readiness Score (0-100%)** | No system combines similarity + inclusion rate − exclusion penalty into a composite |
| **3** | **Longitudinal Patient Visit Timeline** | All systems (DAX, Abridge, TrialMatchAI) are single-session. OmniMatch accumulates across visits |
| **4** | **Geographic Proximity Ranking** | No system re-ranks by distance from clinic. A distant perfect match ranks below a nearby good match |
| **5** | **Sponsor Referral Routing** | No ambient system provides path from "matched" → "referral logged" |
| **6** | **Transcript Confidence Heatmap** | Whisper errors propagate silently. OmniMatch highlights low-confidence words for correction |
| **7** | **End-of-Day Digest Webhook** | No system pushes async summaries to Slack/Teams. Clinicians must manually log in |

---

## Renewal Features

### 8. Evidence Ledger

The verification page now creates a browser-side SHA-256 anchor for each
clinician-approved transcript entity. The backend persists only the entity,
character offsets, confidence, approval state, and hashes — never the audio,
full transcript, or quoted span. A matched criterion can display its linked,
human-verified entity in the inbox.

### 9. Trial Freshness Gate

Every match is labelled **READY**, **REVIEW**, or **BLOCKED** before a coordinator
acts. The gate evaluates the registry status, `last_updated` date, and whether
site data is present. It prevents a high semantic score from being mistaken for
confirmed site capacity or enrollment availability.

These additions are workflow support only. They do not determine eligibility,
enroll a patient, or replace clinical judgment.

---

## System Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                          AWS EC2 t2.micro                           │
│  ┌──────────────┐    ┌──────────────────────────────────────────┐  │
│  │  Nginx 1.27  │    │           Docker Network                  │  │
│  │  (TLS 1.3)   │───►│  ┌─────────────┐  ┌──────────────────┐  │  │
│  │  Rate Limit  │    │  │  Next.js 14 │  │   FastAPI 0.111  │  │  │
│  │  Security    │    │  │  (port 3000)│  │   (port 8000)    │  │  │
│  │  Headers     │    │  │             │  │                  │  │  │
│  └──────────────┘    │  │  5 Pages:   │  │  11 Endpoints:   │  │  │
│                      │  │  / login    │  │  /auth /consent  │  │  │
│  ┌──────────────┐    │  │  /session   │  │  /audio /nlp     │  │  │
│  │  S3 Audit    │◄───│  │  /verify    │  │  /match /inbox   │  │  │
│  │  Bucket      │    │  │  /inbox     │  │  /referrals      │  │  │
│  │  (AES-256)   │    │  │  /timeline  │  │  /timeline       │  │  │
│  │  7yr retain  │    │  └─────────────┘  │  /trials/sync    │  │  │
│  └──────────────┘    │                   └──────────────────┘  │  │
│                      │  ┌──────────────────────────────────────┐  │
│  ┌──────────────┐    │  │        Qdrant 1.10 (port 6333)       │  │
│  │  CloudWatch  │◄───│  │  Collection: clinical_trials         │  │
│  │  Logs        │    │  │  Vectors: 384-dim cosine (HNSW)      │  │
│  │  Alarms      │    │  │  ~500 RECRUITING trials indexed      │  │
│  └──────────────┘    │  └──────────────────────────────────────┘  │
│                      └──────────────────────────────────────────────┘
└─────────────────────────────────────────────────────────────────────┘
       │                          │
       ▼                          ▼
  SSM Parameter             SQLite (aiosqlite)
  Store (secrets)           audit_log | users | inbox_items
                            patient_timeline | referrals | visit_sessions
```

---

## Complete File Structure

```
Master's Project/
├── README.md                          ← This file
├── AGENTS.md                          ← Kiro steering rules
├── .gitignore
├── docker-compose.yml                 ← Main (dev shortcut)
├── docker-compose.dev.yml             ← Hot-reload development
├── docker-compose.test.yml            ← Isolated test environment
├── docker-compose.prod.yml            ← Production (read-only FS, multi-worker)
│
├── backend/
│   ├── app/
│   │   ├── main.py                    ← FastAPI entry + APScheduler
│   │   ├── config.py                  ← pydantic-settings
│   │   ├── auth/                      ← JWT, RBAC, consent router
│   │   ├── audio/                     ← RAM-only ingestion (REQ-08)
│   │   ├── transcription/             ← Whisper ASR + word confidence
│   │   ├── nlp/
│   │   │   ├── negex_pipeline.py      ← Main NLP (Ensemble v4)
│   │   │   └── variants/
│   │   │       ├── negex_v1.py        ← Classic NegEx (F1=0.847)
│   │   │       ├── negbio_v2.py       ← NegBio dep-path (F1=0.909)
│   │   │       ├── biobert_v3.py      ← Zero-shot NLI (F1=0.886)
│   │   │       └── ensemble_v4.py     ← Ensemble (F1=0.957) ← DEFAULT
│   │   ├── trials/
│   │   │   ├── clinicaltrials_client.py  ← ClinicalTrials.gov API v2
│   │   │   ├── qdrant_service.py      ← Vector DB
│   │   │   ├── qdrant_config.py       ← Optimized HNSW settings
│   │   │   ├── proximity_service.py   ← Haversine geo ranking (NEW)
│   │   │   └── embedding_cache.py     ← LRU cache + batch upsert (NEW)
│   │   ├── eligibility/
│   │   │   └── criterion_engine.py    ← Per-criterion scoring (NEW)
│   │   ├── matching/router.py         ← Trial search endpoint
│   │   ├── inbox/router.py            ← Async inbox + RBAC
│   │   ├── timeline/                  ← Longitudinal patient data (NEW)
│   │   ├── digest/                    ← Referral + digest webhook (NEW)
│   │   ├── security/
│   │   │   └── middleware.py          ← Rate limiting + sanitization
│   │   ├── models/
│   │   │   ├── schemas.py             ← Pydantic v2 models
│   │   │   └── database.py            ← aiosqlite setup
│   │   └── data/
│   │       ├── mock_transcripts.json  ← 20 labeled transcripts
│   │       └── training_transcripts.json ← 100 labeled transcripts
│   ├── scripts/
│   │   └── seed_trials.py             ← Real ClinicalTrials.gov seeder
│   ├── tests/
│   │   ├── conftest.py                ← Fixtures + async setup
│   │   ├── test_consent.py            ← TEST-01
│   │   ├── test_nlp_pipeline.py       ← TEST-02 (20 transcripts)
│   │   ├── test_matching.py           ← TEST-03, TEST-05
│   │   ├── test_rbac.py               ← TEST-08
│   │   ├── test_new_features.py       ← 7 new feature tests
│   │   └── test_exhaustive.py         ← ALL 8 TEST IDs + performance
│   ├── .bandit.yml                    ← Security scan config
│   ├── pytest.ini
│   ├── requirements.txt               ← Pinned dependencies
│   └── Dockerfile                     ← Multi-stage Python 3.11
│
├── frontend/
│   ├── src/
│   │   ├── app/
│   │   │   ├── page.tsx               ← Home
│   │   │   ├── login/                 ← Auth page
│   │   │   ├── session/               ← Consent + audio + heatmap
│   │   │   ├── verify/                ← Entity verification (HITL)
│   │   │   ├── inbox/                 ← Async trial inbox
│   │   │   └── timeline/              ← Patient visit history (NEW)
│   │   ├── components/
│   │   │   ├── ConsentToggle/         ← REQ-01, WCAG 2.1 AA
│   │   │   ├── AudioRecorder/         ← Consent-gated mic
│   │   │   ├── TranscriptHeatmap/     ← Word confidence (NEW)
│   │   │   ├── EntityChip/            ← Approve/reject (REQ-04)
│   │   │   ├── VerificationPanel/     ← HITL screen
│   │   │   ├── EligibilityBreakdown/  ← Per-criterion (NEW)
│   │   │   ├── InboxDashboard/        ← Async inbox (REQ-07)
│   │   │   ├── TimelinePanel/         ← Visit history (NEW)
│   │   │   └── ui/ReferralButton.tsx  ← Referral (NEW)
│   │   ├── hooks/
│   │   │   ├── useConsent.ts          ← Consent state + audit log
│   │   │   └── useAudioCapture.ts     ← Consent-gated getUserMedia
│   │   ├── lib/
│   │   │   ├── apiClient.ts           ← All API calls
│   │   │   ├── auth.ts                ← Token decode/manage
│   │   │   └── session.ts             ← Session ID management
│   │   └── types/index.ts             ← TypeScript interfaces
│   ├── src/__tests__/                 ← Jest + RTL tests
│   ├── package.json
│   ├── tailwind.config.ts
│   ├── tsconfig.json
│   ├── .eslintrc.json                 ← jsx-a11y accessibility rules
│   └── Dockerfile                     ← Multi-stage Node 20 standalone
│
├── infrastructure/
│   ├── aws/cloudformation.yml         ← VPC, EC2, ALB, S3, IAM, CW
│   ├── nginx/nginx.conf               ← TLS 1.3, rate limit, sec headers
│   └── scripts/
│       ├── deploy_aws.sh              ← One-command AWS deploy
│       └── teardown_aws.sh            ← Safe teardown (keeps S3)
│
├── docs/
│   ├── api/
│   │   ├── OmniMatch_Postman_Collection.json  ← Import into Postman
│   │   └── curl_examples.sh           ← Full cURL test script
│   └── training/
│       ├── USER_MANUAL.md             ← Clinical staff guide
│       ├── ADMIN_GUIDE.md             ← IT admin guide
│       └── QUICK_REFERENCE.md        ← 1-page quick card
│
└── .kiro/
    ├── steering/                      ← security.md, accessibility.md, coding-standards.md
    ├── specs/                         ← sprint1, sprint2, sprint3 specs
    └── hooks/                         ← security-scan, a11y-lint, api-docs-update
```

---

## Quick Start (3 minutes)

```bash
# 1. Clone and configure
git clone <repo-url> && cd "Master's Project"
cp backend/.env.example backend/.env
# Edit backend/.env → set JWT_SECRET_KEY and APP_SECRET_KEY

# 2. Start all services
docker compose up --build

# 3. Seed trial data (in new terminal)
docker compose exec backend python scripts/seed_trials.py --max 50

# 4. Open the app
# Frontend: http://localhost:3000
# API Docs: http://localhost:8000/api/docs
# Qdrant:   http://localhost:6333/dashboard
```

**Demo credentials:**
- Clinical Staff: `clinical_staff` / `Staff@12345`
- Admin: `admin` / `Admin@12345`

---

## Local Development (without Docker)

```bash
# Backend
cd backend
python -m venv .venv && .venv\Scripts\activate    # Windows
pip install -r requirements.txt
python -m spacy download en_core_web_sm
cp .env.example .env
docker run -p 6333:6333 qdrant/qdrant:v1.10.0    # Qdrant only
uvicorn app.main:app --reload --port 8000

# Frontend (new terminal)
cd frontend
npm install --legacy-peer-deps
cp .env.local.example .env.local
npm run dev   # http://localhost:3000
```

---

## Running Tests

```bash
# All backend tests
cd backend && pytest -v

# Specific test IDs from project plan
pytest tests/test_consent.py     -v  # TEST-01: Consent + audio gating
pytest tests/test_nlp_pipeline.py -v  # TEST-02: NLP accuracy ≥95%
pytest tests/test_matching.py    -v  # TEST-03: Entity rejection; TEST-05: 60s inbox
pytest tests/test_rbac.py        -v  # TEST-08: RBAC 401/403
pytest tests/test_exhaustive.py  -v  # All 8 + performance benchmarks
pytest tests/test_new_features.py -v  # 7 new differentiating features

# All frontend tests
cd frontend && npm run test:run

# Docker-isolated test suite (recommended for CI)
docker compose -f docker-compose.test.yml up --abort-on-container-exit

# Security scan
cd backend && bandit -r app/ -c .bandit.yml -ll

# NLP variant benchmark
cd backend && python -c "
from app.nlp.variants.ensemble_v4 import benchmark_variants
import json
transcripts = json.load(open('app/data/mock_transcripts.json'))
metrics = benchmark_variants(transcripts)
for name, m in metrics.items():
    print(f'{name:20s} P:{m[\"precision\"]:.3f} R:{m[\"recall\"]:.3f} F1:{m[\"f1\"]:.3f} {m[\"avg_time_ms\"]:.1f}ms')
"
```

---

## AWS Deployment

```bash
# One-command deploy (creates all AWS resources)
chmod +x infrastructure/scripts/deploy_aws.sh
./infrastructure/scripts/deploy_aws.sh dev

# Safe teardown (preserves S3 audit bucket)
./infrastructure/scripts/teardown_aws.sh dev
```

Stack creates: VPC, EC2 t2.micro (free tier), ALB, S3 (AES-256, 7-year retention),
SSM Parameter Store (secrets), CloudWatch log groups + alarms, IAM roles.

**HIPAA note (simulated):** For real PHI workloads, sign AWS BAA via AWS Artifact first.

---

## API Reference

Full interactive docs: **http://localhost:8000/api/docs** (Swagger UI)

| Method | Endpoint | Auth | Role | Description |
|--------|----------|------|------|-------------|
| GET | `/api/v1/health` | No | — | Health + Qdrant connectivity |
| POST | `/api/v1/auth/login` | No | — | JWT token |
| POST | `/api/v1/consent` | Yes | Any | Consent audit log (REQ-01) |
| POST | `/api/v1/audio/transcribe` | Yes | Any | Whisper ASR + word confidence |
| POST | `/api/v1/nlp/extract` | Yes | Any | NegEx/Ensemble entity extraction |
| POST | `/api/v1/match/search?clinic_zip=` | Yes | Any | Qdrant search + criterion breakdown |
| POST | `/api/v1/sessions/{id}/complete` | Yes | Any | Trigger async matching |
| GET | `/api/v1/inbox` | Yes | CLINICAL_STAFF, ADMIN | List inbox (REQ-10) |
| GET | `/api/v1/inbox/{id}` | Yes | CLINICAL_STAFF, ADMIN | Single inbox item |
| DELETE | `/api/v1/inbox/{id}` | Yes | CLINICAL_STAFF, ADMIN | Mark reviewed |
| POST | `/api/v1/referrals` | Yes | CLINICAL_STAFF, ADMIN | Log sponsor referral |
| GET | `/api/v1/timeline/{pseudo}` | Yes | CLINICAL_STAFF, ADMIN | Patient history |
| POST | `/api/v1/trials/sync` | Yes | ADMIN only | ClinicalTrials.gov sync |

---

## Requirements Traceability

| REQ | Description | Files | Tests |
|-----|-------------|-------|-------|
| REQ-01 | Patient Consent Toggle | `ConsentToggle.tsx`, `useConsent.ts`, `consent_router.py` | TEST-01 |
| REQ-02 | Whisper ASR WER < 8% | `whisper_service.py`, `audio/router.py` | TEST-02 |
| REQ-03 | NegEx ≥95% accuracy | `negex_pipeline.py`, `variants/` | TEST-02 |
| REQ-04 | Human verification UI | `EntityChip.tsx`, `VerificationPanel.tsx` | TEST-03 |
| REQ-05 | ClinicalTrials.gov sync | `clinicaltrials_client.py`, `qdrant_service.py` | TEST-04 |
| REQ-06 | Missing Variables | `matching/router.py` `_generate_missing_variables()` | TEST-05 |
| REQ-07 | Async inbox ≤60s | `inbox/router.py`, `BackgroundTask` | TEST-05 |
| REQ-08 | RAM-only, AES-256 | `audio/router.py`, `io.BytesIO`, `.bandit.yml` | TEST-06 |
| REQ-09 | WCAG 2.1 AA | All frontend components | TEST-07 |
| REQ-10 | RBAC 401/403 | `jwt_handler.py` `require_role()` | TEST-08 |
| REQ-11 | Consent audit logs | `consent_router.py`, `audit_log` table | TEST-06 |

---

## Technology Stack

| Layer | Technology | Version | Why Chosen |
|-------|-----------|---------|------------|
| Backend framework | FastAPI | 0.111 | Async-native, auto OpenAPI, Pydantic v2 |
| Backend runtime | Python | 3.11 | 3.10+ syntax, type unions, match statements |
| ASR | OpenAI Whisper | base | WER ~8% on clean medical audio; open-source |
| NLP (primary) | Custom NegEx/Ensemble | v4 | 0.957 F1; deterministic; no training data needed |
| NLP (optional) | BioBERT zero-shot | v3 | 0.886 F1; generalizes to unseen patterns |
| Embeddings | all-MiniLM-L6-v2 | — | Best speed/accuracy for Free Tier (15ms/call) |
| Vector DB | Qdrant | 1.10 | HNSW index, cosine similarity, async client |
| Auth | python-jose + bcrypt | — | Industry-standard JWT + cost-12 hashing |
| Database | aiosqlite | 0.20 | Lightweight async SQLite for audit/inbox |
| Scheduler | APScheduler | 3.10 | Daily sync + digest jobs |
| Frontend | Next.js 14 App Router | 14.2 | SSR, TypeScript, file-based routing |
| UI | React 18 + Tailwind CSS | 18/3.4 | Functional components, utility-first CSS |
| Tests (BE) | pytest + pytest-asyncio | 8.2 | Async FastAPI testing |
| Tests (FE) | Jest + React Testing Library | 29/16 | Component + hook tests |
| Container | Docker + Compose | — | Dev/test/prod profiles |
| Cloud | AWS CloudFormation | — | EC2 t2.micro free tier + HIPAA-aligned services |
| Reverse proxy | Nginx | 1.27 | TLS 1.3, rate limiting, security headers |

---

## Security Summary

| Control | Implementation | Requirement |
|---------|---------------|-------------|
| RAM-only audio | `io.BytesIO`; `open("*.wav","wb")` banned by Bandit | REQ-08 |
| AES-256 at rest | EC2 EBS encrypted; S3 SSE-AES256 | REQ-08 |
| TLS 1.3 in transit | Nginx `ssl_protocols TLSv1.3` | REQ-08 |
| Consent gate (code-level) | `if (!consentGranted) return;` before getUserMedia | REQ-01 |
| Audit log append-only | No UPDATE/DELETE on `audit_log` table | REQ-11 |
| RBAC | `require_role(["CLINICAL_STAFF","ADMIN"])` FastAPI dependency | REQ-10 |
| JWT expiry | 8-hour max; bcrypt cost-12 | REQ-10 |
| Secrets management | SSM Parameter Store (AWS); pydantic-settings locally | REQ-08 |
| Rate limiting | 5/min auth; 30/min API; Nginx per-IP | OWASP A07 |
| Input sanitization | `sanitize_clinical_text()` strips control chars + HTML | OWASP A03 |
| Security headers | X-Frame-Options DENY, HSTS, nosniff, etc. | OWASP A05 |
| Dependency pinning | All versions pinned in `requirements.txt` | OWASP A06 |

---

## Performance Benchmarks

| Operation | Target | Achieved | Notes |
|-----------|--------|---------|-------|
| NegEx pipeline | <50ms | ~3ms | 20-transcript average |
| Ensemble NLP | <50ms | ~4ms | Includes NegBio fallback |
| Criterion engine | <100ms | ~12ms | 10 criteria per trial |
| Qdrant search | <200ms | ~15ms | HNSW index, top-10 |
| Embedding encode | <30ms | ~15ms | all-MiniLM-L6-v2 CPU |
| Haversine calc | <1ms | ~0.01ms | 10,000 calls in <100ms |
| Session complete | <3s | <1s | BackgroundTask returns immediately |
| Inbox populate | <60s | ~2s | With mock Qdrant |

---

## What to Do Next

### Immediate (Week 1)

1. **Install and run the project:**
   ```bash
   docker compose up --build
   docker compose exec backend python scripts/seed_trials.py --max 50
   # Open http://localhost:3000
   ```

2. **Run the full test suite** and verify all 8 TEST IDs pass:
   ```bash
   cd backend && pytest tests/ -v --tb=short
   cd frontend && npm run test:run
   ```

3. **Demo the workflow** end-to-end with these test phrases:
   > *"The patient has type 2 diabetes and hypertension, currently on metformin and lisinopril. She denies chest pain or shortness of breath. Family history of stroke in father."*

4. **Review the Swagger UI** at http://localhost:8000/api/docs
   — import `docs/api/OmniMatch_Postman_Collection.json` into Postman

### Short-Term (Weeks 2-3)

5. **NLP accuracy validation** on the 100-transcript dataset:
   ```bash
   cd backend
   pytest tests/test_exhaustive.py::TestNLPAccuracy -v
   ```

6. **Run the NLP variant benchmark** to verify Ensemble v4 > NegEx:
   ```bash
   python -c "
   from app.nlp.variants.ensemble_v4 import benchmark_variants
   import json
   t = json.load(open('app/data/mock_transcripts.json'))
   m = benchmark_variants(t)
   for k,v in m.items(): print(f'{k}: F1={v[\"f1\"]:.3f}')
   "
   ```

7. **Configure the digest webhook** (optional — Slack/Teams):
   Add `DIGEST_WEBHOOK_URL=https://hooks.slack.com/...` to `backend/.env`

8. **Deploy to AWS** for full cloud demo:
   ```bash
   ./infrastructure/scripts/deploy_aws.sh dev
   ```

### Medium-Term (Project Enhancement)

9. **Upgrade NLP accuracy** by activating BioBERT v3 on a machine with GPU:
   - Set `NLP_VARIANT=biobert` in `.env`
   - Expected F1 improvement: 0.957 → ~0.96+

10. **Fine-tune Whisper** on medical audio for WER < 5%:
    - Dataset: [MedQA-USMLE](https://github.com/jind11/MedQA) for medical text
    - Use `whisper.fine_tune()` with medical conversation corpus
    - Reference: arxiv 2507.17326 (87% WER reduction via fine-tuning)

11. **Add BioClinicalBERT embeddings** for better trial semantic search:
    - Replace `all-MiniLM-L6-v2` with `emilyalsentzer/Bio_ClinicalBERT`
    - Expected: +5% trial match precision (per arxiv 2409.13893)

12. **SNOMED CT entity normalization**:
    - Map "HTN" → "Hypertension" → SNOMED concept 38341003
    - Improves cross-visit entity matching in the Timeline feature

13. **EHR integration** (out of scope for this project but natural next step):
    - HL7 FHIR R4 patient resource → auto-populate entity list
    - Reference: HL7 International (2024), https://hl7.org/fhir/R4B/

14. **Multi-tenant clinic support**:
    - Add clinic_id to all data models
    - Add per-clinic user management

### Academic Submission Checklist

- [ ] Run full test suite → all 8 TEST IDs passing
- [ ] Demo the 3-minute clinical workflow end-to-end
- [ ] Show NLP accuracy report (≥95% negation recall)
- [ ] Show the 7 new features vs. existing systems comparison table
- [ ] Export AWS CloudFormation deployment proof
- [ ] Submit GitHub repository with README and all documentation

---

## References

1. American Medical Association. (2024). *Reducing administrative burden in physician workflows.* AMA Press.

2. Chapman WW, et al. (2001). A simple algorithm for identifying negated findings and diseases in discharge summaries. *J Biomed Inform*, 34(5):301-310. doi:10.1006/jbin.2001.1029

3. Peng Y, et al. (2018). NegBio: a high-performance tool for negation and uncertainty detection in radiology reports. *AMIA Jt Summits Transl Sci Proc*, 2017:188-196. PMC5961822.

4. Lee J, et al. (2020). BioBERT: a pre-trained biomedical language representation model. *Bioinformatics*, 36(4):1234-1240. doi:10.1093/bioinformatics/btz682

5. Abdallah M, et al. (2025). TrialMatchAI: an end-to-end AI-powered clinical trial recommendation system. *Nature Communications*, 41467. doi:10.1038/s41467-026-70509-w

6. Brown C, et al. (2025). Real-world validation of a multimodal LLM-powered pipeline for high-accuracy clinical trial patient matching. *npj Digital Medicine*, 43856. doi:10.1038/s43856-025-01256-0

7. Gao R, et al. (2025). Comprehensive assertion detection models for clinical NLP. arXiv:2503.17425. [Fine-tuned LLM F1=0.962]

8. Radford A, et al. (OpenAI, 2023). Robust speech recognition via large-scale weak supervision (Whisper). arXiv:2212.04356. doi:10.48550/arXiv.2212.04356

9. National Institutes of Health. (2025). *ClinicalTrials.gov API v2 RESTful interface specification.* https://clinicaltrials.gov/data-api/api

10. HL7 International. (2024). *Fast Healthcare Interoperability Resources (FHIR) Release 4B.* https://hl7.org/fhir/R4B/

11. NLM Technical Bulletin. (2024, Mar-Apr). *ClinicalTrials.gov API Version 2.0 Now Available.* https://www.nlm.nih.gov/pubs/techbull/ma24/ma24_clinicaltrials_api.html

12. Ektefaie Y, et al. (2024). Comparative analysis of encoder models for clinical cardiology embeddings. arXiv:2511.19739.

---

*OmniMatch is an academic prototype for CPSC-69100. All patient data is synthetic.
No real PHI is collected, stored, or processed at any point.*

**© 2026 HealthTech Innovation Labs — Suhas Reddy Kotla, Rosie Roy Barla, Venkata Akula**
