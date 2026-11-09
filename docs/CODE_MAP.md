# Code learning map

Generated from this checkout. Line numbers identify definitions, not proof that every legacy helper is active. Read route imports from `backend/app/main.py` and the browser page imports to trace the active path.

## How a visit moves through the system

1. The Next.js visit page collects a fictional patient label and explicit consent. The browser only requests its microphone after consent.
2. The API checks identity, consent and input limits. FFmpeg decodes in memory and Whisper small transcribes. No audio file is saved.
3. Rule/context extraction and optional biomedical transformer findings are shown for review. Ambiguous terms remain pending.
4. Only explicitly approved patient findings enter the search. Qdrant retrieves studies; criteria are review checks, not enrollment confirmation.
5. Background matching writes a visit to the inbox. A patient label groups separate sessions; archive removes a reviewed visit from the active view without deleting its database history.
6. RAG retrieves passages, reranks literal evidence and checks citations/abstention. Tone and NLI are auxiliary signals, not medical judgments.

## Models

Whisper small is a publisher-pretrained speech model. The six pinned transformer checkpoints are listed in `backend/app/understanding/model_registry.py`. The embedding checkpoint is reused for retrieval. No neural checkpoint was fine-tuned in this update. A local English Disease Ontology snapshot is terminology, not a trained model. See [models and data](MODELS_AND_DATA.md) and [measured accuracy](ACCURACY_UPGRADE.md).

## Backend definitions

### `backend/app/__init__.py`
Module definitions and supporting helpers.


### `backend/app/audio/__init__.py`
Module definitions and supporting helpers.


### `backend/app/audio/router.py`
Audio ingestion router — RAM-only audio processing (REQ-08).

