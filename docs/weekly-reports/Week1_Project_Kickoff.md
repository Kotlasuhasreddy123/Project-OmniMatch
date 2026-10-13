# OmniMatch — Weekly Progress Report
## Week 1: Project Kickoff & Requirements Definition

**Course:** CPSC-69100 — Computer Science Master's Project
**Team:** HealthTech Innovation Labs
**Advisor:** Dr. Khaled Alzoubi
**Submission Date:** Week 1, Fall 2026

---

### 1. Team Activities This Week

| Activity | Owner | Status |
|----------|-------|--------|
| Project charter drafted and signed | Suhas | ✅ Complete |
| Stakeholder kick-off meeting held (Zoom, Sept 6) | All | ✅ Complete |
| Problem statement and scope finalized | All | ✅ Complete |
| Requirements table (REQ-01 to REQ-11) drafted | Suhas, Rosie | ✅ Complete |
| GitHub repository created and team added | Suhas | ✅ Complete |
| AWS Educate account provisioned | Suhas | ✅ Complete |
| Technology stack decision made | All | ✅ Complete |
| Development methodology selected (Agile, 2-week sprints) | All | ✅ Complete |

---

### 2. Problem Definition

Physicians spend an average of 15.5 minutes per patient on direct care while simultaneously managing administrative documentation burdens *(AMA, 2024)*. There are currently over 500,000 active clinical trials listed on ClinicalTrials.gov *(NIH, 2025)*, yet manual trial matching is impractical for busy clinicians.

**OmniMatch** addresses this gap by providing an ambient AI system that:
- Listens to doctor-patient conversations with explicit consent
- Automatically extracts structured clinical entities using NLP
- Matches patients to relevant clinical trials via vector search
- Routes matches to an asynchronous inbox for end-of-day review

---

### 3. Key Decisions Made

**Decision 1 — Asynchronous Inbox over Real-Time Alerts**
*Rationale:* Clinical stakeholder (Venkata, acting as clinical rep) noted that real-time pop-up alerts disrupt patient visits and break care continuity. The team pivoted to an end-of-day asynchronous review model.

**Decision 2 — Patient Consent as Hard Code-Level Gate**
*Rationale:* IT Security officer (Rosie) mandated that audio recording cannot begin without explicit, audit-logged patient consent. This constraint is enforced at the code level, not just the UI level.

**Decision 3 — RAM-Only Audio Processing**
*Rationale:* HIPAA alignment requires that no raw audio containing potential PHI is ever written to disk. All audio buffers are processed in-memory via `io.BytesIO`.

**Decision 4 — Technology Stack**
- Backend: Python 3.11 + FastAPI (async)
- Frontend: Next.js 14 + React 18 + Tailwind CSS
- AI/ML: OpenAI Whisper (ASR) + spaCy NegEx (NLP)
- Database: Qdrant (vector) + SQLite (audit/inbox)
- Cloud: AWS Free Tier (EC2 t2.micro)

---

### 4. Requirements Summary (REQ-01 to REQ-11)

| REQ ID | Type | Description | Priority |
|--------|------|-------------|---------|
| REQ-01 | Functional | Patient consent toggle before mic activation | High |
| REQ-02 | Functional | Whisper ASR, WER < 8% | High |
| REQ-03 | Functional | NegEx entity extraction, ≥95% negation accuracy | High |
| REQ-04 | Functional | Human-in-the-loop verification UI | High |
| REQ-05 | Functional | ClinicalTrials.gov daily sync | High |
| REQ-06 | Functional | Missing Variables checklist | High |
| REQ-07 | Functional | Async inbox population < 60 seconds | High |
| REQ-08 | Security | RAM-only audio, AES-256 encryption | High |
| REQ-09 | Accessibility | WCAG 2.1 Level AA | Medium |
| REQ-10 | Access Control | RBAC (401/403 enforcement) | High |
| REQ-11 | Privacy | Consent audit logs, no cloud PHI | High |

---

### 5. Risks Identified

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|-----------|
| Whisper WER > 8% on medical terms | Medium | High | Use `base` model; add medical vocabulary post-processing |
| Qdrant search latency > 2s | Low | Medium | HNSW index tuning; embedding cache |
| ClinicalTrials.gov API rate limits | Low | Medium | Paginate with delay; fallback to cached data |
| AWS Free Tier resource limits | Medium | Medium | Use t2.micro; optimize Docker image sizes |

---

### 6. Next Week Plan

- [ ] Set up FastAPI project skeleton (Suhas)
- [ ] Configure Qdrant Docker container (Rosie)
- [ ] Scaffold Next.js frontend with Tailwind (Venkata)
- [ ] Implement Patient Consent toggle component (Venkata)
- [ ] Create GitHub Actions CI pipeline (Suhas)

---

### 7. Stakeholder Meeting Minutes (Sept 6, 2026)

**Attendees:** Suhas (PM), Venkata (Acting Clinical Rep), Rosie (Acting IT Security Officer)
**Platform:** Zoom, 6:00 PM CST
**Duration:** 90 minutes

**Key Outcomes:**
1. Approved transition to Asynchronous Clinical Trial Inbox model
2. Confirmed mandatory Patient Consent toggle with audit logging
3. Agreed on Missing Variables Checklist feature
4. Assigned technical responsibilities per team member

---

*Prepared by: Suhas Reddy Kotla | Reviewed by: All Team Members*
