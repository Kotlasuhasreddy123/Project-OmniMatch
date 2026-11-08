# Install OmniMatch on your own computer

No AWS account or paid API key is needed for the local synthetic-data demo. The app runs in Docker on your computer. You need Git, Docker with Compose v2, and Python 3.10+ for the setup helper. The backend's Python dependencies are installed inside its Python 3.11 container; they do not need to be installed into your personal Python environment.

## Requirements

- Windows: Docker Desktop using Linux containers/WSL 2. macOS: Docker Desktop. Linux: Docker Engine and Compose v2 with permission to run Docker.
- Start with 16 GB system RAM and allocate at least 8 GB to Docker. CPU inference is supported; no GPU is required. Allow roughly 15–25 GB free disk for images, packages and model caches. These are planning estimates; measure actual use on your computer.
- Internet access for the first build and model downloads. Whisper and MiniLM weights are cached in the backend data volume. Optional registry sync/external research links still need internet. First installation can take several minutes or longer on a slow connection.
- Free local ports 3000, 8000, 6333 and 6334. If another OmniMatch copy is running, stop that copy first; do not delete its volumes.

## Windows PowerShell

Start Docker Desktop and wait until its engine is ready. Then run:

```powershell
git clone https://github.com/Kotlasuhasreddy123/Project-OmniMatch.git
cd Project-OmniMatch
py -3 scripts/setup_local.py --start
docker compose ps
py -3 scripts/setup_local.py --verify
```

If `py` is unavailable but Python is installed, use `python` instead. If neither exists, install Python 3 and reopen PowerShell. The setup script creates backend/.env with two random secrets if the file is absent. It preserves an existing file and stops if placeholder secrets remain.

## macOS or Linux terminal

```bash
git clone https://github.com/Kotlasuhasreddy123/Project-OmniMatch.git
cd Project-OmniMatch
python3 scripts/setup_local.py --start
docker compose ps
python3 scripts/setup_local.py --verify
```

On Linux, fix Docker group/socket permissions using Docker's installation instructions if `docker info` cannot connect. On Apple Silicon, the images/dependencies must be tested on that architecture; no ARM machine was available for this release, so ARM compatibility is not claimed as verified.

## Open and use it

Open http://localhost:3000. The backend is at http://localhost:8000/api/docs. See http://localhost:3000/preview for illustrative display data. Model warm-up can take longer than container startup; `--verify` requires Qdrant connectivity, the frontend, a loaded Whisper model and configured WorkOS IDs. It does not verify actual email delivery. If it fails during downloads, inspect logs and retry once warm-up completes. For optional transformers, use `python scripts/setup_local.py --start --advanced` after reading [the local release checklist](LOCAL_RELEASE_CHECKLIST.md).

Shared demonstration passwords have been removed. Configure owner-approved email access using [the passwordless setup guide](PASSWORDLESS_ACCESS.md) before opening a session. Blank WorkOS IDs keep protected functions disabled. You can view `/preview` without an account. Registration and email delivery require the external provider configuration; downloading the source does not automatically create an account.

Start a session, grant consent and read a fictional example: “The patient has asthma and uses albuterol. The patient denies COPD.” Review the transcript, approve the patient's confirmed terms, and complete the visit. Open the inbox and inspect study suggestions and missing information. Results depend on the indexed sample catalog; the repo contains three invented studies, not all clinical trials. Try repeated and negated conditions to check the context behavior. Human approval is required before matching.

## Models and data

Both learned models already have trained weights. See [models and original training sources](MODELS_AND_DATA.md). Installing/downloading a model or indexing a study does not retrain it. Raw audio is processed in memory; approved demo information and inbox/audit records are stored locally. Never enter real patient identifiers or recordings in this academic installation.

Run the offline text-context regression checks without starting Docker:

```powershell
py -3 backend/evaluate_context.py --output docs/my-context-check.json
```

Use `python3` instead of `py -3` on macOS/Linux. The report checks synthetic text context, not speech accuracy or clinical validity.

## Stop, restart and update

```bash
docker compose stop
docker compose start
```

Before an update, back up your demo data and record the old Git commit. Then:

```bash
git pull --ff-only
docker compose --env-file backend/.env up -d --build
```

Do not use `docker compose down -v` unless you intentionally want to remove the database, indexed studies and model cache. Named volumes preserve data across normal stops and rebuilds.

## Troubleshooting

- Docker not ready: start Docker Desktop/Engine and confirm `docker info` works.
- Port already allocated: run `docker compose ps` in your other checkout and stop its containers first.
- Recording blocked: enable consent, allow browser microphone permission, and open the localhost URL.
- Model download/warm-up failure: check internet access, available memory/disk and `docker compose logs --tail=100 backend`. Fix the cause and restart the backend.
- No study suggestions: confirm terms were approved and check the limited catalog. A missing result does not rule out real research opportunities.
- Slow transcription: use shorter recordings and close memory-intensive apps. Increasing Whisper model size requires more memory and time and must be tested separately.
- Old study index: check whether the same named volumes were created by an older installation; back up before any deliberate reindexing. Do not delete data as a troubleshooting shortcut.

Public AWS deployment has a [separate guide](AWS_DEPLOYMENT.md). No AWS deployment is required to install this version locally.
