# Local release and remaining work

OmniMatch is a synthetic-patient research project. The software checks and model scores answer different questions. Passing application tests does not establish 98% medical accuracy.

## Install or upgrade

Install Git, Python 3.10+ and Docker Desktop. Start Docker Desktop. In PowerShell:

```powershell
git clone https://github.com/Kotlasuhasreddy123/Project-OmniMatch.git
Set-Location Project-OmniMatch
python scripts/setup_local.py
```

Edit `backend/.env`: add your public `WORKOS_CLIENT_ID` and `WORKOS_ORGANIZATION_ID` after completing [passwordless setup](PASSWORDLESS_ACCESS.md). Keep secrets private. Do not use a shared password. The installer supplies these public IDs to the frontend build as well as the backend.

```powershell
python scripts/setup_local.py --start
# Optional larger local transformers and evidence research:
python scripts/setup_local.py --start --advanced
python scripts/setup_local.py --verify
```

The advanced download needs several GB of disk space and an internet connection. First inference and model switching can be slow on a laptop. Only two optional models are retained in memory at once. Speech and core search have their own models. This is not a hard total-memory cap.

Open http://localhost:3000. Verification returns a nonzero exit code while authentication is unconfigured. A configured provider still needs an actual approved-account email-code rehearsal.

For the existing laptop installation, preserve its project name and database volumes:

```powershell
python scripts/setup_local.py --start --project-name omnimatch-renewed
```

Back up the database and Qdrant before upgrading. Never run `docker compose down -v` on an installation whose records you need. The schema changes add columns; they do not delete existing inbox rows. Older visits without patient labels remain unlinked.

## Repeatable demonstration

1. Sign in with an approved account. Start a visit with the fictional label `DEMO-TEST`.
2. Grant consent, then record or enter: “The fictional patient has asthma and uses albuterol. No diabetes. Her mother had COPD.”
3. Check the transcript. Approve asthma and albuterol. Keep negated diabetes and family COPD excluded. Submit.
4. Open the inbox. Review the suggested study, missing information and source status. A ranking score is not a probability of eligibility or future disease.
5. Start another visit with the same label. Record or enter new information, review terms and submit. The timeline shows separate visit IDs and full timestamps, even on the same day.
6. Mark an inbox visit reviewed, then archive it. It leaves the active inbox but remains in the database and timeline. Select “Show archived visits” to restore it.
7. In Research, enter a fictional note, run analysis, explicitly approve terms, and ask a question about study criteria. Check the quoted sources. This separate workspace does not create an inbox visit.

## Completion evidence and limits

- Visit lifecycle tests use a real temporary SQLite database: repeat visits, retry deduplication, patient-only terms, archive retention, restore and authentication.
- Core NLP and advanced model measurements are recorded in [model results](MODEL_TRAINING_RESULTS.md) and [advanced NLP/RAG](ADVANCED_NLP_AND_RAG.md).
- 98% across specialties and languages is **not achieved**. Do not present application test pass rates as model accuracy.
- Owner-managed WorkOS setup, live email sign-in, team/user acceptance testing and any AWS deployment remain separate operator steps.
- Do not submit real patient information. Synthetic fixture studies cannot accept referrals. The public GitHub Pages site is an access/install portal; Python inference runs on the local installation.

Use [the installation guide](INSTALL_ON_YOUR_COMPUTER.md) for details and [the AWS guide](AWS_DEPLOYMENT.md) if you later choose cloud hosting. No paid cloud resources are created by these local commands.
