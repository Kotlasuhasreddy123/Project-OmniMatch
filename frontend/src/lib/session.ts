/** Visit session ID management — generates and persists session IDs. */

export function generateSessionId(): string {
  return `session-${Date.now()}-${Math.random().toString(36).slice(2, 9)}`;
}

export function getOrCreateSessionId(): string {
  if (typeof window === "undefined") return generateSessionId();
  const existing = sessionStorage.getItem("omni_session_id");
  if (existing) return existing;
  const newId = generateSessionId();
  sessionStorage.setItem("omni_session_id", newId);
  return newId;
}

export function clearSessionId(): void {
  if (typeof window !== "undefined") {
    sessionStorage.removeItem("omni_session_id");
  }
}
