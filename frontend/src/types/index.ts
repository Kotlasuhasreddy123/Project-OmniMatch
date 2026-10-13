/** Shared TypeScript types for OmniMatch frontend. */

// ---------------------------------------------------------------------------
// Enums
// ---------------------------------------------------------------------------

export type UserRole = "ADMIN" | "CLINICAL_STAFF";
export type ConsentAction = "CONSENT_GRANTED" | "CONSENT_REVOKED";
export type EntityType = "DISEASE" | "SYMPTOM" | "MEDICATION" | "PROCEDURE" | "LAB_VALUE";
export type EntityStatus = "pending" | "approved" | "rejected";
export type InboxStatus = "unread" | "reviewed";
export type CriterionVerdict = "MET" | "NOT_MET" | "MISSING" | "UNKNOWN";

// ---------------------------------------------------------------------------
// Auth
// ---------------------------------------------------------------------------

export interface LoginRequest { username: string; password: string; }
export interface TokenResponse { access_token: string; token_type: string; expires_in_seconds: number; }

// ---------------------------------------------------------------------------
// Consent
// ---------------------------------------------------------------------------

export interface ConsentRequest { session_id: string; action: ConsentAction; patient_pseudonym?: string; }
export interface ConsentResponse { logged: boolean; audit_id: string; timestamp: string; }

// ---------------------------------------------------------------------------
// Transcription — NEW: word_confidences for heatmap (Feature 6)
// ---------------------------------------------------------------------------

export interface WordConfidence { word: string; confidence: number; start_time?: number; }

export interface TranscriptionResponse {
  transcription: string;
  duration_seconds: number;
  language: string;
  session_id: string;
  word_confidences: WordConfidence[];
}

// ---------------------------------------------------------------------------
// NLP Entities
// ---------------------------------------------------------------------------

export interface ClinicalEntity {
  term: string;
  entity_type: EntityType;
  negated: boolean;
  context: "patient" | "family" | "hypothetical";
  confidence: number;
  status: EntityStatus;
}

// ---------------------------------------------------------------------------
// Renewed Feature 8: Evidence Ledger
// ---------------------------------------------------------------------------

export interface EvidenceSpan {
  entity_term: string;
  start_char: number;
  end_char: number;
  excerpt_sha256: string;
  confidence: number;
  human_verified: boolean;
}

export interface CriterionEvidence {
  criterion_text: string;
  entity_term: string;
  excerpt_sha256: string;
  start_char: number;
  end_char: number;
  human_verified: boolean;
}

export interface EvidenceLedgerResponse {
  ledger_id: string;
  session_id: string;
  verified_entity_count: number;
  event_hash: string;
  created_at: string;
}

export interface NLPExtractResponse {
  entities: ClinicalEntity[];
  session_id: string;
  affirmed_count: number;
  negated_count: number;
  family_context_count: number;
}

// ---------------------------------------------------------------------------
// Trial Matching — NEW: criterion_breakdown, enrollment_readiness_score,
//   nearest_site_miles, nearest_site_city (Features 1, 2, 4)
// ---------------------------------------------------------------------------

export interface CriterionResult {
  criterion_text: string;
  verdict: CriterionVerdict;
  matched_entity: string | null;
  confidence: number;
  is_inclusion: boolean;
  explanation: string;
}

export interface TrialMatch {
  nct_id: string;
  title: string;
  score: number;
  phase: string;
  status: string;
  brief_summary: string;
  conditions: string[];
  sponsor: string;
  missing_variables: string[];
  criterion_breakdown: CriterionResult[];
  enrollment_readiness_score: number;
  score_explanation: string;
  nearest_site_miles: number | null;
  nearest_site_city: string;
  locations: Record<string, string>[];
  criterion_evidence: CriterionEvidence[];
  freshness: TrialFreshness;
}

export interface TrialFreshness {
  level: "READY" | "REVIEW" | "BLOCKED";
  recommended_action: "ROUTE_TO_COORDINATOR" | "VERIFY_BEFORE_OUTREACH" | "DO_NOT_ROUTE";
  reason: string;
  registry_status: string;
  last_updated: string | null;
  age_days: number | null;
  site_data_available: boolean;
  evaluated_at: string;
}

export interface MatchSearchResponse {
  matches: TrialMatch[];
  session_id: string;
  query_entity_count: number;
  match_count: number;
}

// ---------------------------------------------------------------------------
// Inbox
// ---------------------------------------------------------------------------

export interface InboxItem {
  id: string;
  session_id: string;
  created_at: string;
  status: InboxStatus;
  matches: TrialMatch[];
  approved_entities: string[];
}

export interface InboxListResponse {
  items: InboxItem[];
  total: number;
  unread_count: number;
}

// ---------------------------------------------------------------------------
// Session
// ---------------------------------------------------------------------------

export interface SessionCompleteResponse {
  session_id: string;
  matching_triggered: boolean;
  message: string;
}

// ---------------------------------------------------------------------------
// NEW FEATURE 5: Referral
// ---------------------------------------------------------------------------

export interface ReferralRequest {
  inbox_item_id: string;
  nct_id: string;
  session_id: string;
  patient_pseudo?: string;
  trial_title: string;
  met_criteria?: string[];
  webhook_url?: string;
}

export interface ReferralResponse {
  referral_id: string;
  status: string;
  webhook_fired: boolean;
}

// ---------------------------------------------------------------------------
// NEW FEATURE 3: Timeline
// ---------------------------------------------------------------------------

export interface TimelineEntry {
  entity_term: string;
  entity_type: string;
  confidence: number;
  first_seen: string;
  last_seen: string;
  mention_count: number;
  session_id: string;
}

export interface PatientTimelineResponse {
  patient_pseudo: string;
  entries: TimelineEntry[];
  total_entities: number;
  unlock_events: Record<string, string>[];
}

