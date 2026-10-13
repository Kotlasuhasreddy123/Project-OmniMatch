# OmniMatch — Weekly Progress Report
## Week 7: Final Delivery, AWS Deployment & Project Handover

**Course:** CPSC-69100 | **Week:** 7 | **Sprint:** Sprint 3 (Week 2 of 2)

---

### 1. Team Activities This Week

| Activity | Owner | Hours | Status |
|----------|-------|-------|--------|
| AWS CloudFormation deployment (VPC+EC2+ALB+S3) | Suhas | 6 | ✅ |
| Production Docker Compose final config | Rosie | 3 | ✅ |
| Final security scan (Bandit + manual review) | Rosie | 4 | ✅ |
| User Manual (clinical staff) | Venkata | 4 | ✅ |
| Admin Guide (IT operations) | Venkata | 3 | ✅ |
| Quick Reference Card (1-page) | Venkata | 2 | ✅ |
| Full API documentation (Postman + cURL) | Suhas | 3 | ✅ |
| Weekly progress reports (Weeks 1-7) | Suhas | 4 | ✅ |
| Master README (research, architecture, next steps) | All | 4 | ✅ |
| Final academic report compilation | All | 6 | ✅ |

**Total Hours This Week:** 39

---

### 2. Project Completion Summary

#### All Requirements Met

| REQ | Description | Status | Evidence |
|-----|-------------|--------|---------|
| REQ-01 | Patient Consent Toggle | ✅ | TEST-01 PASS; code-level gate |
| REQ-02 | Whisper ASR WER < 8% | ✅ | WER ~6% on clean medical audio |
| REQ-03 | NegEx ≥95% accuracy | ✅ | Ensemble v4 F1=0.957, Recall=96.3% |
| REQ-04 | Human verification UI | ✅ | TEST-03 PASS; only approved entities queried |
| REQ-05 | ClinicalTrials.gov sync | ✅ | TEST-04 PASS; < 5min for 50 trials |
| REQ-06 | Missing Variables checklist | ✅ | Shown per trial in inbox |
| REQ-07 | Async inbox < 60s | ✅ | TEST-05 PASS; ~2s average |
| REQ-08 | RAM-only, AES-256 | ✅ | TEST-06 PASS; Bandit scan clean |
| REQ-09 | WCAG 2.1 AA | ✅ | TEST-07 PASS; all aria attributes |
| REQ-10 | RBAC 401/403 | ✅ | TEST-08 PASS; 8 scenarios verified |
| REQ-11 | Consent audit logs | ✅ | Append-only SQLite audit_log |

**All 11 requirements: MET ✅**

---

### 3. Final System Statistics

| Metric | Value |
|--------|-------|
| Total source files | 128 files |
| Backend Python files | 55 (.py) |
| Frontend TypeScript/React files | 33 (.tsx/.ts) |
| Test files | 9 test files |
| Documentation files | 12 (.md) |
| Backend test coverage | ~78% |
| NLP negation recall | 96.3% |
| Enrollment readiness accuracy | Validated on 20 real ClinicalTrials.gov trials |
| Docker build time (cold) | ~8 minutes |
| Docker build time (cached) | ~45 seconds |
| Frontend bundle size | 87.1 kB shared JS |
| API endpoints | 13 endpoints |

---

### 4. AWS Deployment Architecture

```
Internet
    │
  Route 53 (DNS)
    │
  ALB (HTTPS, port 443 — TLS 1.3)
    │
  EC2 t2.micro (AWS Free Tier)
    ├── Docker: Next.js frontend (port 3000)
    ├── Docker: FastAPI backend (port 8000)
    └── Docker: Qdrant vector DB (port 6333)
    │
  ├── S3 Bucket (AES-256, 7-year retention) — audit logs
  ├── SSM Parameter Store — JWT + app secrets
  └── CloudWatch — application + audit log groups
```

**Cost:** $0 (AWS Free Tier; S3 and CloudWatch within free tier limits for academic use)

---

### 5. Deliverables Completed

**Code & Infrastructure:**
- [ x ] Complete backend (FastAPI, Python 3.11) — 55 Python files
- [ x ] Complete frontend (Next.js 14, TypeScript) — 33 React/TS files
- [ x ] Docker Compose: dev, test, production profiles
- [ x ] AWS CloudFormation IaC template
- [ x ] `seed_trials.py` — live ClinicalTrials.gov data seeder
- [ x ] Bandit security configuration

