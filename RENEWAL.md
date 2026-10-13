# OmniMatch renewal notes

This is the preserved-and-renewed working copy of the Kiro project. The source
folders outside `Chatgpt/` were not modified.

## Current decision

The project is a synthetic-data Master's prototype, not a clinically deployable
system or a proven startup. See `docs/Professor_Startup_Proposal.md` and its Word
version for the competitor analysis, evaluation design, and startup go/no-go gates.
Do not claim global feature novelty, HIPAA compliance, or clinical eligibility.

## Added capabilities

- **Evidence Ledger:** records clinician-approved evidence anchors as hashes and
  offsets only. It connects a MET criterion to a verified entity without
  persisting audio, full transcript text, or the quoted span.
- **Trial Freshness Gate:** labels a match `READY`, `REVIEW`, or `BLOCKED` from
  registry activity, record recency, and available site data. It is an outreach
  safeguard, not a clinical eligibility decision.
- **Server consent gate:** audio transcription now requires the authenticated
  user's latest consent event for that session to be `CONSENT_GRANTED`.
- **Memory-only upload path:** audio is sent as a raw body and streamed into a
  bounded memory buffer; this avoids `UploadFile` disk spooling. FFmpeg receives
  encoded audio via stdin and returns decoded samples via stdout.

## Verification

From `backend`, run:

```powershell
pytest -q tests/test_renewal_features.py
pytest -q tests/test_new_features.py
pytest -q tests/test_consent.py
```

From `frontend`, run after dependency installation:

```powershell
pnpm exec tsc --noEmit
pnpm test:run
```

See `docs/OmniMatch Renewal Handoff and Next Steps.docx` for the complete
research comparison, the runbook, production boundaries, and next sprint plan.

**Verification status on 10 October 2026:** Python compilation succeeded.
The backend tests could not run in this sandbox because `pytest-asyncio` is
missing and PyPI is unreachable. The Word proposal was generated but visual
rendering was unavailable because LibreOffice is not installed. Full tests,
browser validation, and document visual QA remain required before submission.
