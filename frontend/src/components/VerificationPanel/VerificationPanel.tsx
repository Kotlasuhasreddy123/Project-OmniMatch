'use client';

/**
 * VerificationPanel — Human-in-the-Loop entity review screen (REQ-04).
 * Staff must approve/reject every entity before the search query runs.
 */

import { useState, useCallback } from "react";
import { SendHorizonal } from "lucide-react";
import clsx from "clsx";
import { EntityChip } from "@/components/EntityChip/EntityChip";
import type { ClinicalEntity } from "@/types";

interface VerificationPanelProps {
  entities: ClinicalEntity[];
  sessionId: string;
  onSubmit: (approvedEntities: ClinicalEntity[]) => Promise<void>;
  isSubmitting?: boolean;
}

export function VerificationPanel({
  entities,
  sessionId,
  onSubmit,
  isSubmitting = false,
}: VerificationPanelProps) {
  const [localEntities, setLocalEntities] = useState<ClinicalEntity[]>(entities);

  const handleApprove = useCallback((term: string) => {
    setLocalEntities((prev) =>
      prev.map((e) => (e.term === term ? { ...e, status: "approved" } : e))
    );
  }, []);

  const handleReject = useCallback((term: string) => {
    setLocalEntities((prev) =>
      prev.map((e) => (e.term === term ? { ...e, status: "rejected" } : e))
    );
  }, []);

  const approvedCount = localEntities.filter(
    (e) => e.status === "approved" && !e.negated && e.context === "patient"
  ).length;

  const pendingCount = localEntities.filter(
    (e) => e.status === "pending" && !e.negated && e.context === "patient"
  ).length;

  const canSubmit = approvedCount > 0 && !isSubmitting;

  const handleSubmit = async () => {
    if (!canSubmit) return;
    await onSubmit(localEntities.filter((e) => e.status === "approved"));
  };

  const affirmedEntities = localEntities.filter(
    (e) => !e.negated && e.context === "patient"
  );
  const excludedEntities = localEntities.filter(
    (e) => e.negated || e.context !== "patient"
  );

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold text-gray-900">
          Medical Extraction Verification
        </h1>
        <p className="mt-1 text-sm text-gray-500">
          Session: <code className="text-xs">{sessionId}</code>
        </p>
        <p className="mt-2 text-sm text-gray-600">
          Review the AI-extracted clinical entities below. Approve entities to
          include them in the trial search query. Rejected terms are excluded
          from the database query.
        </p>
      </div>

      {/* Status summary */}
      <div
        className="flex flex-wrap gap-3"
        aria-live="polite"
        aria-atomic="true"
      >
        <span className="rounded-full bg-blue-100 px-3 py-1 text-sm font-medium text-blue-800">
          {localEntities.length} total entities
        </span>
        <span className="rounded-full bg-green-100 px-3 py-1 text-sm font-medium text-green-800">
          {approvedCount} approved
        </span>
        {pendingCount > 0 && (
          <span className="rounded-full bg-amber-100 px-3 py-1 text-sm font-medium text-amber-800">
            {pendingCount} pending review
          </span>
        )}
      </div>

      {/* Affirmed entities (can be approved/rejected) */}
      {affirmedEntities.length > 0 && (
        <section aria-labelledby="affirmed-heading">
          <h2 id="affirmed-heading" className="mb-3 text-base font-semibold text-gray-800">
            Patient Entities ({affirmedEntities.length})
          </h2>
          <div
            className="grid grid-cols-1 gap-3 sm:grid-cols-2 lg:grid-cols-3"
            role="list"
            aria-label="Clinical entities pending review"
          >
            {affirmedEntities.map((entity) => (
              <div key={entity.term} role="listitem">
                <EntityChip
                  entity={entity}
                  onApprove={handleApprove}
                  onReject={handleReject}
                />
              </div>
            ))}
          </div>
        </section>
      )}

      {/* Excluded entities (negated / family history — shown for transparency) */}
      {excludedEntities.length > 0 && (
        <section aria-labelledby="excluded-heading">
          <h2
            id="excluded-heading"
            className="mb-3 text-base font-semibold text-gray-500"
          >
            Automatically Excluded ({excludedEntities.length})
          </h2>
          <p className="mb-3 text-xs text-gray-400">
            These entities were detected but are excluded from the query due to
            negation or family/hypothetical context.
          </p>
          <div
            className="grid grid-cols-1 gap-3 sm:grid-cols-2 lg:grid-cols-3"
            role="list"
            aria-label="Automatically excluded entities"
          >
            {excludedEntities.map((entity) => (
              <div key={entity.term} role="listitem">
                <EntityChip
                  entity={entity}
                  onApprove={handleApprove}
                  onReject={handleReject}
                />
              </div>
            ))}
          </div>
        </section>
      )}

      {/* Submit button */}
      <div className="sticky bottom-4">
        <button
          onClick={handleSubmit}
          disabled={!canSubmit}
          aria-disabled={!canSubmit}
          aria-busy={isSubmitting}
          className={clsx(
            "flex w-full items-center justify-center gap-2 rounded-xl px-6 py-4 text-base font-semibold shadow-lg transition-all",
            "focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-blue-500 focus-visible:ring-offset-2",
            canSubmit
              ? "bg-blue-600 text-white hover:bg-blue-700 active:scale-[0.98]"
              : "cursor-not-allowed bg-gray-200 text-gray-400"
          )}
        >
          <SendHorizonal className="h-5 w-5" aria-hidden="true" />
          {isSubmitting
            ? "Running trial search…"
            : `Submit ${approvedCount} Approved ${approvedCount === 1 ? "Entity" : "Entities"} for Matching`}
        </button>
        {approvedCount === 0 && (
          <p
            role="status"
            className="mt-2 text-center text-xs text-amber-600"
          >
            Approve at least one entity to enable the trial search.
          </p>
        )}
      </div>
    </div>
  );
}
