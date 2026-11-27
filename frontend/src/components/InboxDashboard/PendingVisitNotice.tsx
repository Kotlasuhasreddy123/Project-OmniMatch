"use client";
import { useEffect, useState } from "react";
import { completeSession } from "@/lib/apiClient";
import { getCurrentUser } from "@/lib/auth";
import type { ClinicalEntity, EvidenceSpan, InboxItem } from "@/types";

const PENDING_KEY = "omni_pending_visit";
const DELIVERY_TARGET_MS = 60_000;
interface PendingVisit {
  sessionId: string;
  patientLabel: string;
  submittedAt: number;
  ownerId?: string;
  approvedEntities?: ClinicalEntity[];
  evidenceSpans?: EvidenceSpan[];
}

export function PendingVisitNotice({ items, onRefresh }: { items: InboxItem[]; onRefresh: () => Promise<void> }) {
  const [pending, setPending] = useState<PendingVisit | null>(null);
  const [now, setNow] = useState(Date.now());
  const [retrying, setRetrying] = useState(false);
  const [error, setError] = useState<string | null>(null);
  useEffect(() => {
    try {
      const saved = JSON.parse(sessionStorage.getItem(PENDING_KEY) || "null") as PendingVisit | null;
      if (!saved) { setPending(null); return; }
      if (typeof saved.sessionId !== "string" || typeof saved.patientLabel !== "string" || !Number.isFinite(saved.submittedAt)
          || (saved.ownerId && saved.ownerId !== getCurrentUser()?.sub)) {
        sessionStorage.removeItem(PENDING_KEY); setPending(null); return;
      }
      if (items.some(item => item.session_id === saved.sessionId)) {
        sessionStorage.removeItem(PENDING_KEY); setPending(null); return;
      }
      setPending(saved);
    } catch { sessionStorage.removeItem(PENDING_KEY); setPending(null); }
  }, [items]);
  useEffect(() => {
    if (!pending) return;
    const timer = setInterval(() => setNow(Date.now()), 5_000);
    return () => clearInterval(timer);
  }, [pending]);
  if (!pending) return null;
  const delayed = now - pending.submittedAt >= DELIVERY_TARGET_MS;
  const canRetry = Array.isArray(pending.approvedEntities) && pending.approvedEntities.length <= 100;
  async function retry() {
    if (!pending || !canRetry || retrying) return;
    setRetrying(true); setError(null);
    try {
      await completeSession(pending.sessionId, pending.approvedEntities!, pending.evidenceSpans || [], pending.patientLabel);
      const updated = { ...pending, submittedAt: Date.now() };
      sessionStorage.setItem(PENDING_KEY, JSON.stringify(updated));
      setPending(updated); setNow(Date.now());
      await onRefresh();
    } catch (err) { setError(err instanceof Error ? err.message : "Retry could not complete. Try again shortly."); }
    finally { setRetrying(false); }
  }
  return <section className={`mb-5 rounded-xl border p-5 ${delayed ? "border-amber-300 bg-amber-50" : "border-teal-200 bg-teal-50"}`}
    role={delayed ? "alert" : "status"} aria-live="polite">
    <h2 className="font-semibold">{delayed ? "Your visit results are taking longer than expected" : "Your checked visit is being processed"}</h2>
    <p className="mt-2 text-sm">Patient ID: {pending.patientLabel}. {delayed
      ? "The 60-second delivery target has passed. This does not mean that no studies were found. Refresh the inbox or retry the same checked visit."
      : "Study suggestions will appear here when processing finishes. This page checks for updates every 30 seconds."}</p>
    <div className="mt-3 flex flex-wrap gap-3">
      <button className="ui-button ui-button-small ui-button-secondary" onClick={() => void onRefresh()}>Refresh inbox</button>
      {delayed && canRetry && <button className="ui-button ui-button-small" disabled={retrying} onClick={() => void retry()}>
        {retrying ? "Retrying checked visit…" : "Retry checked visit"}</button>}
    </div>
    {error && <p className="mt-2 text-sm text-red-700">{error}</p>}
  </section>;
}
