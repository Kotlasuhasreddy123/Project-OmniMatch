# Week 7 Journal: Individual Implementation Progress and Comparison

**Suhas Reddy Kotla — CPSC-69100 — October 11, 2026**  
**Draft for personal review before submission.** This entry describes the AI/AWS lead's project work supported by the current working copy and its test results. Suhas should confirm which tasks he personally performed or supervised before submitting an individual journal.

## Implementation accomplishments

My assigned Week 5–7 responsibility in our Project Plan and Launch Report is the match engine and missing-variables logic (TSK-05), building on my earlier audio/extraction work (TSK-03). This week I initiated an AI-assisted verification and integration review of that workflow in a separate Chatgpt working copy. The review checked how extracted entities enter matching, whether the clinician-approval gate is preserved, and how the backend's consent, NLP, matching, inbox, and access-control paths behave with synthetic data. The resulting working copy includes integration corrections to missing-variable parsing, family-history context, and tests that incorrectly depended on a live vector service. It now has 155 passing backend tests out of 157, plus 54 passing frontend tests, a clean type check and lint run, and a successful frontend production build. These checks make the prototype easier to demonstrate and expose its remaining weaknesses; they do not prove clinical readiness.

## Incomplete tasks and schedule

TSK-05 is not complete against the plan's quality target. On the 100-transcript synthetic evaluation, extraction/negation recall was 27.8%, far below the 95% REQ-03 goal. On a separate 20-transcript comparison, the ensemble F1 was 0.7812, below the simpler NegEx baseline's 0.8065. I expect to work on term coverage, negation scope, and separate error analysis before the Week 8 milestone, then retest on held-out data. I will not describe the current ensemble as better until the measurements support that claim. The Whisper medical-term error-rate target, actual Qdrant/ClinicalTrials.gov synchronization, and a measured session-to-inbox time remain unverified because this verification environment did not have a running Docker/Qdrant stack or a live audio-model benchmark. I also need to coordinate with Rosie on security validation and Venkata on a complete browser workflow; their assigned tasks are not my individual deliverables. AWS deployment and security controls should be described as pending verification, not completed compliance work.

## Comparison with existing work and useful ideas

TrialGPT reports patient-to-trial retrieval, criterion-level matching, and ranking, showing that basic AI trial matching and criterion explanations are established research directions [1]. An AWS clinical-trial-screening architecture similarly emphasizes evidence for each criterion, missing information, and a clinician's final decision [2]. The Tempus TIME trial portal demonstrates that operational trial matching also needs EHR-connected updates, human review, and site coordination [3]. OmniMatch's present academic distinction is the combination of consent-gated ambient visit input, explicit per-entity clinician approval, and deferred trial routing to an inbox. I do **not** claim those features are unique worldwide or that our prototype outperforms these systems. The most useful practice to adopt is criterion-level evidence with clear “unknown/missing” states, followed by human review; I will also use the TrialGPT evaluation example to define a more rigorous, held-out test set. The official ClinicalTrials.gov API v2 documentation remains the source for structured study data [4].

## Self-evaluation and strengths

I rate my contribution **Satisfactory**. I can point to a testable AI-to-matching path and a broad set of passing automated checks, but two NLP quality tests still fail and the end-to-end stack has not been verified. My strengths this week were initiating the integration review, making limitations measurable, and keeping the prototype focused on synthetic data and clinician oversight. I think this is more useful than presenting a polished score without checking whether the underlying clinical concepts were actually recognized.

## Areas for improvement and challenges

I need to improve clinical vocabulary coverage, distinguish a missed entity from an incorrect negation decision, and test ambiguous examples such as family history and repeated mentions. I will create a labeled error table, fix the highest-frequency misses, and rerun the same regression suite plus a separate held-out set. The immediate technical challenge is that rule-based patterns cover a limited portion of our synthetic transcripts; another is that local mocks allow API tests to pass while Qdrant, Whisper, and timing behavior remain untested. Scheduling-wise, the Week 8 milestone leaves little room for a full clinical-grade evaluation, so I will prioritize a trustworthy synthetic demonstration and document limits explicitly.

## Instructor support

I would appreciate Dr. Alzoubi's feedback on whether our Week 8 scope should narrow to one disease area, which synthetic evaluation design is appropriate for the 95% NLP target, and how to report an unmet target responsibly in the final project report. Guidance on the minimum acceptable end-to-end demonstration would help us prioritize the remaining work. The project should be evaluated as a simulated research prototype, not as a deployed clinical product.

## References (IEEE style)

[1] Q. Jin *et al*., “Matching patients to clinical trials with large language models,” *Nature Communications*, vol. 15, art. 9074, 2024. doi: [10.1038/s41467-024-53081-z](https://doi.org/10.1038/s41467-024-53081-z).

[2] S. Jain, R. Pathangi, P. Allam, and S. Basak, “AI-powered clinical trial eligibility and safety using Amazon Bedrock AgentCore,” *AWS Architecture Blog*, Aug. 19, 2026. [Online]. Available: [AWS article](https://aws.amazon.com/blogs/architecture/ai-agents-for-clinical-trial-screening/). Accessed: Oct. 11, 2026.

[3] A. Rao *et al*., “The Tempus TIME Trial Portal and Clinical Trial Enrollment,” ASCO 2023 presentation, May 26, 2023. [Online]. Available: [Tempus publication](https://www.tempus.com/publications/the-tempus-time-trial-portal-and-clinical-trial-enrollment/). Accessed: Oct. 11, 2026.

[4] U.S. National Library of Medicine, “ClinicalTrials.gov API Version 2.0 now available,” *NLM Technical Bulletin*, 2024. [Online]. Available: [NLM notice](https://www.nlm.nih.gov/pubs/techbull/ma24/ma24_clinicaltrials_api.html). Accessed: Oct. 11, 2026.
