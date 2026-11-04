# Visual results release — November 4, 2026

Release branch: feat/visual-results-refresh. The separate local renewed app retains its previously unpublished work; this release applies the presentation changes to the repository baseline.

- Frontend release: 59 tests pass across 10 suites, including empty-data, metric-update, criterion-count and ranking-order checks for ResultsOverview.
- TypeScript checks pass after completing the existing referral test fixture.
- Next.js production compilation, page generation and standalone build finish successfully on both the renewed local app and the isolated release checkout.
- Existing renewed frontend: 69 tests pass across 12 suites before adding the release-specific chart tests.
- No backend/model changes, model training, external user acceptance study or AWS provisioning performed.

A fresh checkout outside OneDrive installed successfully with an isolated cache. A subsequent `npm ci` succeeded using the generated lockfile, replacing the earlier cached-dependency-only verification. Dependency auditing identified advisories in Next.js 14; the release upgrades to Next.js 15.5.29 and PostCSS 8.5.32 (including a transitive override). The production dependency audit reports zero known vulnerabilities at verification time. This does not establish application or clinical security. GitHub CI installs from the lockfile, checks types, runs tests, audits production dependencies and builds both the application and frontend Docker image.

The AWS Compose overlay passes `docker compose config --quiet`. Docker Desktop was stopped during local checks, so local container execution and AWS provisioning have not been verified. AWS instructions include private SSH rehearsal, a concrete Caddy HTTPS overlay, backup and rollback procedures.

Charts use Recharts with a numerical list and a local HTML/CSS criterion-coverage bar. They respond to input records and do not upload data to a chart service. They count criterion checks per suggestion, so repeated study criteria can appear more than once. Review score is a ranking metric and is not clinical accuracy. `/preview` contains invented display fixtures separate from inbox records.

Security reference: [Next.js upstream security update](https://nextjs.org/blog/nextjs-security-update-october-14-2026). Chart implementation reference: [Recharts BarChart](https://recharts.github.io/en-US/api/BarChart/).
