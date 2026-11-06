# Public portal release and next steps

## What changed

- Shared staff/admin password sign-in is removed. Protected APIs accept WorkOS RSA-signed tokens with the configured application, organization and permission checks.
- The access page explains the waitlist, owner review and email-code flow. Blank provider IDs keep registration and sign-in disabled.
- Public pages now cover policies, licenses, model/data limits and specialty/language evaluation gaps. Results use condition badges alongside the existing local charts.
- GitHub Pages publishes static academic information, the sample results and installation links. Recording and medical-text processing remain in the local app. Public source remains available under MIT.
- CLI smoke checks now require a current approved identity token. The text smoke check asks a person to approve each term rather than approving terms automatically.

## Checks performed

On November 5, 2026 (Central Time), local frontend testing passed 61 tests, the TypeScript check and the production-package audit (zero reported vulnerabilities). Static export with `/Project-OmniMatch` as the base path succeeded. Desktop and mobile access-page layouts were visually inspected.

Backend tests passed 168 checks. One strict expected failure records the unresolved broad negation-recall requirement. The 100-transcript synthetic benchmark reports 29.7% recall, 77.0% precision and 42.9% F1 using its existing matching procedure. The separate focused development regression passes 72/72 assertions. These are different tests; neither is evidence of universal clinical accuracy.

The backend suite uses locally signed test-provider tokens and mocked components where appropriate. It does not verify a real WorkOS invitation/email exchange or a fresh Docker speech-model startup. Those checks remain pending. No new model weights were trained.

## Owner setup

1. Follow [PASSWORDLESS_ACCESS.md](PASSWORDLESS_ACCESS.md) to configure Magic Auth, the native waitlist and organization roles in WorkOS.
2. In GitHub, open the repository's **Settings → Secrets and variables → Actions → Variables**. Add `WORKOS_CLIENT_ID` and `WORKOS_ORGANIZATION_ID`. They are public IDs; no provider secret belongs in the frontend.
3. Under **Settings → Pages**, choose GitHub Actions as the source. The `Academic public portal` workflow builds and publishes the static site after updates to main. To refresh settings, open **Actions → Academic public portal → Run workflow**.
4. Test the entire invitation, approval, membership, code expiry and sign-out flow with test email accounts before opening registration. Reject unapproved accounts and verify staff cannot perform administrative actions.
5. Install locally using [INSTALL_ON_YOUR_COMPUTER.md](INSTALL_ON_YOUR_COMPUTER.md). Set matching public IDs in the frontend and backend, and rebuild. Use synthetic information only.

## Work still in progress

Representative medical speech testing, broader entity coverage, independent retrieval evaluation, additional languages, user acceptance testing and provider account-flow testing remain incomplete. See [VALIDATION_AND_TRAINING_PLAN.md](VALIDATION_AND_TRAINING_PLAN.md). Forecasting and prescribing models are not installed. Do not publish a 98–100% accuracy claim.

No paid cloud resources were provisioned. The AWS guide is optional and does not promise a free AWS deployment; local installation plus the academic static portal avoids that hosting expense. Public registration still depends on WorkOS's current service terms and your configuration.
