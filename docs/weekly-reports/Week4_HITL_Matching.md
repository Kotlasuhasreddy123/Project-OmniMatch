# OmniMatch — Weekly Progress Report
## Week 4: Human-in-the-Loop UI + Trial Match Engine

**Course:** CPSC-69100 | **Week:** 4 | **Sprint:** Sprint 2 (Week 1 of 2)

---

### 1. Team Activities This Week

| Activity | Owner | Hours | Status |
|----------|-------|-------|--------|
| Trial match engine — Qdrant cosine search | Suhas | 5 | ✅ |
| Per-criterion eligibility breakdown (NEW Feature 1) | Suhas | 8 | ✅ |
| Enrollment readiness score 0-100% (NEW Feature 2) | Suhas | 4 | ✅ |
| Missing variables generator | Suhas | 3 | ✅ |
| Geographic proximity ranking (NEW Feature 4) | Suhas | 4 | ✅ |
| EntityChip component (WCAG 2.1 AA) | Venkata | 6 | ✅ |
| VerificationPanel — HITL approval screen | Venkata | 5 | ✅ |
| RBAC middleware — `require_role()` FastAPI dep | Rosie | 4 | ✅ |
| Inbox router — CRUD + RBAC enforcement | Rosie | 5 | ✅ |
| Session completion + BackgroundTask pipeline | Rosie | 4 | ✅ |

**Total Hours This Week:** 48

---

### 2. Technical Accomplishments

#### Trial Match Engine (REQ-05, REQ-06)

The match engine queries Qdrant using approved entity embeddings and returns:
- Top-10 trials by cosine similarity (threshold ≥ 0.65)
- Per-criterion eligibility breakdown (NEW — Feature 1)
- Enrollment readiness score (NEW — Feature 2)
- Geographic proximity data (NEW — Feature 4)

**Enrollment Readiness Score Formula:**
```
score = (cosine_similarity × 0.35)
      + (inclusion_criteria_met_rate × 0.45)
      - (exclusion_violations × 0.20)
```
This is the **primary differentiating feature** vs. all existing systems (TrialMatchAI, PRISM, TrialGPT) which return only a similarity score.

#### Per-Criterion Eligibility Breakdown (NEW — Feature 1)

Each eligibility criterion is individually evaluated:
| Verdict | Meaning | When Shown |
|---------|---------|-----------|
| ✅ MET | Patient has this condition (approved entity found) | Entity in transcript, approved |
| ❌ NOT_MET | Patient explicitly does NOT have this | Entity detected as negated |
| ⚠️ MISSING | Not mentioned in visit | No entity found for criterion |
| ❓ UNKNOWN | Lab value needed | HbA1c, eGFR, blood pressure required |

**Research basis:** *Brown et al. (2025)* achieved 93% criterion-level accuracy on the n2c2 dataset using LLM-based evaluation. OmniMatch uses deterministic rule-based matching for speed and interpretability.

#### Human-in-the-Loop UI (REQ-04)

`EntityChip` component implements full WCAG 2.1 AA:
```tsx
<button aria-label={`Approve entity: ${entity.term}`} aria-pressed={status === "approved"}>
<button aria-label={`Reject entity: ${entity.term}`} aria-pressed={status === "rejected"}>
```

**Critical safety rule:** The submit button is disabled if zero entities are approved. The backend independently validates — rejected entities return HTTP 400 even if the frontend check is bypassed.

#### RBAC Implementation (REQ-10)

```python
@router.get("/inbox")
async def list_inbox(
    current_user: TokenPayload = Depends(require_role(["CLINICAL_STAFF", "ADMIN"]))
):
```

Test results:
- No token → HTTP 401 ✅
- Tampered token → HTTP 401 ✅
- CLINICAL_STAFF role → HTTP 200 ✅
- ADMIN role → HTTP 200 ✅
- Wrong role → HTTP 403 ✅

---

### 3. Competitive Analysis Update

| Feature | TrialMatchAI | PRISM | OmniMatch |
|---------|-------------|-------|-----------|
| Ambient audio | ❌ | ❌ | ✅ |
| Per-criterion breakdown | Partial | ❌ | ✅ Enhanced |
| Enrollment readiness score | ❌ | ❌ | ✅ NEW |
| Geographic proximity | ❌ | ❌ | ✅ NEW |
| Human verification | ❌ | ❌ | ✅ |
| Async inbox | ❌ | ❌ | ✅ |

---

### 4. Test Results

- ✅ TEST-03: All-rejected payload → HTTP 400 (rejected entities never reach Qdrant)
- ✅ TEST-08: Unauthenticated inbox → HTTP 401
- ✅ TEST-08: Wrong role (clinical_staff on /trials/sync) → HTTP 403
- ✅ Enrollment readiness score range [0, 100] validated
- ✅ Criterion engine processes 10 criteria in < 12ms

---

### 5. Next Week Plan

- [ ] Async inbox UI — InboxDashboard with expandable rows (Venkata)
- [ ] Patient visit timeline (NEW Feature 3) (Suhas)
- [ ] Sponsor referral routing (NEW Feature 5) (Rosie)
- [ ] Rate limiting + security middleware (Rosie)
- [ ] Full end-to-end integration test (All)

---

*Prepared by: Suhas Reddy Kotla | Reviewed by: All Team Members*
