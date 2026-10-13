'use client';

/**
 * Verify page — Human-in-the-Loop entity verification (REQ-04).
 * Staff approves/rejects entities, then submits to trigger async matching.
 */

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { VerificationPanel } from "@/components/VerificationPanel/VerificationPanel";
import { completeSession, recordEvidenceLedger } from "@/lib/apiClient";
import { buildEvidenceSpans } from "@/lib/evidence";
import { getOrCreateSessionId, clearSessionId } from "@/lib/session";
import type { ClinicalEntity } from "@/types";
import { AlertCircle } from "lucide-react";

export default function VerifyPage() {
  const router = useRouter();

  const [sessionId, setSessionId] = useState<string>("");
  const [entities, setEntities] = useState<ClinicalEntity[]>([]);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    // Only runs client-side — safe to use sessionStorage
    setSessionId(getOrCreateSessionId());
    const stored = sessionStorage.getItem("omni_entities");
    if (stored) {
      try {
        setEntities(JSON.parse(stored) as ClinicalEntity[]);
      } catch {
        setEntities([]);
      }
    }
  }, []);

  const handleSubmit = async (approvedEntities: ClinicalEntity[]) => {
    if (!sessionId) return;
    setIsSubmitting(true);
    setError(null);
    try {
      const transcript = sessionStorage.getItem("omni_transcription") ?? "";
      const evidenceSpans = await buildEvidenceSpans(transcript, approvedEntities);
      await recordEvidenceLedger(sessionId, approvedEntities, evidenceSpans);
      await completeSession(sessionId, approvedEntities, evidenceSpans);
      sessionStorage.removeItem("omni_entities");
      sessionStorage.removeItem("omni_transcription");
      clearSessionId();
      router.push("/inbox");
    } catch (err) {
      setError(
        err instanceof Error ? err.message : "Failed to submit. Please try again."
      );
    } finally {
      setIsSubmitting(false);
    }
  };

  // Show spinner while sessionId / entities are loading from sessionStorage
  if (!sessionId) {
    return (
      <div className="flex items-center justify-center py-16">
        <div className="h-8 w-8 animate-spin rounded-full border-4 border-blue-600 border-t-transparent" />
      </div>
    );
  }

  if (entities.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center py-16 gap-4">
        <AlertCircle className="h-12 w-12 text-amber-400" aria-hidden="true" />
        <p className="text-base font-medium text-gray-600">
          No entities to verify. Please complete a recording session first.
        </p>
        <a
          href="/session"
          className="text-sm text-blue-600 hover:underline focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-blue-500 rounded"
        >
          Start a new session
        </a>
      </div>
    );
  }

  return (
    <div className="mx-auto max-w-4xl">
      {error && (
        <div
          role="alert"
          className="mb-4 rounded-lg bg-red-50 border border-red-200 px-4 py-3 text-sm text-red-700"
        >
          {error}
        </div>
      )}
      <VerificationPanel
        entities={entities}
        sessionId={sessionId}
        onSubmit={handleSubmit}
        isSubmitting={isSubmitting}
      />
    </div>
  );
}
