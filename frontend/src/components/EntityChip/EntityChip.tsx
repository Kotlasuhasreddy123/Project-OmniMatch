'use client';

/**
 * EntityChip — interactive approve/reject chip for clinical entities (REQ-04, REQ-09).
 *
 * WCAG 2.1 AA:
 * - Unique aria-labels on each approve/reject button
 * - Status communicated via icon + color (not color alone)
 * - Keyboard: Enter and Space activate buttons
 */

import { Check, X, AlertCircle } from "lucide-react";
import clsx from "clsx";
import type { ClinicalEntity, EntityStatus } from "@/types";

const ENTITY_TYPE_LABELS: Record<string, string> = {
  DISEASE: "Disease",
  SYMPTOM: "Symptom",
  MEDICATION: "Medication",
  PROCEDURE: "Procedure",
  LAB_VALUE: "Lab Value",
};

const ENTITY_TYPE_COLORS: Record<string, string> = {
  DISEASE: "bg-purple-100 text-purple-800 border-purple-200",
  SYMPTOM: "bg-orange-100 text-orange-800 border-orange-200",
  MEDICATION: "bg-blue-100 text-blue-800 border-blue-200",
  PROCEDURE: "bg-teal-100 text-teal-800 border-teal-200",
  LAB_VALUE: "bg-yellow-100 text-yellow-800 border-yellow-200",
};

interface EntityChipProps {
  entity: ClinicalEntity;
  onApprove: (term: string) => void;
  onReject: (term: string) => void;
}

export function EntityChip({ entity, onApprove, onReject }: EntityChipProps) {
  const { term, entity_type, negated, context, confidence, status } = entity;
  const isExcluded = negated || context !== "patient";
  const typeColor =
    ENTITY_TYPE_COLORS[entity_type] ?? "bg-gray-100 text-gray-700 border-gray-200";

  return (
    <div
      className={clsx(
        "flex flex-col gap-2 rounded-xl border p-3 transition-all",
        status === "approved" && "border-green-300 bg-green-50",
        status === "rejected" && "border-red-200 bg-red-50 opacity-60",
        status === "pending" && "border-gray-200 bg-white",
        isExcluded && "opacity-70"
      )}
      role="group"
      aria-label={`Clinical entity: ${term}. Type: ${ENTITY_TYPE_LABELS[entity_type] ?? entity_type}. Status: ${status}.`}
    >
      {/* Entity term + type badge */}
      <div className="flex items-start justify-between gap-2">
        <div className="flex flex-wrap items-center gap-2">
          <span
            className={clsx(
              "text-sm font-semibold",
              status === "rejected" && "line-through text-gray-500"
            )}
          >
            {term}
          </span>

          <span
            className={clsx(
              "rounded-full border px-2 py-0.5 text-xs font-medium",
              typeColor
            )}
            aria-label={`Entity type: ${ENTITY_TYPE_LABELS[entity_type] ?? entity_type}`}
          >
            {ENTITY_TYPE_LABELS[entity_type] ?? entity_type}
          </span>

          {/* Negation / family context badges */}
          {negated && (
            <span className="rounded-full bg-red-100 px-2 py-0.5 text-xs font-medium text-red-700">
              Negated
            </span>
          )}
          {context === "family" && (
            <span className="rounded-full bg-amber-100 px-2 py-0.5 text-xs font-medium text-amber-700">
              Family History
            </span>
          )}
          {context === "hypothetical" && (
            <span className="rounded-full bg-gray-100 px-2 py-0.5 text-xs font-medium text-gray-600">
              Hypothetical
            </span>
          )}
        </div>

        {/* Confidence */}
        <span className="shrink-0 text-xs text-gray-400">
          {Math.round(confidence * 100)}%
        </span>
      </div>

      {/* Exclusion notice */}
      {isExcluded && (
        <p className="flex items-center gap-1 text-xs text-amber-700">
          <AlertCircle className="h-3.5 w-3.5" aria-hidden="true" />
          {negated
            ? "Excluded from query (negated)"
            : "Excluded from query (not patient context)"}
        </p>
      )}

      {/* Approve / Reject buttons — only when not already excluded */}
      {!isExcluded && (
        <div className="flex gap-2">
          <button
            onClick={() => onApprove(term)}
            disabled={status === "approved"}
            aria-label={`Approve entity: ${term}`}
            aria-pressed={status === "approved"}
            className={clsx(
              "flex flex-1 items-center justify-center gap-1.5 rounded-lg border px-3 py-1.5 text-sm font-medium transition-all",
              "focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-green-500 focus-visible:ring-offset-1",
              status === "approved"
                ? "border-green-400 bg-green-500 text-white"
                : "border-green-200 bg-white text-green-700 hover:bg-green-50"
            )}
          >
            <Check className="h-4 w-4" aria-hidden="true" />
            Approve
          </button>

          <button
            onClick={() => onReject(term)}
            disabled={status === "rejected"}
            aria-label={`Reject entity: ${term}`}
            aria-pressed={status === "rejected"}
            className={clsx(
              "flex flex-1 items-center justify-center gap-1.5 rounded-lg border px-3 py-1.5 text-sm font-medium transition-all",
              "focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-red-500 focus-visible:ring-offset-1",
              status === "rejected"
                ? "border-red-400 bg-red-500 text-white"
                : "border-red-200 bg-white text-red-700 hover:bg-red-50"
            )}
          >
            <X className="h-4 w-4" aria-hidden="true" />
            Reject
          </button>
        </div>
      )}
    </div>
  );
}
