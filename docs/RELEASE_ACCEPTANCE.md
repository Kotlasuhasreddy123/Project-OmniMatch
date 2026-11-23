# Release acceptance and handover

Updated November 22, 2026. The approved academic use remains synthetic patient information and research-study review. No clinical forecasting, prescribing or universal accuracy claim is included in the release.

## Reproduce the installation checks

After following [installation](INSTALL_ON_YOUR_COMPUTER.md) and configuring your own approved email access:

```powershell
python scripts/verify_release.py --output output/installation-verification.json
```

For the existing laptop's alternate port:

```powershell
python scripts/verify_release.py --frontend http://localhost:3013 --output output/installation-verification.json
```

The verifier reads page responses, service readiness and unauthenticated API denial. It changes no visits and does not sign in. A successful response for a page does not establish working authentication, microphone input, visual accessibility or clinical accuracy.

## Designated user acceptance

One person operates while another records the actual outcome. Use fresh invented IDs beginning `DEMO-`. Each participant must use their own approved account. Record the date, release commit, computer, browser, operator, expected result, actual result, pass or fail, and any defect and retest. Automated tests are separate evidence from this observation.

| Check | Expected behavior |
| --- | --- |
| Consent off | Microphone remains unavailable. |
| Consent on | Consent is logged before capture starts. |
| Actual speech | Read a fictional note; compare each transcript word and correct errors. |
| Context | Patient diabetes and metformin may be approved; denied kidney disease and a mother's stroke remain excluded. |
| Explicit review | Pending or rejected terms do not enter the search. |
| Delivery | Record completion and inbox times; expected delay is at most 60 seconds. |
| Follow-up | Reuse the patient ID; a second distinct visit appears with new terms attributed to that visit. |
| Archive | Reviewed visit leaves active inbox; archived view and history retain it. |
| Restore | Restored visit is visible in the active inbox. |
| Account isolation | Account B cannot see account A's visits, even using the same patient ID. Direct record access is also denied. |
| Staff access | Approved staff can review; cannot perform admin-only actions. |
| Unapproved access | Public resources remain available, protected visits remain denied. |
| Session expiry | Refresh or sign-in recovery works; no authorization bypass. |
| Missing result | Empty suggestions are explained as index/query coverage, not absence of studies worldwide. |
| Simulated study | Referral remains unavailable. |

## User training effectiveness

Ask each designated user to repeat a visit without coaching, identify a wrong term, explain an unknown laboratory requirement, and archive then recover the review. Record what happened, assistance required and their actual feedback. The team previously confirmed practice with different scenarios; named attendance and unassisted results must come from participants.

Explain synthetic-only use, consent, approved accounts, personal inboxes, secure backups, no secrets in screenshots, incident reporting, retention and deletion requests. An email code verifies control of an address; a public physician registry match does not verify that the applicant owns that identity. Owner review remains manual.

## Free deployment choice

The selected demonstration arrangement is the public Render portal plus protected local Docker processing. Public pages are not a hosted inference API. This choice avoids provisioning paid compute. Provider quotas and service terms still apply; no permanent free entitlement is promised. AWS is an optional deployment guide and has not been provisioned as part of this release.

Each teammate installs from the repository on their own laptop, configures access, runs the verifier and then completes the manual checks above. Keep their local secrets private. Record the commit and successful results on each machine. This machine cannot establish another laptop's outcome.

## Final handover

Retain the code commit, installation results, test reports, requirements checklist, model/data provenance, user guide, testing/training record and final course report. Back up encrypted local data and demonstrate a restore using a disposable copy. Do not delete or replace the live volumes to test recovery.

Team members must confirm their own contributions and actual dates and review the final files. The supplied prompts identify a December 1, 2026 presentation, with five introduction slides in five minutes followed by twenty minutes of demonstration and questions, shared evenly among the three members. Verify exact final-report deadlines and the current rubric in Blackboard.
