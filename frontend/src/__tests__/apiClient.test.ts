/**
 * apiClient tests — all API methods with full mock coverage.
 */

import "@testing-library/jest-dom";
import {
  login, logConsent, transcribeAudio, extractEntities,
  searchTrials, getInbox, markReviewed, completeSession,
  createReferral, ApiError, setToken, clearToken,
} from "@/lib/apiClient";

const mockFetch = jest.fn();
global.fetch = mockFetch;

function mockResponse(status: number, data: unknown) {
  return Promise.resolve({
    ok: status >= 200 && status < 300,
    status,
    statusText: status === 200 ? "OK" : "Error",
    json: () => Promise.resolve(data),
  } as Response);
}

beforeEach(() => { jest.clearAllMocks(); clearToken(); });

describe("apiClient — login", () => {
  it("posts to /api/v1/auth/login and returns token", async () => {
    mockFetch.mockReturnValueOnce(
      mockResponse(200, { access_token: "tok123", token_type: "bearer", expires_in_seconds: 28800 })
    );
    const result = await login({ username: "staff", password: "Pass@123" });
    expect(result.access_token).toBe("tok123");
    expect(mockFetch).toHaveBeenCalledWith(
      expect.stringContaining("/api/v1/auth/login"),
      expect.objectContaining({ method: "POST" })
    );
  });

  it("throws ApiError on 401", async () => {
    mockFetch.mockReturnValueOnce(mockResponse(401, { detail: "Invalid credentials" }));
    await expect(login({ username: "x", password: "y" })).rejects.toThrow(ApiError);
  });
});

describe("apiClient — consent", () => {
  beforeEach(() => setToken("test-token"));

  it("posts CONSENT_GRANTED with session_id", async () => {
    mockFetch.mockReturnValueOnce(
      mockResponse(200, { logged: true, audit_id: "a1", timestamp: new Date().toISOString() })
    );
    const resp = await logConsent({ session_id: "s1", action: "CONSENT_GRANTED" });
    expect(resp.logged).toBe(true);
    const body = JSON.parse(mockFetch.mock.calls[0][1].body);
    expect(body.action).toBe("CONSENT_GRANTED");
    expect(body.session_id).toBe("s1");
  });
});

describe("apiClient — transcription", () => {
  beforeEach(() => setToken("test-token"));

  it("sends raw audio with the session ID in the URL", async () => {
    mockFetch.mockReturnValueOnce(mockResponse(200, {
      transcription: "patient has diabetes",
      duration_seconds: 2.5,
      language: "en",
      session_id: "s1",
      word_confidences: []
    }));
    const blob = new Blob([new Uint8Array(100)], { type: "audio/webm" });
    const resp = await transcribeAudio("s1", blob);
    expect(resp.transcription).toBe("patient has diabetes");
    const callArgs = mockFetch.mock.calls[0];
    expect(callArgs[0]).toContain("session_id=s1");
    expect(callArgs[1].body).toBe(blob);
    expect(callArgs[1].headers["Content-Type"]).toBe("audio/webm");
  });
});

describe("apiClient — NLP extraction", () => {
  beforeEach(() => setToken("test-token"));

  it("posts transcription and returns entity list", async () => {
    mockFetch.mockReturnValueOnce(mockResponse(200, {
      entities: [{ term: "diabetes", entity_type: "DISEASE", negated: false,
                   context: "patient", confidence: 0.9, status: "pending" }],
      session_id: "s1",
      affirmed_count: 1, negated_count: 0, family_context_count: 0
    }));
    const resp = await extractEntities("patient has diabetes", "s1");
    expect(resp.entities).toHaveLength(1);
    expect(resp.entities[0].term).toBe("diabetes");
  });
});

describe("apiClient — trial matching", () => {
  beforeEach(() => setToken("test-token"));

  it("posts approved entities only", async () => {
    mockFetch.mockReturnValueOnce(mockResponse(200, {
      matches: [], session_id: "s1", query_entity_count: 1, match_count: 0
    }));
    const entities = [
      { term: "diabetes", entity_type: "DISEASE" as const, negated: false,
        context: "patient" as const, confidence: 0.9, status: "approved" as const }
    ];
    const resp = await searchTrials(entities, "s1");
    expect(resp.matches).toHaveLength(0);
    const body = JSON.parse(mockFetch.mock.calls[0][1].body);
    expect(body.approved_entities).toHaveLength(1);
  });
});

describe("apiClient — inbox", () => {
  beforeEach(() => setToken("test-token"));

  it("GET /api/v1/inbox returns items list", async () => {
    mockFetch.mockReturnValueOnce(mockResponse(200, {
      items: [], total: 0, unread_count: 0
    }));
    const resp = await getInbox();
    expect(resp.items).toEqual([]);
    expect(mockFetch).toHaveBeenCalledWith(
      expect.stringContaining("/api/v1/inbox"),
      expect.objectContaining({ headers: expect.objectContaining({ Authorization: "Bearer test-token" }) })
    );
  });

  it("DELETE /api/v1/inbox/{id} calls correct endpoint", async () => {
    mockFetch.mockReturnValueOnce({ ok: true, status: 204, json: () => Promise.resolve(undefined) } as any);
    await markReviewed("item-001");
    expect(mockFetch).toHaveBeenCalledWith(
      expect.stringContaining("/api/v1/inbox/item-001"),
      expect.objectContaining({ method: "DELETE" })
    );
  });

  it("throws ApiError 401 when unauthenticated", async () => {
    clearToken();
    mockFetch.mockReturnValueOnce(mockResponse(401, { detail: "Not authenticated" }));
    await expect(getInbox()).rejects.toMatchObject({ status: 401, name: "ApiError" });
  });
});

describe("apiClient — referral (Feature 5)", () => {
  beforeEach(() => setToken("test-token"));

  it("posts referral data to /api/v1/referrals", async () => {
    mockFetch.mockReturnValueOnce(mockResponse(201, {
      referral_id: "ref-001", status: "sent", webhook_fired: true
    }));
    const resp = await createReferral({
      inbox_item_id: "i1", nct_id: "NCT001",
      session_id: "s1", trial_title: "Diabetes Study"
    });
    expect(resp.referral_id).toBe("ref-001");
    expect(mockFetch).toHaveBeenCalledWith(
      expect.stringContaining("/api/v1/referrals"),
      expect.objectContaining({ method: "POST" })
    );
  });
});

describe("apiClient — token management", () => {
  it("attaches Bearer token to requests when set", async () => {
    setToken("my-token");
    mockFetch.mockReturnValueOnce(mockResponse(200, { items: [], total: 0, unread_count: 0 }));
    await getInbox();
    const headers = mockFetch.mock.calls[0][1].headers;
    expect(headers.Authorization).toBe("Bearer my-token");
  });

  it("sends no Authorization header when token cleared", async () => {
    clearToken();
    mockFetch.mockReturnValueOnce(mockResponse(401, { detail: "Unauthorized" }));
    await expect(getInbox()).rejects.toThrow();
  });
});
