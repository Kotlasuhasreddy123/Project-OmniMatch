# OmniMatch — synthetic-data classroom prototype

**Install locally:** [Windows, macOS and Linux instructions](docs/INSTALL_ON_YOUR_COMPUTER.md). No AWS account or paid API key is needed. [Which models are already trained, and on what data?](docs/MODELS_AND_DATA.md)

The active learned models are pretrained Whisper (speech) and `all-MiniLM-L6-v2` (retrieval). Clinical extraction and eligibility checks use rules. A separate TF-IDF/logistic assertion candidate has now been trained on synthetic annotations; it scored 54/60 (90%) on a small internal test and is not connected to the live app. See [all models, training and measured results](docs/MODEL_TRAINING_RESULTS.md). Run `python backend/evaluate_context.py` for the reproducible synthetic context regression checks; see the model guide for the metric and its limits.

## Approved access and public portal

The public portal contains policies, license notices, a specialty/language coverage register, and installation links. WorkOS email access stays disabled until the owner adds application IDs and configures the waitlist and organization roles. Follow [passwordless setup](docs/PASSWORDLESS_ACCESS.md). The public MIT repository remains downloadable regardless of account approval.

See [the evaluation and training plan](docs/VALIDATION_AND_TRAINING_PLAN.md) for the unmet broad extraction benchmark. No universal validation or 98–100% clinical accuracy is claimed.

## Latest model work

The active English vocabulary and context rules improved the legacy 100-transcript development negation recall from 29.7% to 70.3% (F1 77.6%). The broader target remains unmet. The focused 72/72 checks are a separate regression metric. A new `/models` page presents the inventory and evidence; no 98% clinical accuracy is claimed.

## Visual results upgrade

The inbox now includes visit totals, review workload, a criterion-coverage chart and an interactive Recharts study comparison. Values are computed from inbox records, with a numerical list alongside the chart. The renewed local app also connects its overview to search filters. The interface uses system typography, soft teal accents and translucent navigation. Charts render locally; no remote chart service receives visit data. Open `/preview` to explore clearly labeled fictional display examples without signing in.

Use Node.js 20 and `npm ci` inside `frontend/` for development and CI. `package-lock.json` is the canonical dependency lockfile used by Docker. The older pnpm lockfile is retained as historical project material and is not used by the deployment workflow. The frontend has been upgraded to Next.js 15.5.29 and PostCSS 8.5.32 to address dependency advisories; React remains on 18.3.1.

Deployment instructions: [AWS guide](docs/AWS_DEPLOYMENT.md). Model scope and evaluation: [data plan](docs/MODEL_DATA_PLAN.md). Whisper and MiniLM remain unchanged; the separate assertion candidate is experimental.

OmniMatch demonstrates a consent-gated visit, local speech transcription, clinician review of extracted terms, and asynchronous trial suggestions. It is a **research prototype**, not a medical device, clinical decision support product, HIPAA-compliant deployment, or a system for real patient data. Use invented names and details only.

The local demo contains three **fictional** trial records with `DEMO-` identifiers. The trial freshness gate blocks sponsor referral for them. A displayed enrollment-readiness percentage is a heuristic ranking score, **not model accuracy, eligibility, or a probability of enrollment**.

## Start the live demo on Windows

1. Install and start Docker Desktop. Allow enough time and disk space for the first model download and image build.
2. From this folder in PowerShell, run `powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\START_DEMO.ps1`. Later starts can use `-SkipBuild`.
3. Open [the local app](http://localhost:3000). Configure [owner-approved email access](docs/PASSWORDLESS_ACCESS.md) before using protected visits. Shared passwords have been removed. The `/preview` page is available without an account.
4. For authenticated command-line checks, set a current approved WorkOS access token in the shell's `OMNIMATCH_ACCESS_TOKEN` environment variable. Never save it in source or share it. Then run `powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\RUN_SMOKE_TEST.ps1` and `powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\RUN_AUDIO_SMOKE_TEST.ps1`.
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
