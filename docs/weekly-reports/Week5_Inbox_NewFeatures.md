# OmniMatch — Weekly Progress Report
## Week 5: Async Inbox + 7 New Differentiating Features

**Course:** CPSC-69100 | **Week:** 5 | **Sprint:** Sprint 2 (Week 2 of 2)

---

### 1. Team Activities This Week

| Activity | Owner | Hours | Status |
|----------|-------|-------|--------|
| InboxDashboard — expandable rows, WCAG | Venkata | 6 | ✅ |
| Eligibility breakdown UI component | Venkata | 4 | ✅ |
| ReferralButton component (NEW Feature 5) | Venkata | 3 | ✅ |
| Longitudinal patient timeline service (NEW Feature 3) | Suhas | 5 | ✅ |
| Timeline page `/timeline` | Venkata | 4 | ✅ |
| TimelinePanel sidebar widget | Venkata | 3 | ✅ |
| Eligibility unlock detection | Suhas | 3 | ✅ |
| Sponsor referral webhook service (NEW Feature 5) | Rosie | 4 | ✅ |
| End-of-day digest webhook (NEW Feature 7) | Rosie | 3 | ✅ |
| Rate limiting middleware (OWASP A07) | Rosie | 3 | ✅ |
| Security headers middleware (OWASP A05) | Rosie | 2 | ✅ |
| Input sanitization — clinical text (OWASP A03) | Rosie | 2 | ✅ |

**Total Hours This Week:** 42

---

### 2. All 7 New Features Completed

#### Feature 1 — Per-Criterion Eligibility Breakdown ✅
- `criterion_engine.py`: MET/NOT_MET/MISSING/UNKNOWN verdicts
- `EligibilityBreakdown.tsx`: visual panel in inbox
- **Gap filled:** No existing system (TrialMatchAI, PRISM, TrialGPT) provides this

#### Feature 2 — Enrollment Readiness Score (0-100%) ✅
- Composite: similarity(35%) + inclusion_rate(45%) − exclusion_penalty(20%)
- Shown as circular gauge with color coding (green/amber/red)
- **Gap filled:** All existing systems return only cosine similarity

#### Feature 3 — Longitudinal Patient Visit Timeline ✅
- `timeline_service.py`: entities accumulate across sessions per patient pseudonym
- `detect_eligibility_unlocks()`: alerts when new visit fills a previously-MISSING criterion
- Dedicated `/timeline` page with type-grouped display
- **Gap filled:** All ambient systems (DAX, Abridge) are single-session only

#### Feature 4 — Geographic Proximity Ranking ✅
- `proximity_service.py`: haversine distance from clinic ZIP to trial sites
- `?clinic_zip=10001` query parameter on match endpoint
- Trials within 200 miles ranked above distant trials at same score
- **Gap filled:** No existing matching system incorporates geography

#### Feature 5 — Sponsor Referral Routing ✅
- `digest_service.py` `initiate_referral()`: logs referral + fires webhook
- `ReferralButton.tsx`: one-click from inbox item
- Audit trail: username, timestamp, NCT ID, met criteria — zero PHI
- **Gap filled:** No ambient system provides path from match to referral

#### Feature 6 — Transcript Confidence Heatmap ✅
- Whisper `word_timestamps=True` returns per-word probability
- `TranscriptHeatmap.tsx`: green/amber/red highlighting
- Click Edit → correct word → flag `human_verified=true` in audit log
- **Gap filled:** Whisper errors propagate silently in all existing systems

#### Feature 7 — End-of-Day Digest Webhook ✅
- APScheduler at 17:00 UTC
- Payload: unread count, sessions today, deep link to inbox
- Auto-suppressed if zero unread items
- **Gap filled:** No ambient system pushes async summaries to Slack/Teams

---

### 3. Security Hardening Completed

| Control | Implementation | OWASP |
|---------|---------------|-------|
| Rate limiting | 5/min auth; 30/min API (sliding window) | A07 |
| Security headers | X-Frame-Options, HSTS, nosniff, Permissions-Policy | A05 |
| Input sanitization | `sanitize_clinical_text()` removes control chars, HTML | A03 |
| Bandit scanner | `.bandit.yml` — 40+ checks; fails on MEDIUM/HIGH | A06 |
| SQL injection check | `validate_no_sql_injection()` on clinical text fields | A03 |

---

### 4. Test Results

- ✅ TEST-05: Inbox populated within 60 seconds of session completion
- ✅ TEST-07: All WCAG accessibility schema fields present
- ✅ Feature 3: Timeline accumulates entities across 2 sessions, mention_count=2
- ✅ Feature 3: Eligibility unlock detected when new session fills MISSING criterion
- ✅ Rate limiter returns HTTP 429 after 5 auth attempts in 60s

---

### 5. Milestone M3 Achieved

**M3: Human-in-Loop UI — Target: Week 7 ✅ (completed Week 5)**

| Component | Status |
|-----------|--------|
| Consent, Verification, Inbox UI | ✅ Complete |
| Staff can approve terms; inbox populates | ✅ Verified |
| WCAG 2.1 AA compliance | ✅ All aria-labels, focus rings |
| RBAC enforcement | ✅ 401/403 confirmed |

---

### 6. Next Week Plan

- [ ] Full system integration test (all services running) (All)
- [ ] Run all 8 TEST IDs from project plan (All)
- [ ] AWS CloudFormation deployment (Suhas)
- [ ] Bandit security scan — zero HIGH severity (Rosie)
- [ ] Generate project documentation (All)

---

*Prepared by: Suhas Reddy Kotla | Reviewed by: All Team Members*
