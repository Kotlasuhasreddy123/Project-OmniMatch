# Install OmniMatch on your own computer

No AWS account or paid API key is needed for the local synthetic-data demo. The app runs in Docker on your computer. You need Git, Docker with Compose v2, and Python 3.10+ for the setup helper. The backend's Python dependencies are installed inside its Python 3.11 container; they do not need to be installed into your personal Python environment.

## Requirements

- Windows: Docker Desktop using Linux containers/WSL 2. macOS: Docker Desktop. Linux: Docker Engine and Compose v2 with permission to run Docker.
- Start with 16 GB system RAM and leave room for other applications. This laptop completed its rehearsal with a 4 GB WSL memory limit, four CPUs and 8 GB swap after the default limit caused memory pressure; see [the measured local setup](LOCAL_REHEARSAL_RESULTS.md). Larger workloads may need more resources. CPU inference is supported; no GPU is required. Allow at least 20–25 GB free disk for a build. These are planning estimates, not a capacity guarantee.
- Internet access for the first build and model downloads. Whisper and MiniLM weights are cached in the backend data volume. Optional registry sync/external research links still need internet. First installation can take several minutes or longer on a slow connection.
- Free local ports 3000, 8000, 6333 and 6334. If another OmniMatch copy is running, stop that copy first; do not delete its volumes.

## Windows PowerShell

Start Docker Desktop and wait until its engine is ready. Then run:

```powershell
git clone https://github.com/Kotlasuhasreddy123/Project-OmniMatch.git
cd Project-OmniMatch
py -3 scripts/setup_local.py
```

If `py` is unavailable but Python is installed, use `python` instead. If neither exists, install Python 3 and reopen PowerShell. The setup script creates backend/.env with two random secrets if the file is absent. It preserves an existing file and stops if placeholder secrets remain.

## macOS or Linux terminal

```bash
git clone https://github.com/Kotlasuhasreddy123/Project-OmniMatch.git
cd Project-OmniMatch
python3 scripts/setup_local.py
```

On Linux, fix Docker group/socket permissions using Docker's installation instructions if `docker info` cannot connect. On Apple Silicon, the images/dependencies must be tested on that architecture; no ARM machine was available for this release, so ARM compatibility is not claimed as verified.

These commands prepare configuration. They do not build or start the application yet.

## Configure your sign-in provider

Before building, follow [approved email access](PASSWORDLESS_ACCESS.md). For an independent installation, create your own WorkOS application and organization, enable email codes, and configure the waitlist and permissions. No WorkOS API secret is required by this integration. Review the provider's current terms and free-tier limits.

Open `backend/.env` in a text editor. Preserve the generated local secrets and replace these public-ID placeholders:

```dotenv
WORKOS_CLIENT_ID=client_your_application_id
WORKOS_ORGANIZATION_ID=org_your_organization_id
WORKOS_ISSUER=
```

For standard native sessions, leave the issuer blank to derive it from your client ID. A custom authentication domain needs the exact native session issuer, not the hosted login-page URL.

In WorkOS, allow origin `http://localhost:3000` and exact login/logout destination `http://localhost:3000/login/`. Add your email as an organization member with an owner role containing `omnimatch:access` and `omnimatch:admin`. Approved staff need only `omnimatch:access`. Follow the access guide for waitlist approval; signing up alone does not grant these permissions.

The setup helper passes the IDs to both the backend and frontend Docker build. You do not need `frontend/.env.local` for this Docker path. Never commit environment files. For frontend development outside Docker, follow the separate environment instructions in the access guide.

## Build and start

Windows PowerShell:

```powershell
py -3 scripts/setup_local.py --start
docker compose ps
py -3 scripts/setup_local.py --verify
```

macOS/Linux:

```bash
python3 scripts/setup_local.py --start
docker compose ps
python3 scripts/setup_local.py --verify
```

Use the same repository folder for each command. Initial builds and downloads can take several minutes or longer. Wait for the services to become healthy. Verification checks services and configuration; complete email sign-in separately to verify your account.

## Open and use it

Open http://localhost:3000. The backend is at http://localhost:8000/api/docs. See http://localhost:3000/preview for illustrative display data. Model warm-up can take longer than container startup; `--verify` requires Qdrant connectivity, the frontend, a loaded Whisper model and configured WorkOS IDs. It does not verify actual email delivery. If it fails during downloads, inspect logs and retry once warm-up completes. For optional transformers, use `python scripts/setup_local.py --start --advanced` after reading [the local release checklist](LOCAL_RELEASE_CHECKLIST.md).

Open **Access**, review the policies, and choose **Approved? Sign in with email code**. Use your approved organization email and enter the code directly in the provider page. Shared passwords have been removed. Blank WorkOS IDs keep protected functions disabled. You can view `/preview` without an account. Downloading the source does not automatically create an account.

Start a session, grant consent and read a fictional example: “The patient has asthma and uses albuterol. The patient denies COPD.” Review the transcript, approve the patient's confirmed terms, and complete the visit. Open the inbox and inspect study suggestions and missing information. Results depend on the indexed sample catalog; the repo contains three invented studies, not all clinical trials. Try repeated and negated conditions to check the context behavior. Human approval is required before matching.

## Models and data

The core speech and embedding models already have pretrained weights. Optional transformer features add the checkpoints listed in [advanced NLP and RAG](ADVANCED_NLP_AND_RAG.md). See [models and original training sources](MODELS_AND_DATA.md). Installing/downloading a model or indexing a study does not retrain it. Raw audio is processed in memory; approved demo information and inbox/audit records are stored locally. Never enter real patient identifiers or recordings in this academic installation.

Run the offline text-context regression checks without starting Docker:

```powershell
py -3 backend/evaluate_context.py --output docs/my-context-check.json
```

Use `python3` instead of `py -3` on macOS/Linux. The report checks synthetic text context, not speech accuracy or clinical validity.

## Stop, restart and update

Before accepting an installation, run `python scripts/verify_release.py` and complete the [release acceptance checks](RELEASE_ACCEPTANCE.md). Save the results for each teammate's laptop. Automated HTTP checks do not replace sign-in, microphone and user checks.

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
- Access waiting for approval: approve the email under WorkOS Users → Waitlist, then confirm organization membership and the staff access role. Waitlist approval alone is insufficient.
- Invalid or expired session: confirm client/organization IDs, native issuer and exact callback. The browser refreshes rejected tokens once. If the session genuinely ended, return to Access and sign in again; do not disable expiry checks. Rebuild after changing public IDs.

## Existing installations and alternate ports

Back up saved records and record the existing Compose project name before upgrading. A different project name can attach a different set of named volumes. The existing development laptop uses `omnimatch-renewed` and an ignored override for port 3013 and its model cache. New users should follow the default port 3000 instructions above, not copy laptop-specific override paths.

If intentionally using port 3013, allow `http://localhost:3013` and its exact `/login/` callback in WorkOS, and add the origin to backend `APP_ALLOWED_ORIGINS`. The setup helper currently verifies frontend port 3000; check alternate-port frontend reachability separately. Preserve your own override when rebuilding.

Public AWS deployment has a [separate guide](AWS_DEPLOYMENT.md). No AWS deployment is required to install this version locally.

## Accuracy focused speech profile

New installations use Whisper small after the controlled development comparison. It is slower and larger than base. For a constrained laptop, set WHISPER_MODEL=base in backend/.env and recreate the backend. See [measured results and limits](ACCURACY_UPGRADE.md). Small synthetic scores do not establish clinical accuracy.