**Testing:**
- [ x ] 9 test files, 60+ individual test cases
- [ x ] All 8 project TEST IDs passing
- [ x ] 100-transcript NLP training dataset
- [ x ] NLP variant benchmark (4 algorithms compared)
- [ x ] Performance benchmarks documented

**Documentation:**
- [ x ] Master README (architecture, setup, research, next steps)
- [ x ] User Manual (clinical staff workflow guide)
- [ x ] Admin Guide (IT setup + troubleshooting)
- [ x ] Quick Reference Card (1-page)
- [ x ] API documentation (Postman collection + cURL examples)
- [ x ] Weekly Progress Reports (Weeks 1-7)
- [ x ] AGENTS.md (Kiro project steering)

---

### 6. Comparison to Existing Systems

| System | Type | Trial Matching | Ambient Audio | HITL | Our Advantage |
|--------|------|---------------|---------------|------|--------------|
| Nuance DAX | Commercial | ❌ | ✅ | ❌ | We add trial routing |
| Abridge | Commercial | ❌ | ✅ | ❌ | We add trial routing |
| TrialMatchAI | Research | ✅ | ❌ | ❌ | We add ambient capture + 7 new features |
| PRISM | Research | ✅ | ❌ | ❌ | We add ambient + criterion breakdown |
| TrialGPT | Research | ✅ | ❌ | ❌ | We add ambient + enrollment score |
| **OmniMatch** | **Academic** | ✅ | ✅ | ✅ | **All features + 7 new capabilities** |

---

### 7. Lessons Learned

| Lesson | Impact | Future Recommendation |
|--------|--------|----------------------|
| Docker context matters on Windows | Build failed until `desktop-linux` context set | Document context setup in README |
| `next.config.ts` not supported by Next.js 14.2 | Build failed | Upgrade to Next.js 14.3+ for TS config support |
| Duplicate export in React pages from incremental edits | Build failed | Always search for duplicate exports before committing |
| Whisper base model ~5GB first download | Slow first startup | Pre-pull model in CI/CD pipeline |
| APScheduler in single-worker mode only | N/A for Free Tier | Use Celery + Redis for multi-worker production |

---

### 8. Recommended Next Steps

**Short-term (post-submission):**
1. Fine-tune Whisper on medical vocabulary → WER < 5%
2. Replace `all-MiniLM-L6-v2` with `Bio_ClinicalBERT` → +5% match precision
3. Add SNOMED CT entity normalization → better cross-visit matching

**Medium-term (production path):**
4. Sign AWS BAA for real PHI workloads
5. FHIR R4 integration for EHR data pre-population
6. Multi-tenant support (multiple clinics)

**Long-term (research):**
7. Prospective clinical trial for WER and negation accuracy validation
8. IRB approval for real patient data collection

---

### 9. Project Hours Summary

| Team Member | Planned | Actual | Deliverables |
|-------------|---------|--------|-------------|
| Suhas Reddy Kotla | 135 hrs | 138 hrs | AI/NLP/AWS/Match engine |
| Rosie Roy Barla | 130 hrs | 132 hrs | Backend/Security/Qdrant |
| Venkata Akula | 130 hrs | 127 hrs | Frontend/UI/Accessibility |
| **Total** | **395 hrs** | **397 hrs** | |

---

### 10. Project Value Assessment

| Component | Market Rate | Student Cost |
|-----------|-------------|-------------|
| Team Lead / AI Lead (138 hrs × $65/hr) | $8,970 | $0 |
| Backend & Security (132 hrs × $60/hr) | $7,920 | $0 |
| Frontend UI Lead (127 hrs × $55/hr) | $6,985 | $0 |
| AWS infrastructure | $100 | $0 |
| Open-source software (Whisper, Qdrant, Next.js) | $0 | $0 |
| **Total Commercial Value** | **$23,975** | **$0** |

---

### Final Statement

OmniMatch has been successfully designed, implemented, tested, and deployed as a fully functioning prototype that meets all 11 specified requirements. The system introduces 7 novel capabilities not found in any existing clinical trial matching system reviewed in the literature as of Fall 2026.

The prototype is available at: `http://localhost:3000` (local) and deployable to AWS via the included CloudFormation template.

---

*Prepared by: Suhas Reddy Kotla (Team Leader)*
*Reviewed by: Rosie Roy Barla, Venkata Papaiah Thrinadha Nagamahesh Akula*
*Submitted to: Dr. Khaled Alzoubi, CPSC-69100, Fall 2026*
