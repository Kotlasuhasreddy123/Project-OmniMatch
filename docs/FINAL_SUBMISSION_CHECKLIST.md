# Final submission readiness

Prepared November 9, 2026. This is a status checklist, not an approval or a claim of clinical validation.

## Completed software work

- [x] Consent before microphone access, explicit term approval, asynchronous research inbox and role checks.
- [x] Pinned terminology provenance and licenses, ambiguity review, context regression and evidence quotation checks.
- [x] Speech comparison with raw error counts and latency tradeoff documented in [Accuracy upgrade](ACCURACY_UPGRADE.md).
- [x] Real-model backend verification: 250 passed, one expected failure for the unmet broad-recall target. Frontend: 69 passed.
- [x] Local installation, optional AWS deployment, passwordless setup, security controls and model/data documentation.
- [x] Prepared private cumulative report, testing/training draft, technical manual, future individual preparation drafts and rubric checklist.

## Owner and team acceptance gates

- [ ] Configure WorkOS client and organization IDs, then test owner approval, rejected access, email sign-in, expiry and revocation. Never put API secrets in the browser or GitHub.
- [ ] Record designated-user acceptance: expected outcome, actual outcome, pass/fail, issue and correction for each scenario.
- [ ] Record scenario-training attendance, unassisted operation and actual feedback. Previously confirmed practice does not establish formal acceptance or measured training effectiveness.
- [ ] Confirm the latest Blackboard prompts, milestone rubric, deadline and advisor feedback. The supplied syllabus and older project description differ.
- [ ] Each author verifies personal contributions, rewrites preparation drafts in their own words and follows the course AI/authorship rules.
- [ ] Choose local installation or hosted deployment, verify it on the intended machine and complete handover. GitHub Pages serves the public portal; it cannot run the Python API or Qdrant.
- [ ] All members review and approve the final files before one group member submits the group report. Individual journals remain separate.

The cumulative draft includes 33 body pages and at least 10 background pages in the verified rendering. Page count alone does not establish rubric compliance. Recheck after editing or importing into Google Docs.

## Reproduce readiness

```powershell
python scripts/final_readiness.py --services --write-json output/readiness-report.json
```

Exit code 2 means an item remains pending. The script never treats missing approval or a string saying `true` as completed acceptance. Supply `--attestations path-to-private-json` only after retaining the underlying evidence. The seven keys are listed in the script; do not commit personal acceptance records.

## Accuracy limits

No 98 percent application-wide medical accuracy has been established. Broad English development F1 is 85.0 percent; small exact-set and retrieval fixtures score 100 percent on their own tasks. Whisper small has 3.3 percent word error on eight single-voice synthetic notes. These measurements cannot be combined into an overall clinical score. Independent labeled encounters, languages and specialties remain unvalidated.

## What to hand in

Use the professor's cumulative report template, refreshed contents and numbered figures/tables. Include the updated task checklist, testing/training evidence, feedback responses and complete references. Keep account secrets, real patient data, model caches, databases and private individual drafts out of the public repository. Future journals are preparation worksheets until the named student supplies actual work and feedback.

## Confirmed upcoming Blackboard requirements

The owner supplied these updated prompts during preparation. They replace conflicting older syllabus summaries:

- Week 12: one group Milestone 2 report, building on Milestone 1; cover Weeks 10–12 implementation, testing, training, updated task schedule, individual contributions and actual Milestone 1 feedback. Due Sunday 11:59 p.m. Central Time.
- Week 13: individual demonstration reflection, actual feedback, personal work, testing/training findings, changes, incomplete tasks and prioritized action plan. Progress demonstration November 17, 2026; journal due Sunday 11:59 p.m. Central Time.
- Week 14: individual final-readiness journal, assigned Week 13 corrections, retesting, presentation and report responsibilities, rehearsal and dated action plan. Due Sunday 11:59 p.m. Central Time.
- Week 15: December 1, 2026 final presentation, 25 minutes with equal member participation. Five introductory slides in five minutes, then twenty minutes for the live demonstration and questions. The full application must be available on each member laptop.
- Week 16: one unified final group report built on Milestone 2, plus each student's private final reflection. Both are due Thursday 11:59 p.m. Central Time. Individual reflections require a justified project completion percentage and evidence-based ratings for every member; neither can be filled with model accuracy or assumed future outcomes.

No Week 12 or Week 15 individual journal prompt was supplied. Future preparation notes for those weeks must not be presented as required submissions. Actual Milestone 1 and November 17 feedback remain to be supplied. Verify the final-report rubric and exact Blackboard calendar dates before uploading.
