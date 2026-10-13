/**
 * useConsent hook tests — consent state management and audit logging.
 */

import { renderHook, act } from "@testing-library/react";
import "@testing-library/jest-dom";
import { useConsent } from "@/hooks/useConsent";
import * as apiClient from "@/lib/apiClient";

jest.mock("@/lib/apiClient");
const mockLogConsent = apiClient.logConsent as jest.MockedFunction<typeof apiClient.logConsent>;

describe("useConsent hook", () => {
  beforeEach(() => jest.clearAllMocks());

  it("starts with consentGranted=false", () => {
    const { result } = renderHook(() => useConsent({ sessionId: "s1" }));
    expect(result.current.consentGranted).toBe(false);
  });

  it("calls logConsent with CONSENT_GRANTED when toggled on", async () => {
    mockLogConsent.mockResolvedValueOnce({
      logged: true, audit_id: "a1", timestamp: new Date().toISOString()
    });
    const { result } = renderHook(() => useConsent({ sessionId: "s1" }));
    await act(async () => { await result.current.toggleConsent(); });
    expect(mockLogConsent).toHaveBeenCalledWith(
      expect.objectContaining({ action: "CONSENT_GRANTED", session_id: "s1" })
    );
    expect(result.current.consentGranted).toBe(true);
  });

  it("calls logConsent with CONSENT_REVOKED when toggled off", async () => {
    mockLogConsent.mockResolvedValue({
      logged: true, audit_id: "a2", timestamp: new Date().toISOString()
    });
    const { result } = renderHook(() => useConsent({ sessionId: "s1" }));
    // First toggle ON
    await act(async () => { await result.current.toggleConsent(); });
    // Then toggle OFF
    await act(async () => { await result.current.toggleConsent(); });
    expect(mockLogConsent).toHaveBeenLastCalledWith(
      expect.objectContaining({ action: "CONSENT_REVOKED" })
    );
    expect(result.current.consentGranted).toBe(false);
  });

  it("does NOT toggle state if logConsent fails", async () => {
    mockLogConsent.mockRejectedValueOnce(new Error("Network error"));
    const { result } = renderHook(() => useConsent({ sessionId: "s1" }));
    await act(async () => { await result.current.toggleConsent(); });
    expect(result.current.consentGranted).toBe(false);
    expect(result.current.error).toBeTruthy();
  });

  it("sets isLogging=true during API call", async () => {
    let resolve: (v: any) => void;
    mockLogConsent.mockReturnValueOnce(
      new Promise(r => { resolve = r; })
    );
    const { result } = renderHook(() => useConsent({ sessionId: "s1" }));
    act(() => { result.current.toggleConsent(); });
    expect(result.current.isLogging).toBe(true);
    await act(async () => {
      resolve!({ logged: true, audit_id: "a3", timestamp: new Date().toISOString() });
    });
    expect(result.current.isLogging).toBe(false);
  });
});
