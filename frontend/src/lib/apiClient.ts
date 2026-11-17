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
  AdvancedModelStatus,
  NoteUnderstanding,
  StudyEvidenceAnswer,
} from "@/types";

const BASE_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

// ---------------------------------------------------------------------------
// Token management (httpOnly cookies preferred in production)
// ---------------------------------------------------------------------------

let _accessToken: string | null = null;

export function setToken(token: string): void {
  _accessToken = token;
  if (typeof window !== "undefined") {
    try {
      const claims = JSON.parse(atob(token.split(".")[1].replace(/-/g, "+").replace(/_/g, "/")));
      const previous = sessionStorage.getItem("omni_account_sub");
      if (claims.sub && previous !== claims.sub) {
        // Never carry a previous account's draft, consent or patient ID forward.
        Object.keys(sessionStorage).filter(key => key.startsWith("omni_")).forEach(key => sessionStorage.removeItem(key));
      }
      if (claims.sub) sessionStorage.setItem("omni_account_sub", claims.sub);
    } catch { /* API signature verification remains authoritative. */ }
    sessionStorage.setItem("omni_token", token);
    window.dispatchEvent(new Event("omni-auth-change"));
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
  const token = process.env.NEXT_PUBLIC_WORKOS_CLIENT_ID
    ? await (await import("./passwordless")).providerToken()
    : getToken();
  const headers: Record<string, string> = {
    ...(options.headers as Record<string, string>),
  };

  if (token) {
    headers["Authorization"] = `Bearer ${token}`;
  }

  if (!headers["Content-Type"] && !(options.body instanceof FormData) && !(options.body instanceof Blob)) {
    headers["Content-Type"] = "application/json";
  }

  const send = async () => {
    try {
      return await fetch(`${BASE_URL}${path}`, { ...options, headers });
    } catch {
      // Do not retry uncertain mutations after a connection failure.
      throw new ApiError(0, "The local service could not be reached. If Docker is starting, wait until the backend is healthy. Check the inbox before resending a visit; the request outcome is unknown.");
    }
  };
  let res = await send();
  if (res.status === 401 && process.env.NEXT_PUBLIC_WORKOS_CLIENT_ID) {
    // A rejected authentication check has not run the endpoint. Refresh once
    // to recover an expired token; never loop or retry a forbidden (403) action.
    try {
      const renewed = await (await import("./passwordless")).providerToken(true);
      headers.Authorization = `Bearer ${renewed}`;
    } catch {
      clearToken();
      throw new ApiError(401, "Your sign-in session ended. Open Access and sign in again. Keep this tab open to preserve your unsent note.");
    }
    res = await send();
    if (res.status === 401) {
      clearToken();
      throw new ApiError(401, "Your sign-in could not be verified. Open Access and sign in again. Keep this tab open to preserve your unsent note.");
    }
  }

  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: res.statusText }));
    throw new ApiError(res.status, typeof err.detail === 'string' ? err.detail :
      res.status === 422 ? 'Check the input values and try again.' : 'Request failed');
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

export function getAdvancedModelStatus(): Promise<AdvancedModelStatus> {
  return apiFetch('/api/v1/understanding/status');
}
export function analyzeNote(text: string): Promise<NoteUnderstanding> {
  return apiFetch('/api/v1/understanding/analyze', {
    method: 'POST', body: JSON.stringify({ text, synthetic_only: true }),
  });
}
export function askStudyEvidence(question: string, approvedEntities: ClinicalEntity[]): Promise<StudyEvidenceAnswer> {
  return apiFetch('/api/v1/understanding/answer', {
    method: 'POST', body: JSON.stringify({ question, synthetic_only: true,
      approved_entities: approvedEntities.filter(entity => entity.status === 'approved' && entity.context === 'patient' && !entity.negated) }),
  });
}

// ---------------------------------------------------------------------------
// Auth
// ---------------------------------------------------------------------------

export async function login(credentials: LoginRequest): Promise<TokenResponse> {
  void credentials;
  throw new ApiError(410, "Password sign-in was removed. Use approved email-code access.");
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
  evidenceSpans: EvidenceSpan[] = [],
  patientPseudo?: string
): Promise<SessionCompleteResponse> {
  return apiFetch<SessionCompleteResponse>(
    `/api/v1/sessions/${sessionId}/complete`,
    {
      method: "POST",
      body: JSON.stringify({
        session_id: sessionId,
        approved_entities: approvedEntities,
        evidence_spans: evidenceSpans,
        patient_pseudo: patientPseudo,
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

export async function getInbox(includeArchived = false): Promise<InboxListResponse> {
  return apiFetch<InboxListResponse>(`/api/v1/inbox?include_archived=${includeArchived}`);
}

export async function archiveInboxItem(id: string, restore = false): Promise<void> {
  return apiFetch<void>(`/api/v1/inbox/${encodeURIComponent(id)}/${restore ? 'restore' : 'archive'}`, { method: 'POST' });
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
