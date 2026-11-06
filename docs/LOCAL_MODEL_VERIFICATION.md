# Local installation and model verification — November 5, 2026

- Two active pretrained checkpoints: Whisper (base by default) and sentence-transformers/all-MiniLM-L6-v2. Their source model cards are linked in MODELS_AND_DATA.md. No new model weights were trained in this change.
- Active extraction inspected directly: vocabulary and context regular expressions, rather than a loaded spaCy medical model.
- New synthetic regression: 69 examples, 72 expected target-term/context checks. Baseline 70/72; corrected rules 72/72. This is a development regression set used to fix the code, not held-out medical validation.
- Existing text extraction tests: 38 passed; the API integration test was excluded because the isolated test run does not initialize the full backend dependencies or services.
- Frontend: all 59 existing tests pass after adding the model explanations to the guide; TypeScript checks pass.
- The installer compiles, its argument/help path works, and its unavailable-Docker path exits with an actionable message. Two isolated unit tests check new secret generation, preservation of existing configuration, and failure before creating a configuration when Docker is unavailable.
- Base Compose configuration validates. Local Docker Desktop is stopped, so a new full-stack installation and real audio inference were not rerun in this change. Installing successfully on another person's system, medical speech accuracy, and ARM compatibility are not claimed as verified.
- No AWS services or paid accounts are required for the local path. The backend persists model caches under its Docker data volume; patient examples must remain synthetic.
