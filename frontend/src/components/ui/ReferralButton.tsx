'use client';

/**
 * ReferralButton — NEW FEATURE 5
 * One-click sponsor referral initiation from an inbox item.
 */

import { useState } from "react";
import { Send, CheckCircle2, AlertCircle } from "lucide-react";
import clsx from "clsx";
import { createReferral } from "@/lib/apiClient";
import type { TrialMatch } from "@/types";

interface ReferralButtonProps {
  inboxItemId: string;
  match: TrialMatch;
  sessionId: string;
}

export function ReferralButton({ inboxItemId, match, sessionId }: ReferralButtonProps) {
  const [state, setState] = useState<"idle" | "loading" | "sent" | "error">("idle");
  const [referralId, setReferralId] = useState<string>("");
  const canRefer = match.freshness?.recommended_action === "ROUTE_TO_COORDINATOR";

  const metCriteria = match.criterion_breakdown
    .filter((c) => c.verdict === "MET")
    .map((c) => c.criterion_text)
    .slice(0, 5);

  const handleReferral = async () => {
    if (!canRefer) return;
    setState("loading");
    try {
      const result = await createReferral({
        inbox_item_id: inboxItemId,
        nct_id: match.nct_id,
        session_id: sessionId,
        trial_title: match.title,
        met_criteria: metCriteria,
        patient_pseudo: "REDACTED",
      });
      setReferralId(result.referral_id);
      setState("sent");
    } catch {
      setState("error");
    }
  };

  if (state === "sent") {
    return (
      <div className="flex items-center gap-1.5 text-xs text-green-700 font-medium">
        <CheckCircle2 className="h-4 w-4" aria-hidden="true" />
        Referral logged ({referralId.slice(0, 8)}…)
      </div>
    );
  }

  if (!canRefer) {
    return <span className="text-xs text-amber-700">Referral unavailable until trial status is verified</span>;
  }

  return (
    <button
      onClick={handleReferral}
      disabled={state === "loading"}
      aria-busy={state === "loading"}
      aria-label={`Initiate referral for trial ${match.nct_id}: ${match.title}`}
      className={clsx(
        "flex items-center gap-1.5 rounded-lg border px-3 py-1.5 text-xs font-medium transition-colors",
        "focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-blue-500 focus-visible:ring-offset-1",
        state === "error"
          ? "border-red-200 bg-red-50 text-red-700"
          : "border-blue-200 bg-blue-50 text-blue-700 hover:bg-blue-100"
      )}
    >
      {state === "error" ? (
        <AlertCircle className="h-3.5 w-3.5" aria-hidden="true" />
      ) : (
        <Send className="h-3.5 w-3.5" aria-hidden="true" />
      )}
      {state === "loading" ? "Logging…" : state === "error" ? "Retry" : "Initiate Referral"}
    </button>
  );
}
