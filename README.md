# OmniMatch — synthetic-data classroom prototype

OmniMatch demonstrates a consent-gated visit, local speech transcription, clinician review of extracted terms, and asynchronous trial suggestions. It is a **research prototype**, not a medical device, clinical decision support product, HIPAA-compliant deployment, or a system for real patient data. Use invented names and details only.

The local demo contains three **fictional** trial records with `DEMO-` identifiers. The trial freshness gate blocks sponsor referral for them. A displayed enrollment-readiness percentage is a heuristic ranking score, **not model accuracy, eligibility, or a probability of enrollment**.

## Start the live demo on Windows

1. Install and start Docker Desktop. Allow enough time and disk space for the first model download and image build.
2. From this folder in PowerShell, run `powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\START_DEMO.ps1`. Later starts can use `-SkipBuild`.
3. Open [the local app](http://localhost:3000) in Chrome or Edge. Sign in with the **local demonstration account** `clinical_staff` / `Staff@12345`. Never reuse that password for anything else.
4. Before the presentation, run `powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\RUN_SMOKE_TEST.ps1` and `powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\RUN_AUDIO_SMOKE_TEST.ps1`.
5. Allow microphone permission in the browser when prompted. The microphone control remains disabled until consent is granted.

See [the demo guide](docs/team-share/OmniMatch%20October%2020%20Live%20Demo%20Guide.docx) for the speaking script, UI sequence, and backup plan. See [the Week 8 evidence report](docs/weekly-reports/OmniMatch%20Week%208%20Implementation%20Milestone%20Evidence.docx) for measured results and limitations.

## What is actually verified

- In Docker, the backend health endpoint reports Qdrant connected and the Whisper base model loaded.
- A synthetic end-to-end text workflow produced an inbox item within 60 seconds in one local run.
- A synthetic speech sample was transcribed in memory by Whisper in one local run.
- Browser review requires explicit approval of patient entities before submission. Negated and family-history mentions are excluded from the matching payload.
- Automated frontend tests pass. The full backend suite includes an **unmet 95% NLP benchmark**; do not report the suite or the model as 100% passing.

Performance on a small, synthetic benchmark is not evidence of clinical safety or generalization. The code also lacks production-grade encryption-at-rest, TLS deployment, secret management, and real-patient validation. Do not connect a real clinic or submit real patient information.

## Development and tests

The backend is FastAPI and Python; the frontend is Next.js and TypeScript; Qdrant holds the local demo index. `docker-compose.yml` starts all three services. Backend tests run with `docker compose -p omnimatch-test -f docker-compose.test.yml run --rm --no-deps backend-test`. Frontend tests run from `frontend` with `npm run test:run -- --runInBand` after installing dependencies. The production frontend build is `npm run build`.

The prior Kiro-era README is retained at [docs/README_Historical.md](docs/README_Historical.md) for provenance. Its performance figures and broad claims are **not validated results**.
