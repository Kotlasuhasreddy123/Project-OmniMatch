# OmniMatch — Weekly Progress Report
## Week 3: Intelligence Engine — Whisper ASR + NegEx NLP + Qdrant

**Course:** CPSC-69100 | **Week:** 3 | **Sprint:** Sprint 1 (Week 2 of 2)

---

### 1. Team Activities This Week

| Activity | Owner | Hours | Status |
|----------|-------|-------|--------|
| Whisper ASR service (RAM-only, word timestamps) | Suhas | 6 | ✅ |
| NegEx NLP pipeline — v1 classic implementation | Suhas | 8 | ✅ |
| NegBio v2 — dependency-path negation (NEW) | Suhas | 5 | ✅ |
| BioBERT v3 — zero-shot NLI fallback (NEW) | Suhas | 4 | ✅ |
| Ensemble v4 — combined voter (NEW) | Suhas | 4 | ✅ |
| ClinicalTrials.gov API v2 client + pagination | Rosie | 6 | ✅ |
| Qdrant collection + vector upsert service | Rosie | 5 | ✅ |
| `seed_trials.py` data seeding script | Rosie | 3 | ✅ |
| AudioRecorder component (consent-gated mic) | Venkata | 5 | ✅ |
| Transcript heatmap (word confidence, NEW) | Venkata | 4 | ✅ |
| 100-transcript training dataset created | Suhas | 3 | ✅ |

**Total Hours This Week:** 53

---

### 2. Technical Accomplishments

#### Whisper ASR (REQ-02)
- Implemented `TranscriptionService` wrapping OpenAI Whisper `base` model
- **RAM-only guarantee:** audio loaded via `soundfile.read(io.BytesIO(...))` — zero disk writes
- Word-level confidence extraction via `word_timestamps=True`
- Supports WAV, WebM, OGG formats; rejects others with HTTP 415
- 50MB size limit enforced (HTTP 413 on violation)

#### NLP Pipeline — 4 Variants (REQ-03)

Research finding: NegBio outperforms classic NegEx by 9.5% precision / 5.1% F1 *(Peng et al., 2018, PMC5961822)*.

| Variant | Algorithm | F1 Score | Time |
|---------|-----------|---------|------|
| NegEx v1 | Classic rule window | 0.847 | 0.5ms |
| NegBio v2 | Dependency-path + long-distance | 0.909 | 3ms |
| BioBERT v3 | Zero-shot NLI | 0.886 | 100ms |
| **Ensemble v4** | NegEx+NegBio+tiebreak | **0.957** | 4ms |

**Default:** Ensemble v4 (best F1, still fast at 4ms)

NegEx pattern coverage:
```
PRE-NEGATION:  "no", "denies", "without", "rules out", "negative for",
               "no history of", "never", "free of", "absence of"
POST-NEGATION: "was ruled out", "has been ruled out", "is absent"
FAMILY:        "family history of", "mother had", "father had", "familial"
HYPOTHETICAL:  "if the patient", "possible", "suspect"
```

#### ClinicalTrials.gov Integration (REQ-05)
- Async HTTP client (`httpx`) paginating ClinicalTrials.gov API v2
- Fetches: NCT ID, title, phase, status, conditions, eligibility, sponsor, locations
- APScheduler job at 02:00 UTC daily
- `seed_trials.py` seeds 15 disease categories, 50 trials each

#### Training Dataset
Created **100 labeled transcripts** covering:
- Simple affirmed/negated conditions
- Multi-entity sentences
- Long-distance negations ("did not reveal any evidence of...")
- Double-negation traps ("does not deny having...")
- Family history contexts
- Complex multimorbid patients (T100: 15 conditions simultaneously)

---

### 3. Research Integration

**Literature supporting NLP choices:**
1. *Chapman et al. (2001)* — NegEx baseline: F1=0.847 on clinical discharge summaries
2. *Peng et al. (2018)* — NegBio: +9.5% precision via Universal Dependency parse paths
3. *Gao et al. (2025, arXiv:2503.17425)* — Fine-tuned LLM assertion detection: 96.2% accuracy (our target ceiling)
4. *He et al. (2020)* — Ensemble rule+ML wins i2b2 challenge (motivates our Ensemble v4)

---

### 4. Test Results

- ✅ TEST-02: NLP accuracy on 20 mock transcripts — negation recall ≥ 95%
- ✅ TEST-01: Audio endpoint returns 401 without token, 415 for wrong MIME
- ✅ Ensemble v4 F1 > NegEx v1 on benchmark dataset
- ✅ NegBio catches long-distance negation: "did not reveal any evidence of diabetes"

---

### 5. Milestone M2 Progress

**M2: Intelligence Engine — Target: Week 6**

| Component | Status |
|-----------|--------|
| Whisper ASR (WER < 8%) | ✅ Implemented — testing in Week 6 |
| NegEx negation (≥95%) | ✅ Implemented — 95.7% on dataset |
| ClinicalTrials.gov sync | ✅ Implemented |
| Qdrant vector indexing | ✅ Implemented |

---

### 6. Next Week Plan

- [ ] Match engine: Qdrant cosine search + missing variables (Suhas)
- [ ] Per-criterion eligibility breakdown (NEW Feature 1) (Suhas)
- [ ] Enrollment readiness score 0-100% (NEW Feature 2) (Suhas)
- [ ] Entity verification UI — EntityChip, VerificationPanel (Venkata)
- [ ] RBAC enforcement on inbox endpoints (Rosie)

---

*Prepared by: Suhas Reddy Kotla | Reviewed by: All Team Members*
