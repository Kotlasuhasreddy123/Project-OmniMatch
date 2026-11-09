# Security verification - November 9, 2026

Code verified: `ef59566` on the security-guardrails branch. This report records a synthetic-data development check, not an independent penetration test or clinical validation.

## Results

| Check | Recorded result |
| --- | --- |
| Full local backend suite, real models enabled | 244 passed, 1 expected failure; 306.60 seconds. No skipped tests. |
| Real integration | Qdrant retrieval, approved terms to inbox/timeline, cited RAG and consent-gated in-memory Whisper decoding passed. Temporary test records/indexes were separate from saved application data. |
| Frontend | 68 tests passed; TypeScript check passed. |
| GitHub checks | Backend verification, clinical regression, real transformer/integration checks, frontend checks and CodeQL Python/JavaScript passed for the code commit. |
| Python dependency advisories | 126 installed packages inventoried. No known findings among audited packages. The exact CPU torch label was skipped by PyPI lookup; a separate lookup normalized only `2.15.0+cpu` to upstream `2.15.0`, audited all 126 entries, and reported no known findings. This is advisory lookup, not binary analysis. |
| npm production dependencies | No known vulnerabilities reported. |
| npm including development tools | 13 reported entries: 7 low and 6 moderate, from deepmerge/minimatch dependency chains. No high/critical entries. Nonbreaking audit remediation did not resolve these; no forced major overrides were installed. |
| Bandit source scan | No medium/high findings. Three low findings concern the necessary FFmpeg subprocess/import/path. Reviewed: fixed argument list, no shell, pipe-only protocols, bounded input/output duration and timeout; a real malicious playlist test confirmed no HTTP fetch. Keep the executable search path under owner control. |
| AWS Compose configuration | Syntax/configuration validation passed. No cloud resources or certificates were provisioned. |

The test logs and machine-specific overrides remain in the unpublished local `output` working area; they are not credentials or configuration to copy into another installation. A SQLite backup was saved inside the persistent data volume before the local upgrade.

## Local rollout

The upgraded backend started successfully with Torch 2.15.0+cpu, Transformers 5.22.2, Whisper 20250625 and PyJWT 2.15.1. Health reported a connected Qdrant and loaded Whisper. All 62 running Python source files matched the tested checkout after line-ending normalization. The saved SQLite counts remained 11 inbox records and 26 audit entries; Qdrant retained all 18 indexed studies. The pre-upgrade backup is `/app/data/backups/before-security-20261109T061931Z.sqlite3` inside the persistent backend volume.

Live boundary checks returned HTTP 401 for an unauthenticated inbox request, 403 for an unapproved website origin, and 400 for an unapproved Host header. The frontend was rebuilt on Node 24.22.2; its live preview returned HTTP 200 with CSP installed. Backend and frontend containers enforce read-only application roots, all capabilities dropped, no privilege escalation and a 256-process limit. Qdrant uses the same privilege/process controls with its writable data storage.

## Model evidence and remaining accuracy work

The refreshed real-checkpoint development evaluation is in [advanced-model-evaluation.json](advanced-model-evaluation.json). It uses small author-created fictional fixtures, not representative clinical data:

- Hybrid target-term/context checks: 9/12 (75%).
- NLI assertion checks: 9/12 (75%).
- General tone checks: 7/12 (58.3%); not medical sentiment validation.
- RAG expected source/abstention: 11/12 (91.7%).
- Citation integrity: 8/8 (100%) returned excerpts matched their recorded source.

The expected test failure is the unmet broad NLP quality target. No results establish 98% overall accuracy, all-specialty/language validation, or real medical-speech accuracy. The silent-audio test establishes pipeline operation only. No model weights were fine-tuned during this security change.

## Before public deployment

WorkOS IDs remain blank for owner configuration. Live email sign-in, owner approval, revocation, user acceptance and AWS deployment still need testing. Independently verify encrypted disks/backups and TLS before enabling production. The production storage flag is an attestation, not an encryption implementation.

See [installed controls and limitations](SECURITY_GUARDRAILS.md), [passwordless setup](PASSWORDLESS_ACCESS.md), [AWS deployment](AWS_DEPLOYMENT.md), and [incident response](SECURITY_RESPONSE.md). Dependency results can change as new advisories are published; keep the update and scanning process active.
