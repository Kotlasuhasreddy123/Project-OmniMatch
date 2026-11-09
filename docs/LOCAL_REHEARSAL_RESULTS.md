# Local Docker rehearsal — November 8, 2026

The upgraded frontend, backend and Qdrant are running and healthy on the laptop. This completes the local service rehearsal. Owner email sign-in and user acceptance remain unfinished.

## Results

| Check | Actual result |
|---|---|
| Full backend suite in the built Docker image | 215 passed; one known expected failure; no unexpected failures |
| Known expected failure | The broad NLP negation-recall target remains unmet; it is not counted as a pass |
| Real study retrieval | Pinned MiniLM embeddings searched a real Qdrant collection |
| Visit completion | Approved asthma/albuterol terms produced a saved inbox result; negated and family terms stayed excluded |
| Matching to inbox timing | 0.067 seconds in the successful rerun, after model/index warm-up; not a general latency guarantee |
| Evidence research | A real reranker/generator pipeline returned the asthma study's COPD exclusion source |
| Speech pipeline | Real Whisper decoded a one-second silent WAV entirely in memory after consent; no speech-accuracy result is claimed |
| Protected inbox without sign-in | HTTP 401 |
| Removed password-login endpoint | HTTP 410 |
| Advanced checkpoint cache | All six checkpoints present; advanced mode enabled on this laptop |
| Existing records | All 11 inbox rows, 26 audit rows and 18 simulated studies retained |
| Temporary test collections | None left after testing |
| Website previews | HTTP 200 at ports 3000 and 3013 |

The GitHub real-model workflow also passed the two new integration checks and the existing real-model API check. Its fixture database and Qdrant collection are separate from the laptop's saved records. Test identities are signed by a temporary test key inside the test process. They do not enable public account access or verify WorkOS email delivery.

The original run had one configuration-dependent test failure: a mocked live-sync test inherited `DEMO_MODE=true` from the local installation. The application correctly refused live sync. The test fixture now sets its own mode, and an added test confirms that demo mode still returns HTTP 409 without starting a live sync. The failed log/XML were retained alongside the corrected run.

Do not convert the application test pass count into a model-accuracy percentage. The broad extraction benchmark and advanced-model development results remain separate. **98% medical accuracy is not achieved.** No model weights were fine-tuned in this recovery update.

## Open the application

- Main website: http://localhost:3000
- Existing preview address: http://localhost:3013/preview
- Backend health: http://localhost:8000/api/v1/health
- API documentation: http://localhost:8000/api/docs

Sign-in stays disabled until the owner completes [WorkOS configuration](PASSWORDLESS_ACCESS.md). There is no shared-password fallback. The public preview uses illustrative data; it is available while registration is unconfigured.

## Current laptop startup commands

Run these from the `omnimatch-visual-release` folder in PowerShell:

```powershell
docker compose --env-file backend/.env -p omnimatch-renewed -f docker-compose.yml -f output/local-model-cache.compose.yml up -d
docker compose --env-file backend/.env -p omnimatch-renewed -f docker-compose.yml -f output/local-model-cache.compose.yml ps
python scripts/setup_local.py --verify
```

The local override reuses this laptop's downloaded models through a read-only mount and also exposes port 3013. It is a machine-specific file under `output`, not a portable GitHub setting. The verification command intentionally returns nonzero while WorkOS is unconfigured, even though service health passes.

On another computer, follow [the portable installation guide](INSTALL_ON_YOUR_COMPUTER.md). Use `python scripts/setup_local.py --start --advanced` to download models into that installation's own data volume.

## Repeat the real integration checks

After configuring and preparing the portable Docker installation, run from its repository root in PowerShell:

```powershell
$backendSource = (Resolve-Path backend).Path
docker compose --env-file backend/.env run --rm --no-deps -e OMNIMATCH_LOCAL_STACK_TESTS=1 --volume "${backendSource}:/app:ro" backend python -m pytest tests/test_local_stack.py -q -s -p no:cacheprovider
```

On this laptop, include `-p omnimatch-renewed -f docker-compose.yml -f output/local-model-cache.compose.yml` after `--env-file backend/.env` to use its existing volumes and model-cache override. The test creates and deletes only its own randomly named `omnimatch_rehearsal_…` study collection and uses temporary SQLite files. It does not delete saved patient visits.

## Recovery and resource settings

Docker was first unable to start after the earlier disk-full failure. Its data file was copied while Docker/WSL were stopped. The original and backup have matching full-file SHA-256 checksums. The backup is outside OneDrive at `%LOCALAPPDATA%\OmniMatch\recovery\docker_data-before-recovery-20261108.vhdx`; keep it until recovery is no longer needed. This follows [Docker's backup guidance](https://docs.docker.com/desktop/settings-and-maintenance/backup-and-restore/).

Windows then reported a low-virtual-memory condition during image packaging. This laptop completed the build and tests with the following `%USERPROFILE%\.wslconfig` settings:

```ini
[wsl2]
memory=4GB
processors=4
swap=8GB
```

These settings apply to all WSL 2 distributions, including any added later. They are local machine settings, not changes to the repository or a universal hardware recommendation. Swap uses disk and may slow inference. Adjust them through WSL settings if future workloads need different limits. See [Microsoft's WSL configuration guide](https://learn.microsoft.com/en-us/windows/wsl/wsl-config). No browser tabs or editor windows belonging to the user were closed.

Local evidence is retained in `output/local-docker-tests.log`, `output/local-docker-tests.xml`, `output/local-rehearsal-results.json` and `output/docker-recovery-backup.json`. The earlier failed test run is retained as `output/local-docker-tests-initial.*`.
