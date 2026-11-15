# OmniMatch team demonstration script and questions

Prepared November 15 2026 for Tuesday November 17. The supplied timetable calls November 17 the progress demonstration and December 1 the final presentation. This guide uses the supplied 25 minute format. Confirm the meeting time and actual limit in Blackboard.

## Start with the correct claim

We turn a fictional visit into reviewed findings, research suggestions and a saved visit history. We show the evidence and information that still needs checking. We do not predict disease, prescribe medication or establish final trial eligibility. Similar cases in this update are six authored teaching examples, not real patient outcomes or published case studies. Our distinction is the combined workflow, not a claim that no other product has these features.

The last full real-stack evaluation was November 9: 250 backend tests passed, with one expected failure for unmet broad recall; 69 frontend tests passed. Broad English development F1 was 85.0 percent, recall 82.3 percent and precision 87.8 percent. Small targeted context and exact-set fixtures passed 72/72 each. Hybrid target/context and RAG expected-source-or-abstention passed 12/12 each. Whisper small made three word edits in ninety synthetic reference words, or 3.3 percent word error. Do not call these 90 percent application accuracy. The November 15 frontend run passed 73 tests and TypeScript checking; the updated frontend production image built successfully. No backend code or neural model weights changed in this presentation update.

## Speaking plan

Allow five minutes for five introductory slides and twenty minutes for the demonstration and questions. Each member receives about eight minutes twenty seconds overall. The operator pauses while another person speaks and makes every click visible.

| Time | Speaker | Screen or action |
| --- | --- | --- |
| 0 to 1 | Suhas | Slide 1 title and members |
| 1 to 2 | Rosie | Slide 2 client and users |
| 2 to 3 | Venkata | Slide 3 problem and overview |
| 3 to 4 | Suhas | Slide 4 tools and architecture |
| 4 to 5 | Rosie | Slide 5 verified responsibilities |
| 5 to 11 | Venkata | Live visit input and review; teammates read the dialogue |
| 11 to 17 | Suhas | Matching, evidence, models and measured results |
| 17 to 22 | Rosie | Follow-up history, case comparison, archive and security |
| 22 to 25 | All | About one minute of questions each |

## Slides one to five exact narration

Suhas slide 1: Good afternoon. We are HealthTech Innovation Labs. I am Suhas Reddy Kotla, and my teammates are Rosie Roy Barla and Venkata Papaiah Thrinadha Nagamahesh Akula. Our project is OmniMatch. We help organize information from a visit so that a person can review possible research studies. We will show the complete path from a fictional conversation to reviewed terms and a saved history. I will explain the AI and evaluation, Rosie will explain the backend and security, and Venkata will guide the user experience. Please watch how the review steps keep an uncertain finding from silently becoming a fact.

Rosie slide 2: We do not have an external hospital client. Our team represents a simulated clinic and research coordinator. The intended users are clinical staff who review a note and coordinators who examine study suggestions. Those are different activities. The clinician checks what was actually said. The coordinator checks whether the study information is relevant and complete. All patient information in this demonstration is fictional. We are showing our academic workflow, not presenting a medical deployment or a compliance certification.

Venkata slide 3: A visit may mention a patient's condition, a medicine, a denied disease and a relative's history together. Searching every disease word would produce the wrong patient profile. Our interface therefore separates recording, transcript correction, term approval and study review. We also preserve earlier visits under one patient label. The new history view highlights what was added and repeated without assuming that something disappeared just because it was not mentioned again. We want users to understand why a result appears and what information is still missing.

Suhas slide 4: The browser uses Next.js, React and TypeScript. FastAPI handles requests and checks access. Whisper small turns audio into text locally. Programmed context rules and a pinned English disease dictionary propose findings. Optional transformer models support medical term proposals and evidence retrieval. Sentence embeddings and Qdrant retrieve studies, while SQLite stores visit and audit records. Docker packages the services. Downloading pretrained weights and indexing studies are not the same as training a model. I will show our own measurements separately from model-publisher claims.

Rosie slide 5: Our responsibilities follow the project plan. Suhas focuses on AI, evaluation and infrastructure coordination. I focus on backend behavior, access and security. Venkata focuses on the interface and the visit and inbox flow. Before presenting, each of us must confirm the personal work we describe against our commits and notes. Our current implementation includes consent checks, explicit term approval, later inbox delivery, repeated visits, archive and restore, and evidence-linked review. We will also point out the remaining account and validation requirements rather than hide them.

## First visit complete conversation

Only begin this section if the preflight shows an authenticated working application. Venkata operates the screen. Rosie reads the doctor. Suhas reads the patient. Read only the quoted dialogue into the microphone; do not read the stage directions. Use patient label DEMO-1117-A. Confirm recording is disabled before consent, then grant consent and start recording. Use normal voices, a quiet room and one microphone.

