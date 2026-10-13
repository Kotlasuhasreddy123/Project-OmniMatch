'use client';

/**
 * EligibilityBreakdown — NEW FEATURE 1 & 2
 * Per-criterion verdict display + Enrollment Readiness Score.
 *
 * Research prototype display of preliminary criterion signals. Comparable
 * commercial and research systems also provide criterion-level explanations.
 */

import { useState } from "react";
import { CheckCircle2, XCircle, HelpCircle, AlertCircle, ChevronDown, ChevronUp, type LucideIcon } from "lucide-react";
import clsx from "clsx";

export type CriterionVerdict = "MET" | "NOT_MET" | "MISSING" | "UNKNOWN";

interface CriterionResult {
  criterion_text: string;
  verdict: CriterionVerdict;
  matched_entity: string | null;
  confidence: number;
  is_inclusion: boolean;
  explanation: string;
}

interface EligibilityBreakdownProps {
  criterionBreakdown: CriterionResult[];
  enrollmentReadinessScore: number;
  scoreExplanation: string;
  nctId: string;
}

const VERDICT_CONFIG: Record<
  CriterionVerdict,
  { label: string; color: string; icon: LucideIcon }
> = {
  MET: {
    label: "Met",
    color: "text-green-700 bg-green-50 border-green-200",
    icon: CheckCircle2,
  },
  NOT_MET: {
    label: "Not Met",
    color: "text-red-700 bg-red-50 border-red-200",
    icon: XCircle,
  },
  MISSING: {
    label: "Missing",
    color: "text-amber-700 bg-amber-50 border-amber-200",
    icon: AlertCircle,
  },
  UNKNOWN: {
    label: "Unknown",
    color: "text-gray-500 bg-gray-50 border-gray-200",
    icon: HelpCircle,
  },
};

function ScoreBadge({ score }: { score: number }) {
  const color =
    score >= 70
      ? "bg-green-500"
      : score >= 45
      ? "bg-amber-500"
      : "bg-red-400";

  return (
    <div className="flex items-center gap-3" aria-label={`Enrollment readiness score: ${score}%`}>
      <div className="relative h-14 w-14">
        <svg className="h-14 w-14 -rotate-90" viewBox="0 0 36 36" aria-hidden="true">
          <circle cx="18" cy="18" r="15.9" fill="none" stroke="#e5e7eb" strokeWidth="3" />
          <circle
            cx="18" cy="18" r="15.9" fill="none"
            stroke={score >= 70 ? "#22c55e" : score >= 45 ? "#f59e0b" : "#f87171"}
            strokeWidth="3"
            strokeDasharray={`${score} 100`}
            strokeLinecap="round"
          />
        </svg>
        <span className="absolute inset-0 flex items-center justify-center text-sm font-bold text-gray-800">
          {Math.round(score)}%
        </span>
      </div>
      <div>
        <p className="text-sm font-semibold text-gray-700">Enrollment Readiness</p>
        <p className="text-xs text-gray-400">Composite eligibility score</p>
      </div>
    </div>
  );
}

export function EligibilityBreakdown({
  criterionBreakdown,
  enrollmentReadinessScore,
  scoreExplanation,
  nctId,
}: EligibilityBreakdownProps) {
  const [showAll, setShowAll] = useState(false);

  const inclusion = criterionBreakdown.filter((c) => c.is_inclusion);
  const exclusion = criterionBreakdown.filter((c) => !c.is_inclusion);
  const displayedInclusion = showAll ? inclusion : inclusion.slice(0, 5);

  if (criterionBreakdown.length === 0) return null;

  return (
    <div
      role="region"
      className="space-y-4 rounded-xl border border-gray-100 bg-gray-50 p-4"
      aria-label={`Eligibility breakdown for trial ${nctId}`}
    >
      {/* Score */}
      <ScoreBadge score={enrollmentReadinessScore} />

      {scoreExplanation && (
        <p className="text-xs text-gray-400 font-mono">{scoreExplanation}</p>
      )}

      {/* Inclusion criteria */}
      {inclusion.length > 0 && (
        <div>
          <h4 className="mb-2 text-xs font-semibold uppercase tracking-wider text-gray-500">
            Inclusion Criteria ({inclusion.length})
          </h4>
          <ul aria-label="Inclusion criteria verdicts" className="space-y-1.5">
            {displayedInclusion.map((c, i) => {
              const cfg = VERDICT_CONFIG[c.verdict];
              const Icon = cfg.icon;
              return (
                <li
                  key={i}
                  className={clsx(
                    "flex items-start gap-2 rounded-lg border px-3 py-2 text-xs",
                    cfg.color
                  )}
                  aria-label={`${c.verdict}: ${c.criterion_text}`}
                >
                  <Icon className="mt-0.5 h-3.5 w-3.5 shrink-0" aria-hidden={true} />
                  <div className="min-w-0">
                    <p className="font-medium line-clamp-2">{c.criterion_text}</p>
                    {c.matched_entity && (
                      <p className="mt-0.5 text-xs opacity-75">
                        Matched: <em>{c.matched_entity}</em>
                      </p>
                    )}
                  </div>
                  <span className="ml-auto shrink-0 font-semibold">{cfg.label}</span>
                </li>
              );
            })}
          </ul>

          {inclusion.length > 5 && (
            <button
              onClick={() => setShowAll((p) => !p)}
              className="mt-2 flex items-center gap-1 text-xs text-blue-600 hover:underline focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-blue-500"
              aria-expanded={showAll}
            >
              {showAll ? (
                <><ChevronUp className="h-3 w-3" aria-hidden="true" /> Show less</>
              ) : (
                <><ChevronDown className="h-3 w-3" aria-hidden="true" /> Show {inclusion.length - 5} more</>
              )}
            </button>
          )}
        </div>
      )}

      {/* Exclusion criteria summary */}
      {exclusion.length > 0 && (
        <div>
          <h4 className="mb-2 text-xs font-semibold uppercase tracking-wider text-gray-500">
            Exclusion Criteria ({exclusion.length})
          </h4>
          <ul aria-label="Exclusion criteria verdicts" className="space-y-1.5">
            {exclusion.slice(0, 3).map((c, i) => {
              const cfg = VERDICT_CONFIG[c.verdict];
              const Icon = cfg.icon;
              return (
                <li
                  key={i}
                  className={clsx("flex items-start gap-2 rounded-lg border px-3 py-2 text-xs", cfg.color)}
                >
                  <Icon className="mt-0.5 h-3.5 w-3.5 shrink-0" aria-hidden={true} />
                  <p className="line-clamp-1">{c.criterion_text}</p>
                  <span className="ml-auto shrink-0 font-semibold">{cfg.label}</span>
                </li>
              );
            })}
          </ul>
        </div>
      )}
    </div>
  );
}
