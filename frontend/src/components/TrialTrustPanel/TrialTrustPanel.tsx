'use client';

import { CheckCircle2, CircleAlert, ShieldCheck, XCircle } from "lucide-react";
import clsx from "clsx";
import type { CriterionEvidence, TrialFreshness } from "@/types";

interface TrialTrustPanelProps {
  freshness: TrialFreshness;
  criterionEvidence: CriterionEvidence[];
}

const ICONS = {
  READY: CheckCircle2,
  REVIEW: CircleAlert,
  BLOCKED: XCircle,
};

export function TrialTrustPanel({ freshness, criterionEvidence }: TrialTrustPanelProps) {
  const Icon = ICONS[freshness.level] ?? CircleAlert;
  const color = freshness.level === "READY"
    ? "text-green-700 bg-green-50 border-green-200"
    : freshness.level === "BLOCKED"
      ? "text-red-700 bg-red-50 border-red-200"
      : "text-amber-800 bg-amber-50 border-amber-200";

  return (
    <section aria-label="Match trust and evidence" className="space-y-3">
      <div className={clsx("rounded-lg border p-3", color)}>
        <h4 className="flex items-center gap-1.5 text-xs font-semibold uppercase tracking-wider">
          <Icon className="h-4 w-4" aria-hidden="true" />
          Outreach Gate {freshness.level}
        </h4>
        <p className="mt-1 text-sm">{freshness.reason}</p>
        <p className="mt-1 text-xs">Recommended action: {freshness.recommended_action.replaceAll("_", " ")}</p>
      </div>

      <div>
        <h4 className="flex items-center gap-1.5 text-xs font-semibold uppercase tracking-wider text-gray-500">
          <ShieldCheck className="h-4 w-4" aria-hidden="true" />
          Human Verified Evidence
        </h4>
        {criterionEvidence.length === 0 ? (
          <p className="mt-1 text-sm text-gray-600">No approved transcript anchor was available for a matched criterion.</p>
        ) : (
          <ul className="mt-2 space-y-1" aria-label="Human verified criterion evidence">
            {criterionEvidence.map((evidence) => (
              <li key={`${evidence.criterion_text}-${evidence.excerpt_sha256}`} className="text-sm text-gray-700">
                <span className="font-medium">{evidence.entity_term}</span> supports {evidence.criterion_text}
                <span className="ml-1 text-xs text-green-700">verified</span>
              </li>
            ))}
          </ul>
        )}
      </div>
    </section>
  );
}