Doctor: Hello. This is a fictional visit for our project demonstration. May I record our conversation for this exercise?

Patient: Yes, I agree.

Doctor: Please tell me about your current conditions and the medicine you take.

Patient: I have type 2 diabetes and high blood pressure. I take metformin.

Doctor: Is there anything you want to clearly record as absent from your own history?

Patient: I do not have kidney disease.

Doctor: Is there any family history you would like to mention separately?

Patient: My mother had a stroke. That is my mother's history.

Doctor: Thank you. We will check the transcript together before using it for the research search.

Patient: That is correct.

Venkata stops recording, waits once, and reviews the actual transcript. If a drug word or negation is wrong, correct it visibly. If the model cannot finish, switch to the written-note fallback below and state what happened. Never repeatedly click Submit.

Venkata: The transcript is an intermediate result. I check it before extraction because a wrong medicine name could affect the next step. Now I review the extracted terms. I expect the patient's diabetes, high blood pressure and metformin to be available for approval. Kidney disease should remain negated, and stroke should remain family history. I check the actual output rather than assuming the script guarantees it. I approve the relevant patient findings explicitly. The family and denied terms must not enter the search. If the term says only diabetes, I correct or clarify the subtype rather than silently treating it as type 2. I now submit the reviewed visit once.

Written fallback note: The patient has type 2 diabetes and high blood pressure and takes metformin. The patient denies kidney disease. The patient's mother had a stroke.

Do not promise an exact number of studies. The repository starts with three fictional studies; the existing laptop previously retained eighteen simulated records. Check the actual index before rehearsing. A no-result outcome must be explained honestly.

## Study results and AI explanation

Suhas opens the newly saved inbox item and expands one returned study.

Suhas: We now see possible studies from the configured catalog. The ranking score helps order suggestions. It is not a disease probability, model accuracy or a guarantee of enrollment. I can inspect the matched terms and each criterion. A laboratory requirement may remain unknown because it was not stated. The correct response is to identify the information needed, not invent a laboratory value. A denied condition does not prove every exclusion is cleared. A human still checks the full protocol and the patient's current information.

Suhas: These study records are simulated, so referral is blocked. That means the record cannot be sent as a real enrollment opportunity. It is expected behavior, not a failed search. Our demo is about organizing a review. If we use live registry data later, we also need to verify recruitment status, freshness, sites and the complete protocol.

Suhas: Whisper is pretrained speech recognition. The default is small because it made fewer word errors than base in our eight-note synthetic comparison, at higher processing time. Our English term dictionary now contains 30,995 unambiguous variants, with twenty ambiguous aliases requiring review. Those are dictionary entries, not thirty thousand conditions that we clinically validated. We retain exact source and license information.

Suhas: The optional evidence workflow combines keyword retrieval, dense embeddings and reranking. It uses a small generator for a restricted quotation task and checks the returned text against the source. If evidence is insufficient, the system can abstain. A correct citation does not by itself prove medical relevance. We keep those tests separate. Our broad NLP F1 is 85 percent on an inspected development corpus. Some smaller tasks scored perfectly, but we do not combine them into a claimed 90 or 98 percent overall medical accuracy.

If the optional research page is configured, ask: What medicine is mentioned in the selected asthma study? Inspect the actual returned passage and citation. Then ask: What disease will this patient develop next? Explain the abstention. Skip this optional step if model readiness is incomplete. Do not count a skipped demonstration as a pass.

## Follow-up visit and comparison script

Rosie: Now I will show why the patient label and session ID are different. The same fictional patient can have multiple visits. I keep DEMO-1117-A and start another session. I do not edit the earlier visit to make it look as though the new information was already there.

Doctor: Welcome back. What information would you like to add to your record today?

Patient: I also have asthma and use albuterol.

Doctor: Is the information about your mother's history still separate from your own conditions?

Patient: Yes. My mother's stroke is not my own condition.

Doctor: We will review this update before sending it for research review.

Patient: Yes, please.

Operator reviews and approves the actual output. For matching that needs earlier information, select Load previous approved terms and explicitly approve relevant history again. Submit once, then open Timeline for DEMO-1117-A.

Rosie: Here are two separate visits under the same label. The new comparison shows terms added in the latest visit, repeated terms, and terms not repeated. Not repeated does not mean resolved or stopped. The system does not assume that an earlier medicine was discontinued. This is a comparison of recorded words, not a prediction of worsening disease.