- [transcribe_audio, line 27](../backend/app/audio/router.py#L27): Transcribe an in-memory audio buffer using Whisper ASR.

### `backend/app/auth/__init__.py`
Module definitions and supporting helpers.


### `backend/app/auth/consent_router.py`
Consent audit logging router — REQ-01, REQ-11.

- [log_consent, line 19](../backend/app/auth/consent_router.py#L19): Log a patient consent grant or revocation to the append-only audit log.

### `backend/app/auth/jwt_handler.py`
JWT creation and verification utilities.

- [create_access_token, line 18](../backend/app/auth/jwt_handler.py#L18): Create a signed JWT access token.
- [decode_token, line 37](../backend/app/auth/jwt_handler.py#L37): Decode and validate a JWT token.
- [get_current_user, line 65](../backend/app/auth/jwt_handler.py#L65): FastAPI dependency that extracts and validates the current user from a Bearer token.
- [require_role, line 86](../backend/app/auth/jwt_handler.py#L86): FastAPI dependency factory that enforces role-based access control.

### `backend/app/auth/router.py`
Password authentication was retired; WorkOS verifies passwordless identities.

- [retired_password_login, line 10](../backend/app/auth/router.py#L10)
- [current_identity, line 14](../backend/app/auth/router.py#L14)
- [authentication_config, line 18](../backend/app/auth/router.py#L18)

### `backend/app/auth/workos_verifier.py`
Verify provider signatures and application/organization permissions; never trust UI claims.

- [refresh_keys, line 21](../backend/app/auth/workos_verifier.py#L21)
- [verify_workos_token, line 40](../backend/app/auth/workos_verifier.py#L40)

### `backend/app/config.py`
Application configuration loaded from environment variables via pydantic-settings.

- [Settings, line 7](../backend/app/config.py#L7): Central settings object — all values sourced from .env or environment.

### `backend/app/data/__init__.py`
Module definitions and supporting helpers.


### `backend/app/digest/__init__.py`
Module definitions and supporting helpers.


### `backend/app/digest/digest_service.py`
End-of-day digest + sponsor referral webhook service — NEW FEATURES.

- [ensure_referrals_table, line 43](../backend/app/digest/digest_service.py#L43): Create the referrals table if it doesn't exist.
- [initiate_referral, line 50](../backend/app/digest/digest_service.py#L50): Log a sponsor referral and optionally fire a webhook.
- [send_daily_digest, line 126](../backend/app/digest/digest_service.py#L126): Send an end-of-day digest to a webhook endpoint.

### `backend/app/digest/router.py`
Referral and digest routers — NEW FEATURES 5 & 7.

- [create_referral, line 34](../backend/app/digest/router.py#L34): Initiate a sponsor referral for a matched clinical trial.

### `backend/app/eligibility/__init__.py`
Module definitions and supporting helpers.


### `backend/app/eligibility/criterion_engine.py`
Per-criterion eligibility scoring engine — NEW FEATURE differentiating OmniMatch.

- [CriterionVerdict, line 23](../backend/app/eligibility/criterion_engine.py#L23)
- [CriterionResult, line 31](../backend/app/eligibility/criterion_engine.py#L31): Result of evaluating one eligibility criterion against a patient session.
- [EligibilityBreakdown, line 42](../backend/app/eligibility/criterion_engine.py#L42): Full per-criterion breakdown for one trial match.
- [_is_lab_criterion, line 77](../backend/app/eligibility/criterion_engine.py#L77): Return True if the criterion requires a lab value.
- [_is_exclusion_section, line 82](../backend/app/eligibility/criterion_engine.py#L82): Return True if the text is part of an Exclusion Criteria section.
- [_split_criteria, line 87](../backend/app/eligibility/criterion_engine.py#L87): Split eligibility text into inclusion and exclusion criterion lines.
- [_match_criterion_to_entities, line 129](../backend/app/eligibility/criterion_engine.py#L129): Evaluate a single eligibility criterion against patient entities.
- [compute_enrollment_readiness, line 199](../backend/app/eligibility/criterion_engine.py#L199): Compute the composite Enrollment Readiness Score (0–100).
- [evaluate_trial_eligibility, line 247](../backend/app/eligibility/criterion_engine.py#L247): Perform full per-criterion eligibility evaluation for one trial.

### `backend/app/evidence/__init__.py`
PHI-minimizing evidence ledger for human-verified trial matching.


### `backend/app/evidence/ledger_service.py`
Evidence Ledger helpers.

- [_canonical_event, line 29](../backend/app/evidence/ledger_service.py#L29): Generate a deterministic digest for the PHI-minimized evidence event.
- [approved_evidence_spans, line 39](../backend/app/evidence/ledger_service.py#L39): Return only spans for approved, patient-context, non-negated entities.
- [link_criterion_evidence, line 53](../backend/app/evidence/ledger_service.py#L53): Attach approved transcript anchors only to MET criterion results.
- [record_evidence_ledger, line 79](../backend/app/evidence/ledger_service.py#L79): Persist a PHI-minimized, tamper-evident evidence-review event.

### `backend/app/evidence/router.py`
Evidence Ledger API routes.

- [create_evidence_ledger, line 13](../backend/app/evidence/router.py#L13): Record an approved evidence event without storing the raw transcript.

### `backend/app/inbox/__init__.py`
Module definitions and supporting helpers.


### `backend/app/inbox/router.py`
Asynchronous Clinical Trial Inbox router — REQ-07, REQ-10.

- [_run_matching_and_store, line 38](../backend/app/inbox/router.py#L38): Background task: run trial matching and write results to the inbox.
- [complete_session, line 173](../backend/app/inbox/router.py#L173): Mark a visit session as complete and trigger asynchronous trial matching.
- [list_inbox, line 223](../backend/app/inbox/router.py#L223): Return all inbox items for authorized clinical staff.
- [get_inbox_item, line 269](../backend/app/inbox/router.py#L269): Return a single inbox item by ID.
- [mark_reviewed, line 313](../backend/app/inbox/router.py#L313): Mark an inbox item as reviewed.
- [archive_item, line 345](../backend/app/inbox/router.py#L345): Hide a reviewed item without deleting its result or patient history.
- [restore_item, line 367](../backend/app/inbox/router.py#L367)

### `backend/app/main.py`
OmniMatch FastAPI application entry point.

- [_schedule_daily_sync, line 49](../backend/app/main.py#L49): Register the daily sync job and end-of-day digest with APScheduler.
- [private_validation_error, line 144](../backend/app/main.py#L144)
- [private_server_error, line 150](../backend/app/main.py#L150)
- [on_startup, line 173](../backend/app/main.py#L173): Initialize database tables, Qdrant collection, and APScheduler on startup.
- [on_shutdown, line 208](../backend/app/main.py#L208): Gracefully shut down the APScheduler.
- [health_check, line 219](../backend/app/main.py#L219): Return system health status including Qdrant connectivity.

### `backend/app/matching/__init__.py`
Module definitions and supporting helpers.


### `backend/app/matching/router.py`
Trial match engine router — REQ-05, REQ-06, REQ-07.

- [_generate_missing_variables, line 35](../backend/app/matching/router.py#L35): Compare trial eligibility criteria against approved patient entities.
- [search_trials, line 78](../backend/app/matching/router.py#L78): Query Qdrant for trial matches using only APPROVED clinical entities.

### `backend/app/models/__init__.py`
Module definitions and supporting helpers.


### `backend/app/models/database.py`
Async SQLite database setup for audit logs and inbox storage.

- [get_db, line 63](../backend/app/models/database.py#L63): Open and return a database connection for use as a FastAPI dependency.
- [init_db, line 73](../backend/app/models/database.py#L73): Create all tables on application startup if they don't exist.

### `backend/app/models/schemas.py`
Shared Pydantic v2 schemas used across the OmniMatch API.

- [UserRole, line 16](../backend/app/models/schemas.py#L16)
- [ConsentAction, line 21](../backend/app/models/schemas.py#L21)
- [EntityType, line 26](../backend/app/models/schemas.py#L26)
- [EntityStatus, line 34](../backend/app/models/schemas.py#L34)
- [InboxStatus, line 40](../backend/app/models/schemas.py#L40)
- [LoginRequest, line 49](../backend/app/models/schemas.py#L49)
- [TokenResponse, line 54](../backend/app/models/schemas.py#L54)
- [TokenPayload, line 60](../backend/app/models/schemas.py#L60)
- [ConsentRequest, line 70](../backend/app/models/schemas.py#L70)
- [ConsentResponse, line 80](../backend/app/models/schemas.py#L80)
- [TranscriptionResponse, line 90](../backend/app/models/schemas.py#L90)
- [ClinicalEntity, line 107](../backend/app/models/schemas.py#L107)
- [EvidenceSpan, line 130](../backend/app/models/schemas.py#L130): A client-side transcript anchor for a human-verified entity.
- [CriterionEvidence, line 151](../backend/app/models/schemas.py#L151): An auditable, PHI-minimizing link from a criterion to approved evidence.
- [EvidenceLedgerRequest, line 162](../backend/app/models/schemas.py#L162)
- [EvidenceLedgerResponse, line 168](../backend/app/models/schemas.py#L168)
- [NLPExtractRequest, line 176](../backend/app/models/schemas.py#L176)
- [NLPExtractResponse, line 181](../backend/app/models/schemas.py#L181)
- [MatchSearchRequest, line 193](../backend/app/models/schemas.py#L193)
- [TrialMatch, line 201](../backend/app/models/schemas.py#L201)
- [MatchSearchResponse, line 235](../backend/app/models/schemas.py#L235)
- [InboxItem, line 246](../backend/app/models/schemas.py#L246)
- [InboxListResponse, line 257](../backend/app/models/schemas.py#L257)
- [SyncResponse, line 267](../backend/app/models/schemas.py#L267)
- [SessionCompleteRequest, line 278](../backend/app/models/schemas.py#L278)
- [SessionCompleteResponse, line 288](../backend/app/models/schemas.py#L288)
- [HealthResponse, line 298](../backend/app/models/schemas.py#L298)
- [ReferralRequest, line 309](../backend/app/models/schemas.py#L309)
- [ReferralResponse, line 319](../backend/app/models/schemas.py#L319)
- [TimelineEntry, line 329](../backend/app/models/schemas.py#L329)
- [TimelineVisit, line 339](../backend/app/models/schemas.py#L339)
- [PatientTimelineResponse, line 348](../backend/app/models/schemas.py#L348)

### `backend/app/nlp/__init__.py`
Module definitions and supporting helpers.


### `backend/app/nlp/context_candidate.py`
Experimental assertion classifier. Not used by the live extraction endpoint.

- [context_features, line 14](../backend/app/nlp/context_candidate.py#L14)
- [ContextCandidate, line 25](../backend/app/nlp/context_candidate.py#L25)

### `backend/app/nlp/negex_pipeline.py`
NegEx-based NLP pipeline for clinical entity extraction with negation detection.

- [subject_prefix, line 187](../backend/app/nlp/negex_pipeline.py#L187): Scope family history to the latest explicitly stated subject.
- [_compile_patterns, line 193](../backend/app/nlp/negex_pipeline.py#L193): Compile a list of regex pattern strings into Pattern objects.
- [_get_compiled_patterns, line 199](../backend/app/nlp/negex_pipeline.py#L199): Return cached compiled regex pattern groups.
- [_check_context, line 212](../backend/app/nlp/negex_pipeline.py#L212): Check if a trigger pattern appears within a word-window around the entity match.
- [extract_entities, line 253](../backend/app/nlp/negex_pipeline.py#L253): Extract clinical entities from a transcription with negation and context classification.

### `backend/app/nlp/router.py`
NLP entity extraction router — REQ-03.

- [extract_clinical_entities, line 22](../backend/app/nlp/router.py#L22): Extract clinical entities from a transcription using the NegEx pipeline.

### `backend/app/nlp/variants/__init__.py`
Module definitions and supporting helpers.


### `backend/app/nlp/variants/biobert_v3.py`
Unused experimental zero-shot NLI wrapper, retained under a legacy filename.

- [_get_pipeline, line 23](../backend/app/nlp/variants/biobert_v3.py#L23): Lazy-load the zero-shot classification pipeline.
- [classify, line 55](../backend/app/nlp/variants/biobert_v3.py#L55): Classify assertion type using zero-shot NLI.
- [is_available, line 122](../backend/app/nlp/variants/biobert_v3.py#L122): Check if the BioBERT variant is available in this environment.

### `backend/app/nlp/variants/ensemble_v4.py`
Variant 4: Ensemble Voter — Combines NegEx + NegBio + optional BioBERT.

- [classify_ensemble, line 27](../backend/app/nlp/variants/ensemble_v4.py#L27): Ensemble negation classification combining NegEx + NegBio + optional BioBERT.
- [benchmark_variants, line 118](../backend/app/nlp/variants/ensemble_v4.py#L118): Run all 4 variants on test transcripts and compute accuracy metrics.

### `backend/app/nlp/variants/negbio_v2.py`
Unused rule experiment under a legacy NegBio-inspired filename.

- [classify, line 61](../backend/app/nlp/variants/negbio_v2.py#L61): Classify negation using NegBio-style extended dependency window.

### `backend/app/nlp/variants/negex_v1.py`
Unused standalone NegEx-style rule experiment.

- [_compiled, line 47](../backend/app/nlp/variants/negex_v1.py#L47)
- [classify, line 56](../backend/app/nlp/variants/negex_v1.py#L56): Classify negation/context for one entity span using classic NegEx window.

### `backend/app/nlp/vocabulary.py`
English terminology for synthetic research conversations.


### `backend/app/security/__init__.py`
Module definitions and supporting helpers.


### `backend/app/security/boundaries.py`
Deterministic HTTP and compute boundaries; no clinical text is logged here.

- [bounded_inference, line 14](../backend/app/security/boundaries.py#L14)
- [RequestBoundaryMiddleware, line 22](../backend/app/security/boundaries.py#L22)

### `backend/app/security/deployment.py`
Fail closed on obvious public-deployment misconfiguration.

- [validate_production, line 5](../backend/app/security/deployment.py#L5)

### `backend/app/security/middleware.py`
Security middleware — rate limiting, input sanitization, request validation.

- [RateLimitMiddleware, line 39](../backend/app/security/middleware.py#L39): Simple in-process sliding-window rate limiter.
- [SecurityHeadersMiddleware, line 83](../backend/app/security/middleware.py#L83): Add security headers to every response.
- [sanitize_clinical_text, line 123](../backend/app/security/middleware.py#L123): Sanitize clinical transcription text for safe NLP processing.
- [sanitize_session_id, line 149](../backend/app/security/middleware.py#L149): Sanitize a session ID to prevent injection.
- [sanitize_entity_term, line 163](../backend/app/security/middleware.py#L163): Sanitize a clinical entity term.
- [validate_no_sql_injection, line 177](../backend/app/security/middleware.py#L177): Check if text contains SQL injection patterns.

### `backend/app/security/model_policy.py`
Heuristic screening complements, but never replaces, permission/output gates.

- [instruction_like, line 12](../backend/app/security/model_policy.py#L12)

### `backend/app/security/webhooks.py`
Opt-in, owner-configured destinations only. Never accept a caller URL.

- [post_configured_webhook, line 10](../backend/app/security/webhooks.py#L10)

### `backend/app/sessions/__init__.py`
Module definitions and supporting helpers.


### `backend/app/timeline/__init__.py`
Module definitions and supporting helpers.


### `backend/app/timeline/router.py`
Patient timeline router — NEW FEATURE 3.

- [get_timeline, line 34](../backend/app/timeline/router.py#L34): Return the longitudinal entity timeline for a pseudonymized patient.

### `backend/app/timeline/timeline_service.py`
Approved-term history for fictional patients, not a diagnosis or a new match query.

- [ensure_timeline_table, line 35](../backend/app/timeline/timeline_service.py#L35): Create the patient_timeline table if it doesn't exist.
- [upsert_patient_entities, line 47](../backend/app/timeline/timeline_service.py#L47): Merge new session entities into the patient's longitudinal timeline.
- [get_patient_timeline, line 116](../backend/app/timeline/timeline_service.py#L116): Return the full entity timeline for a patient across all visits.
- [get_cumulative_entities, line 137](../backend/app/timeline/timeline_service.py#L137): Return all entity terms ever approved for this patient across all visits.
- [detect_eligibility_unlocks, line 153](../backend/app/timeline/timeline_service.py#L153): Detect if new session entities fill previously-missing trial criteria.

### `backend/app/transcription/__init__.py`
Module definitions and supporting helpers.


### `backend/app/transcription/whisper_service.py`
Whisper ASR service — transcribes audio from in-memory buffers only.

- [is_whisper_loaded, line 24](../backend/app/transcription/whisper_service.py#L24): Report whether the speech model is present in this server process.
- [_get_whisper, line 29](../backend/app/transcription/whisper_service.py#L29): Lazy-load the whisper module.
- [get_whisper_model, line 38](../backend/app/transcription/whisper_service.py#L38): Load and cache the Whisper model.
- [TranscriptionService, line 56](../backend/app/transcription/whisper_service.py#L56): Wraps OpenAI Whisper for RAM-only audio transcription.
- [get_transcription_service, line 130](../backend/app/transcription/whisper_service.py#L130): Return the singleton TranscriptionService instance.

### `backend/app/trials/__init__.py`
Module definitions and supporting helpers.


### `backend/app/trials/clinicaltrials_client.py`
ClinicalTrials.gov API v2 client for fetching and syncing trial data.

- [ClinicalTrialsClient, line 27](../backend/app/trials/clinicaltrials_client.py#L27): Async HTTP client for ClinicalTrials.gov API v2.

### `backend/app/trials/embedding_cache.py`
Embedding cache — prevents redundant sentence-transformer calls.

- [_cache_key, line 35](../backend/app/trials/embedding_cache.py#L35): Generate a stable cache key from a list of entity terms.
- [get_cached_query_vector, line 41](../backend/app/trials/embedding_cache.py#L41): Return a query embedding vector, using cache when available.
- [get_cache_stats, line 79](../backend/app/trials/embedding_cache.py#L79): Return current cache statistics for monitoring.
- [clear_cache, line 92](../backend/app/trials/embedding_cache.py#L92): Clear the embedding cache (useful in tests).
- [upsert_trials_batched, line 107](../backend/app/trials/embedding_cache.py#L107): Upsert trial vectors in optimized batches.

### `backend/app/trials/freshness_service.py`
Trial Freshness Gate for safe coordinator outreach.

- [_parse_date, line 17](../backend/app/trials/freshness_service.py#L17)
- [evaluate_trial_freshness, line 29](../backend/app/trials/freshness_service.py#L29): Return an explainable gate for outreach, never a clinical eligibility claim.

### `backend/app/trials/proximity_service.py`
Geographic proximity trial ranking — NEW FEATURE differentiating OmniMatch.

- [haversine_distance, line 62](../backend/app/trials/proximity_service.py#L62): Calculate great-circle distance in miles between two lat/lon points.
- [get_clinic_coords, line 80](../backend/app/trials/proximity_service.py#L80): Return (lat, lon) for a clinic ZIP code, or None if not found.
- [fetch_trial_locations, line 92](../backend/app/trials/proximity_service.py#L92): Fetch site locations for a trial from ClinicalTrials.gov API v2.
- [rank_by_proximity, line 128](../backend/app/trials/proximity_service.py#L128): Re-rank trial matches by geographic proximity to the clinic.

### `backend/app/trials/qdrant_config.py`
Qdrant collection configuration — optimal index settings based on literature.

- [get_collection_config, line 75](../backend/app/trials/qdrant_config.py#L75): Return the optimal Qdrant collection configuration.

### `backend/app/trials/qdrant_service.py`
Qdrant vector database service for clinical trial embeddings.

- [get_embedding_model, line 30](../backend/app/trials/qdrant_service.py#L30): Load and return the singleton SentenceTransformer model.
- [get_qdrant_client, line 48](../backend/app/trials/qdrant_service.py#L48): Return the singleton AsyncQdrantClient.
- [QdrantService, line 65](../backend/app/trials/qdrant_service.py#L65): Manages the clinical_trials Qdrant collection and vector operations.
- [get_qdrant_service, line 201](../backend/app/trials/qdrant_service.py#L201): Return the singleton QdrantService instance.

### `backend/app/trials/router.py`
ClinicalTrials.gov sync router — REQ-05.

- [_run_sync, line 22](../backend/app/trials/router.py#L22): Execute the full ClinicalTrials.gov → Qdrant sync pipeline.
- [trigger_sync, line 57](../backend/app/trials/router.py#L57): Manually trigger a ClinicalTrials.gov → Qdrant synchronization.

### `backend/app/understanding/__init__.py`
Local transformer text understanding and grounded study evidence.


### `backend/app/understanding/analysis_service.py`
Hybrid term proposals, assertion disagreement review, and separate text tone.

- [span_context, line 11](../backend/app/understanding/analysis_service.py#L11)
- [analyze, line 29](../backend/app/understanding/analysis_service.py#L29)

### `backend/app/understanding/model_registry.py`
Reviewed public checkpoints. No remote Python code or mutable revisions.


### `backend/app/understanding/rag_service.py`
BM25 + dense RRF retrieval, cross-encoder reranking and quote-verified RAG.

- [tokens, line 18](../backend/app/understanding/rag_service.py#L18)
- [passages_from_trials, line 22](../backend/app/understanding/rag_service.py#L22)
- [bm25, line 61](../backend/app/understanding/rag_service.py#L61)
- [normalized, line 78](../backend/app/understanding/rag_service.py#L78)
- [answer, line 84](../backend/app/understanding/rag_service.py#L84)

### `backend/app/understanding/router.py`
Authenticated, opt-in local text understanding and source-grounded research.

- [AnalyzeRequest, line 23](../backend/app/understanding/router.py#L23)
- [EvidenceRequest, line 35](../backend/app/understanding/router.py#L35)
- [require_enabled, line 41](../backend/app/understanding/router.py#L41)
- [compute, line 46](../backend/app/understanding/router.py#L46)
- [model_status, line 57](../backend/app/understanding/router.py#L57)
- [analyze_note, line 76](../backend/app/understanding/router.py#L76)
- [answer_study_question, line 82](../backend/app/understanding/router.py#L82)

### `backend/app/understanding/runtime.py`
Lazy CPU-only transformer inference. Missing weights never become fake results.

- [ModelUnavailable, line 9](../backend/app/understanding/runtime.py#L9)
- [LocalTransformers, line 13](../backend/app/understanding/runtime.py#L13)
- [get_runtime, line 149](../backend/app/understanding/runtime.py#L149)

## Frontend files

Pages define routes; components render reusable controls; hooks manage browser state; lib contains API/auth helpers; types hold shared contracts. Test files are checks rather than application screens.

- [frontend/src/__tests__/apiClient.test.ts](../frontend/src/__tests__/apiClient.test.ts)
- [frontend/src/__tests__/ConsentToggle.test.tsx](../frontend/src/__tests__/ConsentToggle.test.tsx)
- [frontend/src/__tests__/EligibilityBreakdown.test.tsx](../frontend/src/__tests__/EligibilityBreakdown.test.tsx)
- [frontend/src/__tests__/EntityChip.test.tsx](../frontend/src/__tests__/EntityChip.test.tsx)
- [frontend/src/__tests__/InboxLifecycle.test.tsx](../frontend/src/__tests__/InboxLifecycle.test.tsx)
- [frontend/src/__tests__/ModelEvidence.test.tsx](../frontend/src/__tests__/ModelEvidence.test.tsx)
- [frontend/src/__tests__/PublicAccess.test.tsx](../frontend/src/__tests__/PublicAccess.test.tsx)
- [frontend/src/__tests__/ReferralButton.test.tsx](../frontend/src/__tests__/ReferralButton.test.tsx)
- [frontend/src/__tests__/ResearchPage.test.tsx](../frontend/src/__tests__/ResearchPage.test.tsx)
- [frontend/src/__tests__/ResultsOverview.test.tsx](../frontend/src/__tests__/ResultsOverview.test.tsx)
- [frontend/src/__tests__/SecurityPolicy.test.ts](../frontend/src/__tests__/SecurityPolicy.test.ts)
- [frontend/src/__tests__/SessionReview.test.tsx](../frontend/src/__tests__/SessionReview.test.tsx)
- [frontend/src/__tests__/useAudioCapture.test.ts](../frontend/src/__tests__/useAudioCapture.test.ts)
- [frontend/src/__tests__/useConsent.test.ts](../frontend/src/__tests__/useConsent.test.ts)
- [frontend/src/__tests__/VerificationPanel.test.tsx](../frontend/src/__tests__/VerificationPanel.test.tsx)
- [frontend/src/app/guide/page.tsx](../frontend/src/app/guide/page.tsx)
- [frontend/src/app/inbox/page.tsx](../frontend/src/app/inbox/page.tsx)
- [frontend/src/app/layout.tsx](../frontend/src/app/layout.tsx)
- [frontend/src/app/licenses/page.tsx](../frontend/src/app/licenses/page.tsx)
- [frontend/src/app/login/page.tsx](../frontend/src/app/login/page.tsx)
- [frontend/src/app/models/page.tsx](../frontend/src/app/models/page.tsx)
- [frontend/src/app/page.tsx](../frontend/src/app/page.tsx)
- [frontend/src/app/policies/page.tsx](../frontend/src/app/policies/page.tsx)
- [frontend/src/app/preview/page.tsx](../frontend/src/app/preview/page.tsx)
- [frontend/src/app/research/page.tsx](../frontend/src/app/research/page.tsx)
- [frontend/src/app/session/page.tsx](../frontend/src/app/session/page.tsx)
- [frontend/src/app/timeline/page.tsx](../frontend/src/app/timeline/page.tsx)
- [frontend/src/app/validation/page.tsx](../frontend/src/app/validation/page.tsx)
- [frontend/src/app/verify/page.tsx](../frontend/src/app/verify/page.tsx)
- [frontend/src/app/workspace/page.tsx](../frontend/src/app/workspace/page.tsx)
- [frontend/src/components/AdvancedModelEvidence.tsx](../frontend/src/components/AdvancedModelEvidence.tsx)
- [frontend/src/components/AudioRecorder/AudioRecorder.tsx](../frontend/src/components/AudioRecorder/AudioRecorder.tsx)
- [frontend/src/components/CaseBadge.tsx](../frontend/src/components/CaseBadge.tsx)
- [frontend/src/components/ConsentToggle/ConsentToggle.tsx](../frontend/src/components/ConsentToggle/ConsentToggle.tsx)
- [frontend/src/components/EligibilityBreakdown/EligibilityBreakdown.tsx](../frontend/src/components/EligibilityBreakdown/EligibilityBreakdown.tsx)
- [frontend/src/components/EntityChip/EntityChip.tsx](../frontend/src/components/EntityChip/EntityChip.tsx)
- [frontend/src/components/InboxDashboard/InboxDashboard.tsx](../frontend/src/components/InboxDashboard/InboxDashboard.tsx)
- [frontend/src/components/InboxDashboard/ResultsOverview.tsx](../frontend/src/components/InboxDashboard/ResultsOverview.tsx)
- [frontend/src/components/InboxDashboard/StudyComparisonChart.tsx](../frontend/src/components/InboxDashboard/StudyComparisonChart.tsx)
- [frontend/src/components/ModelEvidence.tsx](../frontend/src/components/ModelEvidence.tsx)
- [frontend/src/components/PatientIdentity/PatientIdentity.tsx](../frontend/src/components/PatientIdentity/PatientIdentity.tsx)
- [frontend/src/components/PortalBoundary.tsx](../frontend/src/components/PortalBoundary.tsx)
- [frontend/src/components/TimelinePanel/TimelinePanel.tsx](../frontend/src/components/TimelinePanel/TimelinePanel.tsx)
- [frontend/src/components/TranscriptHeatmap/TranscriptHeatmap.tsx](../frontend/src/components/TranscriptHeatmap/TranscriptHeatmap.tsx)
- [frontend/src/components/TrialTrustPanel/TrialTrustPanel.tsx](../frontend/src/components/TrialTrustPanel/TrialTrustPanel.tsx)
- [frontend/src/components/ui/ReferralButton.tsx](../frontend/src/components/ui/ReferralButton.tsx)
- [frontend/src/components/VerificationPanel/VerificationPanel.tsx](../frontend/src/components/VerificationPanel/VerificationPanel.tsx)
- [frontend/src/hooks/useAudioCapture.ts](../frontend/src/hooks/useAudioCapture.ts)
- [frontend/src/hooks/useConsent.ts](../frontend/src/hooks/useConsent.ts)
- [frontend/src/lib/apiClient.ts](../frontend/src/lib/apiClient.ts)
- [frontend/src/lib/auth.ts](../frontend/src/lib/auth.ts)
- [frontend/src/lib/evidence.ts](../frontend/src/lib/evidence.ts)
- [frontend/src/lib/passwordless.ts](../frontend/src/lib/passwordless.ts)
- [frontend/src/lib/patient.ts](../frontend/src/lib/patient.ts)
- [frontend/src/lib/session.ts](../frontend/src/lib/session.ts)
- [frontend/src/types/index.ts](../frontend/src/types/index.ts)

## Infrastructure and evaluation

- `docker-compose.yml`: local API, frontend and Qdrant services; named volumes preserve data.
- `deploy/compose.aws.yml`: optional hosted configuration; requires external account, TLS and security setup.
- `backend/evaluate_context.py`, `evaluate_broad.py`, `evaluate_final_scenarios.py`: distinct NLP development tests.
- `backend/evaluate_advanced.py`: actual pinned transformer task checks.
- `backend/evaluate_speech.py`: strict word-error evaluation on in-memory samples.
- `scripts/final_readiness.py`: evidence freshness and explicit owner acceptance gates.

A source map is a learning guide, not a claim that every line is clinically validated. Start with one fictional visit, follow its request and response through these files, and compare the matching tests.
