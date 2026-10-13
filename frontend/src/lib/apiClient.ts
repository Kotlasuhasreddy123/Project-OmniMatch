/**
 * Centralized API client for OmniMatch backend.
 * All fetch calls go through here — never use fetch() directly in components.
 */

import type {
  ClinicalEntity,
  ConsentRequest,
  ConsentResponse,
  EvidenceLedgerResponse,
  EvidenceSpan,
  InboxItem,
  InboxListResponse,
  LoginRequest,
  MatchSearchResponse,
  NLPExtractResponse,
  SessionCompleteResponse,
  TokenResponse,
  TranscriptionResponse,
} from "@/types";

const BASE_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

// ---------------------------------------------------------------------------
// Token management (httpOnly cookies preferred in production)
// ---------------------------------------------------------------------------

let _accessToken: string | null = null;

export function setToken(token: string): void {
  _accessToken = token;
  if (typeof window !== "undefined") {
    sessionStorage.setItem("omni_token", token);
  }
}

export function getToken(): string | null {
  if (_accessToken) return _accessToken;
  if (typeof window !== "undefined") {
    return sessionStorage.getItem("omni_token");
  }
  return null;
}

export function clearToken(): void {
  _accessToken = null;
  if (typeof window !== "undefined") {
    sessionStorage.removeItem("omni_token");
  }
}

// ---------------------------------------------------------------------------
// Core fetch wrapper
// ---------------------------------------------------------------------------

async function apiFetch<T>(
  path: string,
  options: RequestInit = {}
): Promise<T> {
  const token = getToken();
  const headers: Record<string, string> = {
    ...(options.headers as Record<string, string>),
  };

  if (token) {
    headers["Authorization"] = `Bearer ${token}`;
  }

  if (!headers["Content-Type"] && !(options.body instanceof FormData) && !(options.body instanceof Blob)) {
    headers["Content-Type"] = "application/json";
  }

  const res = await fetch(`${BASE_URL}${path}`, { ...options, headers });

  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: res.statusText }));
    throw new ApiError(res.status, err.detail ?? "Request failed");
  }

  if (res.status === 204) return undefined as T;
  return res.json() as Promise<T>;
}

export class ApiError extends Error {
  constructor(
    public status: number,
    message: string
  ) {
    super(message);
    this.name = "ApiError";
  }
}

// ---------------------------------------------------------------------------
// Auth
// ---------------------------------------------------------------------------

export async function login(credentials: LoginRequest): Promise<TokenResponse> {
  return apiFetch<TokenResponse>("/api/v1/auth/login", {
    method: "POST",
    body: JSON.stringify(credentials),
  });
}

// ---------------------------------------------------------------------------
// Consent
// ---------------------------------------------------------------------------

export async function logConsent(body: ConsentRequest): Promise<ConsentResponse> {
  return apiFetch<ConsentResponse>("/api/v1/consent", {
    method: "POST",
    body: JSON.stringify(body),
  });
}

// ---------------------------------------------------------------------------
// Audio transcription
// ---------------------------------------------------------------------------

export async function transcribeAudio(
  sessionId: string,
  audioBlob: Blob
): Promise<TranscriptionResponse> {
  return apiFetch<TranscriptionResponse>(`/api/v1/audio/transcribe?session_id=${encodeURIComponent(sessionId)}`, {
    method: "POST",
    headers: { "Content-Type": audioBlob.type || "audio/webm" },
    body: audioBlob,
  });
}

// ---------------------------------------------------------------------------
// NLP extraction
// ---------------------------------------------------------------------------

export async function extractEntities(
  transcription: string,
  sessionId: string
): Promise<NLPExtractResponse> {
  return apiFetch<NLPExtractResponse>("/api/v1/nlp/extract", {
    method: "POST",
    body: JSON.stringify({ transcription, session_id: sessionId }),
  });
}

// ---------------------------------------------------------------------------
// Trial matching
// ---------------------------------------------------------------------------

export async function searchTrials(
  approvedEntities: ClinicalEntity[],
  sessionId: string,
  evidenceSpans: EvidenceSpan[] = []
): Promise<MatchSearchResponse> {
  return apiFetch<MatchSearchResponse>("/api/v1/match/search", {
    method: "POST",
    body: JSON.stringify({
      approved_entities: approvedEntities,
      session_id: sessionId,
      evidence_spans: evidenceSpans,
    }),
  });
}

// ---------------------------------------------------------------------------
// Session completion
// ---------------------------------------------------------------------------

export async function completeSession(
  sessionId: string,
  approvedEntities: ClinicalEntity[],
  evidenceSpans: EvidenceSpan[] = []
): Promise<SessionCompleteResponse> {
  return apiFetch<SessionCompleteResponse>(
    `/api/v1/sessions/${sessionId}/complete`,
    {
      method: "POST",
      body: JSON.stringify({
        session_id: sessionId,
        approved_entities: approvedEntities,
        evidence_spans: evidenceSpans,
      }),
    }
  );
}

export async function recordEvidenceLedger(
  sessionId: string,
  approvedEntities: ClinicalEntity[],
  evidenceSpans: EvidenceSpan[]
): Promise<EvidenceLedgerResponse> {
  return apiFetch<EvidenceLedgerResponse>("/api/v1/evidence/ledger", {
    method: "POST",
    body: JSON.stringify({
      session_id: sessionId,
      approved_entities: approvedEntities,
      evidence_spans: evidenceSpans,
    }),
  });
}

// ---------------------------------------------------------------------------
// Inbox
// ---------------------------------------------------------------------------

export async function getInbox(): Promise<InboxListResponse> {
  return apiFetch<InboxListResponse>("/api/v1/inbox");
}

export async function getInboxItem(id: string): Promise<InboxItem> {
  return apiFetch<InboxItem>(`/api/v1/inbox/${id}`);
}

export async function markReviewed(id: string): Promise<void> {
  return apiFetch<void>(`/api/v1/inbox/${id}`, { method: "DELETE" });
}

// ---------------------------------------------------------------------------
// NEW FEATURE 5: Referral routing
// ---------------------------------------------------------------------------

export async function createReferral(
  body: import("@/types").ReferralRequest
): Promise<import("@/types").ReferralResponse> {
  return apiFetch<import("@/types").ReferralResponse>("/api/v1/referrals", {
    method: "POST",
    body: JSON.stringify(body),
  });
}

// ---------------------------------------------------------------------------
// NEW FEATURE 3: Patient timeline
// ---------------------------------------------------------------------------

export async function getPatientTimeline(
  patientPseudo: string
): Promise<import("@/types").PatientTimelineResponse> {
  return apiFetch<import("@/types").PatientTimelineResponse>(
    `/api/v1/timeline/${encodeURIComponent(patientPseudo)}`
  );
}
