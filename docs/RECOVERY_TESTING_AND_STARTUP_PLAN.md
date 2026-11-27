# Recovery testing and startup plan

Updated November 26, 2026, Central Time. The regression and browser results below were recorded on November 22; subsequent installation checks are dated separately. This supplements the earlier release verification record. All patient scenarios are synthetic. Automated tests do not establish clinical accuracy, completed user acceptance, or physical microphone quality.

## Latest engineering results

| Check | Result | What this establishes |
| --- | --- | --- |
| Backend regression | 268 passed, 1 failed, 3 skipped, 1 expected failure across 273 collected tests; 60.48 seconds | Isolated API and module regression, including five additional recovery tests |
| NLP speed recheck | Failed; 86.34 ms average against a 50 ms target | The performance target is not met on this run; the full suite also measured 65.62 ms |
| Frontend regression | 94 passed across 22 suites; 27.062 seconds | Includes eight new pending-visit and explicit-retry checks |
| TypeScript | Passed | Static type checking of the updated frontend |
| Public browser checks | Passed | Sample results, expanded case explanation, keyboard result sorting, protected inbox redirect to sign-in |

The expected backend failure preserves the broader NLP quality target; it must not be counted as a passing accuracy test. The three skipped integrations need explicit cached-model/local-service execution. Timing measurements are machine-specific and are not the full visit-to-inbox latency. Earlier results remain dated historical records rather than replacing these findings.

## Defects found and corrected

1. An invalid completion request could claim the URL session ID before rejecting a mismatched body. Validation now happens before ownership is claimed.
2. Duplicate historical rows for one session could inflate term mention counts. History now deduplicates sessions before aggregation.
3. A background matching exception could place its raw message in logs. Logging now retains the exception category without the potentially private message.
4. The browser saved a pending-visit marker but the inbox did not display it. The inbox now shows processing status, warns after the 60-second target, and offers refresh or an explicit retry of the same previously approved findings. A received inbox item clears the marker. Switching accounts cannot expose another account's pending payload.

Additional checks confirmed that concurrent retries store one visit, a transient search failure can recover on a later explicit retry, and a disposable SQLite backup can be restored while retaining archive state and account ownership. This restore test uses fixture data; it is not a verification of live-volume encryption or a production disaster-recovery exercise. The retry mechanism is not a durable job queue and does not guarantee processing survives a server restart.

## Checks still requiring people or a production environment

- A fresh WorkOS sign-in, approval and revocation flow using the actual accounts. The available browser session was signed out; no authentication codes were retrieved or bypassed.
- Physical microphone recording with a person speaking, including correction of transcription errors and handling denied microphone permission.
- Independent user acceptance, unassisted training outcomes, and installation on each teammate's laptop.
- Load and endurance tests, restart-safe job delivery, encrypted backup restore, and external security review on the intended deployment.
- Independent clinical evaluation by specialty, language, site and outcome. The application has no validated universal accuracy, future-disease probability or prescribing capability.

The public Render deployment serves the portal. Protected inference and saved-visit processing currently run in the local Docker installation. These are different deployment surfaces.

## Strongest initial startup use case

We recommend a research-coordinator assistant for reviewing possible clinical trials and missing patient information. Start with one specialty, one language and one research site selected through interviews. The existing combined workflow—reviewed findings, evidence, study criteria, personal history and an asynchronous inbox—is a useful starting point. Its commercial value and novelty still need customer and competitor validation.

ClinicalTrials.gov provides programmatic access to publicly available study records [1]. A startup version should display source identifiers, recruitment status, site details, protocol version and refresh dates; a search result alone is not confirmation that a site can enroll someone.

## Prioritized future uses

| Priority | Use case | Required improvement | Measure of value |
| --- | --- | --- | --- |
| First | Coordinator trial prescreening | Current registry records, reviewed patient evidence, criterion explanations | Review time, precision and recall at the reviewed shortlist size, missed exclusions |
| First | Missing-information worklist | Named missing fields, dates and source links, clear unknown states | Correct missing fields and fewer repeated chart checks |
| Next | Follow-up review alerts | Durable jobs and new verified observations linked to prior criteria | Useful alerts accepted, false alert burden, delivery latency |
| Next | Read-only EHR import | Authorized FHIR connection, site-specific profiles, provenance and consent | Correct imported fields and reconciliation errors |
| Later | Research-site feasibility | Governed aggregate queries with tenant separation and small-group protection | Time to evaluate a protocol without exposing individual records |
| Later | Patient study navigation | Accessible explanations, consent and coordinator handoff | Understanding, successful handoffs and accessibility outcomes |
| Research | Comparable historical cases | Licensed or authorized deidentified cases with source context | Clinician-rated relevance and provenance completeness |
| Separate research program | Future-risk estimates | Longitudinal outcome labels, defined time horizon, calibration and independent evaluation | Discrimination, calibration and clinical utility on external data |

FHIR supports exchange of healthcare information [2]. A connector must use the version, profiles and authorization supported by each site. It must not silently assume that every EHR exposes the same records. Historical case displays must never show another user's private records simply because symptoms are similar.

Forecasting and medicine recommendations require separate intended-use, data, safety and regulatory assessment. They are not achieved by adding a ranking score or increasing a training epoch count. FDA guidance explains how clinical decision support functions are assessed [3]. For US covered entities or business associates using cloud services for electronic protected health information, appropriate business-associate arrangements and HIPAA safeguards are relevant [4]; the current synthetic-data project is not a claim of clinical compliance.

## Proposed ninety day plan

**Days 1 to 30:** Interview coordinators, select one painful workflow, define the intended use, close the observed speed issue, add durable job status and retries, complete live account and microphone checks, and establish data permissions. Keep patient data synthetic until appropriate governance exists.

**Days 31 to 60:** Build one authorized read-only data connector, refresh study records, create clinician-adjudicated evaluation labels and hold out encounters and sites. Compare assisted review with the current manual workflow. Record false positives, missed exclusions, explanation quality and actual review time.

**Days 61 to 90:** Consider a small governed pilot only if earlier gates pass. Test isolation, audit trails, recovery, retention, accessibility and operational support. Obtain real user feedback and cost estimates before choosing a paid research-site subscription model. These are planning estimates, not completed milestones or a promise of free clinical hosting.

## Release gates for a startup pilot

Use independently reviewed evaluation data and report precision, recall, extraction F1, speech word-error rate, shortlist relevance, and performance by subgroup. Do not combine these into one application-wide accuracy percentage. Set clinical thresholds with qualified reviewers before evaluating the held-out set.

Require zero unauthorized cross-account access in the defined security test set, visible source provenance for every study suggestion, demonstrated restore procedures, explicit consent, observable job failures and tested access revocation. A proposed business goal is reduced coordinator review time; it remains a hypothesis until measured in a baseline comparison.

## Sources

[1] ClinicalTrials.gov. How to Download Study Records. https://clinicaltrials.gov/data-api/how-download-study-records

[2] HL7 International. FHIR Overview. https://www.hl7.org/fhir/overview.html

[3] US Food and Drug Administration. Clinical Decision Support Software guidance, January 2026. https://www.fda.gov/regulatory-information/search-fda-guidance-documents/clinical-decision-support-software

[4] US Department of Health and Human Services. HIPAA and Cloud Computing. https://www.hhs.gov/hipaa/for-professionals/special-topics/health-information-technology/cloud-computing/index.html