Rosie: The similar-case panel compares this approved history with six authored teaching cases. It displays the shared terms and each example's two-visit history. The count is literal overlap, not a probability or measured accuracy. These examples are not actual past patients or published case reports. They help demonstrate the interface; they cannot justify prescribing. To support actual outcome prediction, we would need a defined outcome and time horizon, permitted longitudinal data, independent labels, calibration and evaluation on a separate population. We have not done that work.

Rosie marks the inbox item reviewed, archives it, confirms it is hidden from the normal inbox, then opens the archived filter and restores it. Do not permanently delete data or clear volumes.

Rosie: Archive cleans the working inbox while keeping the saved visit. Restore brings it back. Access is checked by the API, not just by hiding a screen. Consent is recorded before audio, and audio is processed in memory. Visits, approved terms and audit records are still persistent data. Our current account setup must be verified; neither a public website nor a visible login button proves the protected application is ready. We do not claim that a software scan establishes HIPAA compliance.

## Closing and short version

Suhas: Our contribution is an inspectable path from a fictional visit to reviewed research information. We separate what the system found, what a person approved and what remains unknown.

Rosie: We preserve visit history and apply access and consent checks. We also retain honest limits around accounts, deployment and validation.

Venkata: We make those decisions visible through clear screens, visit comparisons, result charts and missing-information explanations. Thank you. We are ready for questions.

For a ten minute progress meeting use one minute for the introduction, three for the first visit, two for results, two for repeat history and archive, and two for questions. Omit optional model inference and extra case exploration. Never rush through consent and approval.

## Questions for Suhas

1. Did you train all these models? We use publisher-pretrained Whisper and transformer weights. The latest improvement used terminology grounding, context-rule corrections and retrieval changes. No neural fine-tuning was performed in that update. An older experimental TF-IDF classifier remains disconnected from the live workflow.
2. Is the system 90 percent accurate? No application-wide clinical accuracy is established. I can report each task, dataset and metric separately, including the broad F1 of 85 percent and the small synthetic speech error rate.
3. Why not simply use an LLM? We need explicit evidence and review boundaries. A fluent answer alone does not establish a clinical fact or eligibility. Our retrieval and quotation checks limit unsupported output, while still allowing abstention.
4. Which BERT techniques run? The optional workflow uses a DeBERTa medical entity model, MiniLM embeddings, MiniLM NLI and an MS MARCO cross-encoder. The tone model is a DistilBERT variant; tone does not drive medical matching. Exact repository revisions are in the model registry.
5. Can you predict future disease? Not with validated performance. We compare prior visits and highlight missing information. A true prediction requires a defined outcome, time horizon, independently labeled longitudinal data and clinical evaluation.
6. Why do small tests reach 100 percent while broad F1 is lower? They measure different tasks and difficulty. The small fixtures are known development checks. We disclose the broader failures rather than select only the best score.
7. What happens for an unseen symptom? The vocabulary or transformer may propose it, but human review is required. The small catalog may have no relevant study. No match does not mean no disease or no trial exists.
8. What would you train next? Define a specific task first, secure permitted representative data, split by encounter or speaker, freeze an independent test set, train on development data and compare errors and calibration. We would not fit repeatedly on the final evaluation examples.

## Questions for Rosie

9. Where is patient information stored? The local installation uses SQLite for visit and audit records and Qdrant for study vectors. Only fictional data is permitted. Audio processing is in memory; that does not mean the whole system stores nothing.
10. How is login protected? The API verifies WorkOS token signatures, organization and permissions. Password login is retired. Until the owner configures and tests the WorkOS application, the protected live flow remains unavailable.
11. Is it HIPAA compliant? We have implemented and tested controls in a synthetic academic system. We have not established legal compliance or passed an independent clinical security assessment.
12. What if someone skips the frontend approval? The backend filters the submitted entities too. A crafted request must not silently match pending, rejected, negated or non-patient findings.
13. Why block outreach? Simulated studies cannot accept real referrals. Real outreach also requires verified recruitment, sites and eligibility information.
14. Are archived visits deleted? No. They are hidden from the active view and can be restored. Retention and actual deletion are separate policy and implementation decisions.
15. Can it all run on free Render? A static site can be free. The current model stack needs much more memory and persistent storage than a simple static site. Free web services can spin down and lose local files. We do not claim the current SQLite and model setup is durable on that plan.
16. Why not remove sign-in for the demo? A presentation is not a reason to remove access controls. We configure the account or clearly demonstrate the public display examples instead.

## Questions for Venkata

