# Session repair and verification November 15 2026

The owner completed email-code login, but authenticated API requests showed an invalid or expired token error. Two integration assumptions caused the rejection: a required client_id claim that standard native session tokens do not require, and an issuer that did not match the application's native session issuer.

We confirmed the issuer using the provider's public OpenID discovery document. The backend now derives the native issuer when the setting is blank, while supporting an exact configured custom issuer. It still verifies the configured application's RSA signing keys, issuer, expiration, issued-at time, session, organization and access permission. Explicit client or audience claims must match if present. No token, email code or private key is logged. See [WorkOS's issuer guidance](https://github.com/workos/authkit-nextjs#optional-configuration).

The browser gets current tokens through the provider SDK. After HTTP 401 it forces one refresh and retries once. HTTP 403 is not retried. A repeated rejection asks for sign-in without deleting the unsent note. Network failures are not automatically resent because their outcome may be uncertain.

## Verification results

| Check | Observed result |
| --- | --- |
| Frontend tests | 77 passed |
| Backend regression | 250 passed, 3 skipped, 1 expected failure |
| Focused authentication and security checks | 45 passed |
| Production frontend and backend builds | Passed |
| Anonymous inbox and timeline | HTTP 401 |
| Signed-in consent | Saved successfully; recorder unlocked |
| First fictional written visit | Five extracted terms; three explicitly approved; negated and family terms excluded |
| Research matching | One simulated study suggestion saved for the first visit |
| Review and archive | Mark reviewed, archive, view archived and restore succeeded |
| Follow-up written visit | New session under the same patient label; asthma and albuterol approved; one suggestion saved |
| Timeline | Two visits; new terms listed in the second visit without overwriting the first |
| Production npm dependency audit | Zero reported vulnerabilities at scan time |
| Full npm audit including development tools | 13 findings: 6 moderate and 7 low; no high or critical findings |

These are software checks, not a clinical accuracy percentage. Existing model evaluation limits still apply. No neural fine-tuning was performed. The development-tool findings remain maintenance work and must not be described as resolved. GitHub's private alert page was unavailable in the signed-out browser, so its two alerts were not independently reconciled.

## Before presenting

Keep Docker healthy and open http://localhost:3013/session/ for the protected local workflow. Use a new fictional patient label, grant consent, record the planned dialogue, review the transcript and approve each relevant term. Do a fresh microphone rehearsal on every presentation laptop. The browser test above used written notes, not a live speech recording. Wait for the inbox's 30-second poll or refresh the page after matching.

The Render site is a free static portal; it does not host the Python models or saved patient database. Staff onboarding, denied accounts, provider sign-out and revocation still require wider acceptance checks. Tokens must expire; do not disable expiry to prevent session errors. Keep the refresh mechanism and sign in again when a session genuinely ends.
