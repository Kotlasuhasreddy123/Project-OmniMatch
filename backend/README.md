# OmniMatch Backend

FastAPI backend for the OmniMatch system. Handles audio ingestion, Whisper ASR transcription, NegEx NLP pipeline, ClinicalTrials.gov sync, Qdrant vector matching, and the async clinical trial inbox.

## Setup

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python -m spacy download en_core_web_sm
cp .env.example .env
# Start Qdrant: docker run -p 6333:6333 qdrant/qdrant:v1.10.0
uvicorn app.main:app --reload --port 8000
```

## API Endpoints

### Authentication
| Method | Path | Auth | Description |
|--------|------|------|-------------|
| `POST` | `/api/v1/auth/login` | No | Authenticate and receive JWT token |

### Consent (REQ-01, REQ-11)
| Method | Path | Auth | Description |
|--------|------|------|-------------|
| `POST` | `/api/v1/consent` | Bearer | Log CONSENT_GRANTED or CONSENT_REVOKED to append-only audit log |

### Audio (REQ-08)
| Method | Path | Auth | Description |
|--------|------|------|-------------|
| `POST` | `/api/v1/audio/transcribe` | Bearer | Transcribe audio via Whisper — RAM-only, no disk writes |

### NLP (REQ-03)
| Method | Path | Auth | Description |
|--------|------|------|-------------|
| `POST` | `/api/v1/nlp/extract` | Bearer | Extract clinical entities with NegEx negation detection |

### Trial Matching (REQ-05, REQ-06)
| Method | Path | Auth | Description |
|--------|------|------|-------------|
| `POST` | `/api/v1/match/search` | Bearer | Search Qdrant with approved entities; returns matches + missing variables |
| `POST` | `/api/v1/trials/sync` | Bearer (ADMIN) | Manual ClinicalTrials.gov → Qdrant sync |

### Sessions (REQ-07)
| Method | Path | Auth | Description |
|--------|------|------|-------------|
| `POST` | `/api/v1/sessions/{id}/complete` | Bearer | Complete visit session and trigger background matching |

### Inbox (REQ-07, REQ-10)
| Method | Path | Auth | Role Required | Description |
|--------|------|------|---------------|-------------|
| `GET` | `/api/v1/inbox` | Bearer | CLINICAL_STAFF, ADMIN | List all inbox items |
| `GET` | `/api/v1/inbox/{id}` | Bearer | CLINICAL_STAFF, ADMIN | Get single inbox item |
| `DELETE` | `/api/v1/inbox/{id}` | Bearer | CLINICAL_STAFF, ADMIN | Mark item as reviewed |

### Health
| Method | Path | Auth | Description |
|--------|------|------|-------------|
| `GET` | `/api/v1/health` | No | System health — Qdrant connectivity, Whisper status |

## Running Tests

```bash
pytest                          # all tests
pytest tests/test_consent.py    # TEST-01: consent + audio gating
pytest tests/test_nlp_pipeline.py  # TEST-02: 20 transcripts, ≥95% negation accuracy
pytest tests/test_matching.py   # TEST-03: rejection exclusion; TEST-05: 60s inbox
pytest tests/test_rbac.py       # TEST-08: 401/403 enforcement
pytest --cov=app --cov-report=term-missing  # with coverage
```

## Security Notes

- Audio bytes → `io.BytesIO()` only. `open(..., "wb")` on audio is forbidden and caught by the Bandit hook.
- JWT secret loaded from `.env` via `pydantic-settings`. Never hardcoded.
- Audit log table is append-only — no UPDATE or DELETE queries are issued on it.
- Inbox endpoints enforce `require_role(["CLINICAL_STAFF", "ADMIN"])` at the FastAPI dependency level.
