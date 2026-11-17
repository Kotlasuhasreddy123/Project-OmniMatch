# Contributing to OmniMatch

Start with the [installation guide](docs/INSTALL_ON_YOUR_COMPUTER.md). Use a branch for a focused change. Preserve existing visit data, indexes and model caches.

## Report a problem

Open an issue with the affected version or commit, operating system, steps to reproduce, expected result and actual result. Use synthetic examples only and redact logs. Report security problems privately using [SECURITY.md](SECURITY.md).

## Before proposing a change

- Explain the user-facing problem and the resulting behavior.
- Run relevant tests; the README lists frontend and backend commands.
- Keep consent, individual approval and backend authorization checks intact.
- Add meaningful regression coverage for a defect or new behavior.
- Update affected setup instructions, model notices and data licenses.
- Separate software checks from model evaluation and clinical claims.

Never commit environment files, credentials, email codes, recordings, real patient data, databases, model caches or dependency folders. Explain evaluation and migration requirements when changing model weights, dependencies or persistent schemas.

Source code uses MIT. Preserve third-party notices and verify the rights to contributed data, models and assets.
