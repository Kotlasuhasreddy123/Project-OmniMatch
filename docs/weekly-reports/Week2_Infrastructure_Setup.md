# OmniMatch — Weekly Progress Report
## Week 2: Infrastructure Setup & Project Scaffold

**Course:** CPSC-69100 | **Week:** 2 | **Sprint:** Sprint 1 (Week 1 of 2)

---

### 1. Team Activities This Week

| Activity | Owner | Hours | Status |
|----------|-------|-------|--------|
| GitHub repo structure + branch strategy | Suhas | 3 | ✅ |
| FastAPI app skeleton (`main.py`, `config.py`) | Suhas | 4 | ✅ |
| Pydantic v2 schemas for all API models | Suhas | 3 | ✅ |
| Docker Compose dev/test/prod configs | Rosie | 4 | ✅ |
| Qdrant Docker container + collection setup | Rosie | 3 | ✅ |
| Next.js 14 project with App Router + Tailwind | Venkata | 5 | ✅ |
| Patient Consent Toggle component (WCAG 2.1 AA) | Venkata | 4 | ✅ |
| JWT authentication + bcrypt password hashing | Rosie | 4 | ✅ |
| AWS CloudFormation template (VPC, EC2, S3) | Suhas | 5 | ✅ |
| `.env` secret management via pydantic-settings | Rosie | 2 | ✅ |

**Total Hours This Week:** 37

---

### 2. Technical Accomplishments

#### Backend Infrastructure
- FastAPI application bootstrapped with async lifecycle events
- Pydantic v2 models for all 15 request/response schemas
- aiosqlite database initialization with 5 tables (audit_log, users, inbox_items, patient_timeline, referrals)
- JWT handler with `require_role()` dependency factory for RBAC
- Consent router writing to append-only audit log

#### Frontend Infrastructure
- Next.js 14 App Router configured with TypeScript strict mode
- Tailwind CSS with custom brand color palette
- `ConsentToggle` component with full WCAG 2.1 AA attributes:
  - `role="switch"`, `aria-checked`, `aria-label`, `aria-describedby`
  - Visible focus rings, color + icon (not color alone)
- `useConsent` hook — logs to backend BEFORE toggling local state

#### DevOps
- Three Docker Compose profiles: dev (hot-reload), test (ephemeral DB), prod (read-only FS)
- AWS CloudFormation template: VPC, EC2 t2.micro, ALB, S3 audit bucket (AES-256, 7-year retention)
- Nginx reverse proxy config with TLS 1.3 enforcement

---

### 3. Architecture Diagram

```
Browser (Next.js)
    │
    ├─ ConsentToggle ──► POST /api/v1/consent ──► SQLite audit_log
    │
    ├─ AudioRecorder ──► POST /api/v1/audio/transcribe ──► io.BytesIO (RAM only)
    │
    └─ (future) EntityChip ──► POST /api/v1/match/search ──► Qdrant
```

---

### 4. Security Controls Implemented

| Control | Implementation | Requirement |
|---------|---------------|-------------|
| Password hashing | bcrypt, cost factor 12 | REQ-10 |
| JWT signing | HS256, 8-hour expiry | REQ-10 |
| Secrets management | pydantic-settings + .env | REQ-08 |
| Audit log append-only | No UPDATE/DELETE on audit_log | REQ-11 |
| Audio RAM-only | `io.BytesIO` enforced | REQ-08 |

---

### 5. Challenges & Resolutions

| Challenge | Resolution |
|-----------|-----------|
| `next.config.ts` not supported by Next.js 14.2 | Renamed to `next.config.js` |
| Docker `version` attribute obsolete warning | Removed `version: "3.9"` from all compose files |
| Docker Desktop Linux engine not starting | Confirmed context `desktop-linux` active; verified `Engine running` status |
| Duplicate `export default` in session page | Removed old version, kept updated implementation |

---

### 6. Test Results This Week

- ✅ Docker build: frontend (7 pages compiled), backend (Python + spaCy installed)
- ✅ FastAPI starts on port 8000 — health check returns `{"status":"ok"}`
- ✅ Next.js builds all 7 routes successfully
- ✅ JWT login endpoint returns valid token for demo users

---

### 7. Next Week Plan

- [ ] Implement Whisper ASR transcription endpoint (Suhas)
- [ ] Build NLP NegEx pipeline (Suhas)
- [ ] ClinicalTrials.gov API v2 client (Rosie)
- [ ] Qdrant vector upsert pipeline (Rosie)
- [ ] AudioRecorder component with consent gate (Venkata)

---

*Prepared by: Suhas Reddy Kotla | Reviewed by: All Team Members*
