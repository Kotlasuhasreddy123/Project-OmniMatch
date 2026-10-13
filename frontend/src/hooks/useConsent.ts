'use client';

/**
 * useConsent — manages consent state and backend audit logging.
 * Consent changes are always logged to the backend BEFORE any audio action.
 */

import { useCallback, useState } from "react";
import { logConsent } from "@/lib/apiClient";

interface UseConsentOptions {
  sessionId: string;
}

interface UseConsentReturn {
  consentGranted: boolean;
  toggleConsent: () => Promise<void>;
  isLogging: boolean;
  error: string | null;
}

export function useConsent({ sessionId }: UseConsentOptions): UseConsentReturn {
  const [consentGranted, setConsentGranted] = useState(false);
  const [isLogging, setIsLogging] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const toggleConsent = useCallback(async () => {
    setIsLogging(true);
    setError(null);

    const newState = !consentGranted;
    const action = newState ? "CONSENT_GRANTED" : "CONSENT_REVOKED";

    try {
      await logConsent({
        session_id: sessionId,
        action,
        patient_pseudonym: "REDACTED",
      });
      // Only update local state AFTER successful audit log write
      setConsentGranted(newState);
    } catch (err) {
      const msg =
        err instanceof Error
          ? err.message
          : "Failed to log consent. Please try again.";
      setError(msg);
      // Do NOT toggle state if logging failed
    } finally {
      setIsLogging(false);
    }
  }, [consentGranted, sessionId]);

  return { consentGranted, toggleConsent, isLogging, error };
}