17. Why does a second visit not change the first? Each encounter has a new session ID. A shared patient label links the visits without overwriting the earlier record.
18. Why not automatically reuse all earlier terms? History may be outdated or irrelevant. A person must select and approve relevant information again for the current search.
19. What does the colored result score mean? It is a ranking aid based on retrieval and rule checks. It is not diagnostic confidence, medical accuracy or enrollment probability.
20. Are the similar cases real? No. They are six authored fictional teaching cases. We label them and display the shared terms. We do not claim observed outcomes or cite them as published clinical evidence.
21. How is the design accessible? We provide labeled controls, keyboard focus, readable explanations and text alongside colors. Automated tests do not establish complete WCAG conformance; manual checks remain necessary.
22. How does this differ from existing applications? Ambient scribes emphasize documentation, registry search exposes study records, and TrialGPT research includes retrieval and criterion matching. We combine consent-gated visit input, per-term approval, deferred review, repeat-visit history and visible evidence in a small local academic workflow. We do not claim worldwide novelty or commercial superiority.
23. What if the microphone fails? We explain the failure and use the written-note route with the same review and approval steps. We do not claim that a text fallback demonstrated successful speech recognition.
24. What if the page shows no results? We check approved terms, the configured catalog and service readiness. We show the empty-state explanation rather than invent a match.

## Rehearsal and release checks

Twenty-four hours before the meeting, verify the full workflow on all three laptops using the same release. Confirm the meeting time, speaking order and five slides. Use a fictional patient label unique to the rehearsal. Record expected and actual outcomes, not just a pass-rate headline. Check actual WorkOS sign-in, consent, microphone permission, transcript correction, explicit approval, inbox arrival time, two visits, comparison, archive and restore. Retain screenshots as fallback and mark them as captured examples.

Start the local installation from its project root in PowerShell:

```powershell
git clone https://github.com/Kotlasuhasreddy123/Project-OmniMatch.git
cd Project-OmniMatch
py -3 scripts/setup_local.py --start
py -3 scripts/setup_local.py --verify
docker compose ps
Invoke-RestMethod http://localhost:8000/api/v1/health
Invoke-RestMethod http://localhost:8000/api/v1/auth/config
```

Do not clone into an existing project folder or overwrite its environment file. On the current development laptop, the existing Compose project is omnimatch-renewed and the existing ignored override preserves port 3013 and the model cache:

```powershell
docker compose --env-file backend/.env -p omnimatch-renewed -f docker-compose.yml -f output/local-model-cache.compose.yml up -d
docker compose --env-file backend/.env -p omnimatch-renewed -f docker-compose.yml -f output/local-model-cache.compose.yml ps
```

Health must report Qdrant connected and Whisper loaded. Authentication config must report configured true before calling the full protected flow ready. Do not paste secrets into slides, a terminal recording or GitHub. Do not run docker compose down -v. Do not change models or dependencies during the presentation. Plug in power and test the room microphone and network before the audience arrives.

## Free public website and Render distinction

The existing free public site is https://kotlasuhasreddy123.github.io/Project-OmniMatch/ and its display demonstration is /preview/. This portal is separate from the protected local API and saved database. A live browser interaction with a static example is not a live AI inference demonstration.

We created a free Render Static Site named omnimatch-research in the existing owner workspace. Its public address is https://omnimatch-research.onrender.com/ . Its source is this repository on main, root directory frontend, publish directory out and build command npm ci && OMNIMATCH_STATIC_EXPORT=true NEXT_PUBLIC_PORTAL_MODE=true npm run build. NODE_VERSION is 24.22.2; NEXT_PUBLIC_BASE_PATH uses the empty default. The first build began from d9bfe1e; verify the newest successful deployment before presenting. WorkOS account setup is still pending, so protected live sign-in is not ready. Do not put backend secrets into NEXT_PUBLIC variables.

For an existing Render service with auto deployment enabled, a merge to its linked branch can trigger deployment. Otherwise use the service's Manual Deploy control. A deploy-hook URL is a secret and must stay outside code and documents. Do not create a paid service or call a static portal the complete hosted ML backend.

Render references checked November 15 2026: https://render.com/docs/free and https://render.com/docs/deploy-hooks . Free web services can spin down after fifteen idle minutes and lose local filesystem changes on redeploy or restart; they cannot attach a persistent disk. This is why our free demonstration plan retains the model stack and saved database locally.

## WorkOS owner setup record

The signup page was opened for the owner email. It states that account creation accepts its Terms of Service and Privacy Policy. The automation paused for explicit agreement confirmation; it has not claimed a completed account, public client ID or organization ID. Continue only after that confirmation and any user-controlled credential step. Use the free staging environment; do not add a card, paid custom domain, enterprise SSO or paid service. Configure Magic Auth, waitlist, organization membership and the two permissions as described in docs/PASSWORDLESS_ACCESS.md. Add https://omnimatch-research.onrender.com and its exact /login/ redirect if enabling authentication on that portal. Rebuild both local services after setting the public IDs, then test approval, rejected access, OTP, sign-out and revocation. Record actual results before calling the live demonstration ready.
