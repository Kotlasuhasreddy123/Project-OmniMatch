# OmniMatch: professor review and startup validation proposal

**CPSC-69100 Master's Project | HealthTech Innovation Labs | 10 October 2026**  
**Advisor:** Dr. Khaled Alzoubi  
**Status:** research prototype, synthetic data only; not a medical device or clinical decision system.

## Executive decision

OmniMatch could become a startup, but the present evidence does **not** establish a unique invention or product-market fit. The strongest testable opportunity is a low-friction trial *pre-screening worklist* for smaller clinical sites: a visit produces clinician-approved facts; after the visit, staff see candidate trials with source evidence, missing items, and a freshness check. The output is a reason to investigate, never an eligibility determination or a patient referral without human verification.

We recommend submitting the current research prototype to the professor, running a controlled synthetic-data evaluation, interviewing prospective users, and only then deciding whether to start a company. We should not claim that two features are globally novel; no practical search can prove that, and major vendors already offer overlapping workflows.

## What exists already, in plain terms

| System | What it already does | OmniMatch's proposed focus |
|---|---|---|
| Tempus TIME | Matches patients to trials, tracks patients over time, uses human review and site workflows. | A smaller, visit-to-inbox workflow whose deployment and review effort can be measured at a community site. |
| AWS trial-screening reference | Shows AI agents, criterion evidence, human review, and screening uncertainty. | A working academic prototype and explicit usability/safety evaluation, not a claim of technical first. |
| AWS HealthScribe / Abridge | Ambient clinical documentation and evidence-oriented review. | Trial-routing worklist rather than general visit notes, coding, or billing. |
| ClinicalTrials.gov API | Public structured trial records. | Candidate retrieval plus a visible check of record recency and site information. |

The real distinction must be proven by *implementation cost, staff time saved, error rates, and usefulness*, not by a feature checklist. A site with an existing EHR trial module may have no reason to buy this.

## Product hypothesis and customer

**Initial user:** trial coordinator or research nurse at a small/community oncology or specialty clinic. **Buyer hypothesis:** research director or site operations lead. **Job:** discover potentially relevant recruiting trials without interrupting a consultation, then know exactly what to verify before outreach. The exact specialty and buyer remain hypotheses; customer interviews must decide them.

**Workflow:** consent → capture a synthetic visit → transcribe → clinician approves/rejects each extracted fact → post-visit match → inbox with criterion breakdown, evidence anchor, missing variables, registry freshness, and site information → coordinator verifies against the source protocol and records disposition.

**Differentiation to test:** (1) an approval-gated ambient visit to asynchronous worklist, (2) a compact evidence-and-uncertainty view that makes a candidate actionable for a resource-constrained coordinator. These are *product design hypotheses*, not claims that no other product has them.

## Current prototype and safety boundary

The renewed copy is in `Chatgpt/omnimatch-renewed`; the original Kiro data and folders are untouched. It includes a FastAPI backend, Next.js frontend, trial retrieval, entity review, inbox, evidence ledger, and a trial freshness gate. This iteration additionally makes audio acceptance depend on the latest consent event for the authenticated user and session. It changes audio upload to a raw streamed request body to avoid multipart temporary-file spooling. WebM/WAV decoding is designed to use FFmpeg pipes, not audio files.

These are prototype controls only. SQLite is not AES-256 encrypted at rest; JWT storage in browser sessionStorage is not production-grade; deployment, retention, consent revocation during capture, data provenance, model error handling, and legal/regulatory review need further work. **Do not use real patient data or deploy clinically.**

## Professor evaluation plan

1. Run 20–30 synthetic cases across at least three conditions, including negation, family history, contradictory facts, absent laboratory values, and stale trial records. Freeze the trial snapshot and label each expected criterion result manually.
2. Compare a baseline keyword/manual workflow with OmniMatch on: time to produce a verified shortlist; false-positive candidates; missed plausible candidates; missing-critical-variable detection; and clinician correction burden. Report raw counts and confidence intervals, not only an aggregate score.
3. Conduct a five-person usability walkthrough with research staff or suitably qualified proxies. Ask whether each candidate is actionable, what evidence is missing, and whether the inbox would interrupt their workflow.
4. Measure consent and privacy invariants separately: no server transcription without a current grant; no audio file writes; approved entities only in match payload; role-based inbox access; no outbound PHI. Treat any failure as a stop condition.
5. Keep a limitations log: retrospective/synthetic cases cannot establish clinical safety, recruitment improvement, or commercial demand.

**Proposed academic acceptance criteria:** all consent/RBAC/privacy tests pass; no critical false statement of eligibility; at least 90% of missing critical variables flagged in the labeled set; median coordinator review time lower than the baseline in the same synthetic tasks. These are proposed targets, not achieved results.

## Startup go/no-go gates after professor feedback

**Discovery (4–6 weeks):** interview 12–15 coordinators and research leads from different sites. Ask about current workflow, bottlenecks, data access, EHR constraints, procurement, security requirements, and the cost of a missed/poor-quality candidate. Seek at least three sites willing to review a synthetic demo and one willing to discuss a supervised pilot. Do not ask leading “would you use AI?” questions.

**Pilot design:** select one specialty and one site type. Obtain institutional approvals, data-use agreements, security review, and clinician oversight before touching any real data. Define a prospective, non-interventional pilot with human confirmation before outreach. Consult counsel about HIPAA, state privacy law, clinical decision support / FDA status, and research governance. Pricing, reimbursement, and the buying process remain unvalidated hypotheses.

**Go only if:** users repeatedly identify an expensive workflow gap; the prototype improves verified work rather than generating more review; a pilot sponsor exists; and compliance costs are feasible. **No-go or pivot if:** existing EHR/Tempus workflows already solve the problem at target sites, staff do not trust/act on the evidence, or integration cost overwhelms value.

## Immediate next steps

1. Ask the professor to review the problem definition, safety boundary, evaluation design, and whether the specialty/site focus is appropriate.
2. Complete dependency installation in a network-enabled development environment and run the full backend/frontend suites. The present environment lacks `pytest-asyncio` and cannot reach PyPI; passing tests must not be claimed yet.
3. Fix any test failures, add a deterministic synthetic benchmark and documented results, then rehearse a 10-minute demo with no real PHI.
4. Run user discovery. Decide startup/pivot/no-go from measured evidence and professor feedback, not a novelty claim.

## References checked for this proposal

- Tempus, TIME portal and enrollment: https://www.tempus.com/publications/the-tempus-time-trial-portal-and-clinical-trial-enrollment/
- Tempus, Exigent/TIME collaboration: https://www.tempus.com/publications/optimizing-clinical-trial-subject-selection-insights-from-exigent-research-network-and-the-tempus-ai-time-program-collaboration/
- Tempus, TIME technical spotlight: https://www.tempus.com/wp-content/uploads/2021/10/TIME-Tech-Spotlight-12.pdf
- AWS, AI agents for clinical trial screening: https://aws.amazon.com/blogs/architecture/ai-agents-for-clinical-trial-screening/
- AWS, patient pre-screening with generative AI: https://aws.amazon.com/blogs/industries/improving-patient-pre-screening-for-clinical-trials-with-generative-ai-on-aws/
- AWS, HealthScribe service card: https://docs.aws.amazon.com/pdfs/ai/responsible-ai/aws-healthscribe/aws-healthscribe.pdf
- Abridge product: https://www.abridge.com/product
- National Library of Medicine, ClinicalTrials.gov API v2: https://www.nlm.nih.gov/pubs/techbull/ma24/ma24_clinicaltrials_api.html
