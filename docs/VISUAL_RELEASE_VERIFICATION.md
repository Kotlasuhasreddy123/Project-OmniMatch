# Visual results release — November 4, 2026

Release branch: feat/visual-results-refresh. The separate local renewed app retains its previously unpublished work; this release applies the presentation changes to the repository baseline.

- Frontend release: 58 tests pass across 10 suites, including empty-data and metric-update checks for ResultsOverview.
- TypeScript checks pass after completing the existing referral test fixture.
- Next.js production compilation, page generation and standalone build finish successfully on both the renewed local app and the isolated release checkout.
- Existing renewed frontend: 69 tests pass across 12 suites before adding the release-specific chart tests.
- No backend/model changes, model training, external user acceptance study or AWS provisioning performed.

Builds use the machine's existing installed dependency tree (Next 14.2.5). A clean npm install could not be completed: dependency resolution requested an unavailable @babel/traverse version (^7.29.13). The manifest declares Next 14.2.35. Resolve and lock dependencies in CI before treating the AWS build as reproducibly verified. A passing cached build is not evidence that a fresh machine will install successfully. See AWS_DEPLOYMENT.md for setup and acceptance checks.

Charts are local HTML/CSS with text labels, respond to input records, and do not upload data to a chart service. They count criterion checks per suggestion, so repeated study criteria can appear more than once. Review score is a ranking metric and is not clinical accuracy.
