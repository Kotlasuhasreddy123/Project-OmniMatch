# Release verification November 22 2026

This record describes engineering checks on the Windows Docker installation and repository based on commit `399a8b7`. It does not establish clinical validity or final team acceptance. Patient test data is synthetic.

| Check | Observed result | Scope |
| --- | --- | --- |
| Backend regression | 264 passed, 3 skipped, 1 expected failure; 54.29 seconds | Isolated temporary databases and locally signed test identities; no live record changes |
| Real-model integrations | 3 passed; 180.35 seconds including model loading | Real Qdrant, cached models, in-memory Whisper input, cited evidence API |
| Warm index to inbox | 0.130 seconds | One fictional asthma scenario; not a capacity or general latency guarantee |
| Frontend | 86 passed across 21 suites | Components, consent, review, account display, session recovery, inbox lifecycle and charts |
| TypeScript | Passed | Static type checks |
| HTTP installation | 18 checks passed | 14 page responses, two unauthenticated requests denied with 401, service health and configured account IDs |
| Credential request automation | 12 passed | Mocked WorkOS and email behavior; no new email recipient contacted by these tests |
| Readiness guard tests | 2 passed | Missing or placeholder approvals cannot mark acceptance complete |
| Installation verifier tests | 3 passed | Open protected route or unloaded model fails; successful checks do not imply sign-in or clinical validity |
| npm dependency audit after update | Zero known production or development vulnerabilities | Compatible transitive dependency updates; all 86 frontend tests and TypeScript passed again |

The expected failure retains the broad NLP recall requirement rather than hiding it. The previously reported NLP latency assertion passed in the current full regression. This does not establish that latency under all machine loads will pass.

The first real-model run was stopped after speech processing competed heavily with the running application. A separate run with two CPU resources and bounded PyTorch settings passed the three integrations. The original under-load page check included a home-page timeout; a subsequent complete check passed after model-test load ended. Both records are retained privately. The application still needs workload-specific timing and a physical microphone rehearsal.

The npm audit initially identified a moderate minimatch denial-of-service advisory propagated through TypeScript ESLint development dependencies. Compatible lockfile updates removed the reported npm findings. A GitHub Dependabot alert was also reported by the push; its private detail page requires owner sign-in, so a zero local npm audit is not represented as independent confirmation that GitHub closed that alert. Deprecated build-tool notices also remain distinct from known audit findings.

## Reproduce

The full backend suite needs the backend image, current source mounted into an isolated verification directory, and a writable temporary test directory. Do not run against the live saved-visit database. Optional real integrations additionally need cached weights and a running Qdrant instance. See `backend/tests/test_local_stack.py` and `backend/tests/test_real_advanced.py` for the exact opt-in flags and isolated collection handling.

Frontend: `npm run test:run -- --runInBand` and `npx tsc --noEmit` from `frontend`.

Email automation: `node --test scripts/credential-email/automation.test.cjs`.

Installation: `python scripts/verify_release.py --frontend http://localhost:3013` for the existing laptop, or omit the frontend option for default port 3000. This command makes read-only requests and saves a report without tokens or account secrets.

## Evidence still requiring people

Fresh physical microphone quality, a new applicant receiving the credential email, actual owner approval/revocation, user acceptance comments, unassisted training results, teammate laptop installation, whole-team rehearsal and final authorship approval are not established by these automated tests. The instructor-requested video is assigned separately to the student. No AWS resources were provisioned, and no 90–98 percent application-wide medical accuracy, forecasting or prescribing capability is claimed.
