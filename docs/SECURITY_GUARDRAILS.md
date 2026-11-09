# OmniMatch security guardrails

This guide describes installed controls and the checks still required before public deployment. Only fictional patient information is permitted. These controls do not establish HIPAA compliance or guarantee protection against every attack.

## Installed controls

| Area | What the application enforces |
| --- | --- |
| Account access | WorkOS RS256 signature, issuer, audience, expiry, organization and role checks. No shared-password fallback. Unknown or unapproved accounts cannot read visits. |
| Recording | Consent is required before microphone access. Consent changes are audited. Audio stays in memory; FFmpeg cannot fetch network playlists or local files. Uploads are capped at 50 MiB and decoded recordings at five minutes. |
| Clinical review | Extracted terms require individual approval. Negated and family-history findings cannot silently become patient search terms. |
| Request protection | Explicit browser origins and hostnames, request size and upload-time limits, bounded rate-limit state, one admitted model task at a time. |
| Private errors | Validation responses omit the submitted text. Unexpected server errors do not return tracebacks or secrets. Access logs are disabled for the packaged API. |
| Browser protection | Content Security Policy, frame blocking, MIME-type protection, limited microphone permissions and referrer controls. |
| Outbound callbacks | Disabled by default. Only owner-configured HTTPS destinations on an explicit hostname list are accepted; private IP addresses, environment proxies and redirects are rejected. Referral callbacks omit patient labels, visit terms and user identifiers. |
| Model boundaries | Fixed checkpoint revisions, safetensors, no remote model code, instruction-pattern screening and evidence-linked answers. Models do not have tools or permission to change account access. |
| Containers | Non-root application processes, dropped Linux capabilities, no privilege escalation, process limits and read-only application roots. Persistent data volumes remain writable. Database ports bind to localhost. |
| Repository | CodeQL Python/JavaScript checks, dependency update configuration, vulnerability alerts and secret push protection. Environment files and credentials are excluded from Git. |

## Setup before public use

1. Configure your own WorkOS application, organization, passwordless email flow and roles using [PASSWORDLESS_ACCESS.md](PASSWORDLESS_ACCESS.md). The IDs were deliberately left blank. Test owner approval, rejection and session revocation with separate accounts.
2. Generate two different random secrets; never reuse a password from a chat. Store them in the ignored backend environment file or a deployment secret store.
3. Set explicit browser origins and API hostnames. Do not use wildcard origins or expose Qdrant directly.
4. Use HTTPS and encrypted disks and backups. On AWS, verify EBS encryption before setting `ENCRYPTED_STORAGE_CONFIRMED=true`. That flag records your check; it does not encrypt anything. See [AWS_DEPLOYMENT.md](AWS_DEPLOYMENT.md).
5. Keep webhooks disabled unless needed. Enable only your trusted provider domain and enforce destination IPs with a network egress policy.
6. Run the acceptance checklist, back up saved records and test restoration before publishing.

## Honest limits

The prompt screen is a small English-oriented heuristic, not a complete multilingual safety classifier. Human review and evidence checks remain necessary. The browser policy still permits inline scripts for Next.js hydration; it is not a nonce-based strict CSP. Rate limits are per process and must be replaced or supplemented at the gateway before running multiple workers. Application DNS checks do not eliminate DNS rebinding; outbound network restrictions remain necessary. OS, Docker, TLS certificates, encrypted storage, backup protection and provider settings require ongoing owner maintenance.

No independent penetration test, live WorkOS email acceptance test or all-specialty clinical validation has been completed. Security tests and model task scores are separate: passing security checks does not establish 98% clinical accuracy.

## Verify the installed version

```powershell
docker compose ps
Invoke-RestMethod http://localhost:8000/api/v1/health
# A protected route without a token must return 401:
curl.exe -i http://localhost:8000/api/v1/inbox
# An unapproved browser origin must return 403:
curl.exe -i -X POST -H "Origin: https://unapproved.example" -H "Content-Type: application/json" -d "{}" http://localhost:8000/api/v1/consent
```

For development tests, run `python -m pytest tests -q` from the backend environment and `npm run test:run -- --runInBand` from the frontend. Real-model and real-FFmpeg checks require the packaged model environment and cached weights. The repository CI runs the matching verification workflows.

Report a suspected issue using [SECURITY_RESPONSE.md](SECURITY_RESPONSE.md). Do not send recordings, secrets or patient information in issue reports.
