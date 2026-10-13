'use client';

/**
 * TimelinePanel — compact longitudinal entity summary widget (NEW FEATURE 3).
 * Used as a sidebar panel on the Inbox page to show patient entity history.
 */

import { useEffect, useState } from "react";
import { Clock, TrendingUp } from "lucide-react";
import clsx from "clsx";
import { getPatientTimeline } from "@/lib/apiClient";
import type { PatientTimelineResponse } from "@/types";

interface TimelinePanelProps {
  patientPseudo: string;
}

const TYPE_DOT: Record<string, string> = {
  DISEASE: "bg-purple-500",
  SYMPTOM: "bg-orange-400",
  MEDICATION: "bg-blue-500",
  PROCEDURE: "bg-teal-500",
  LAB_VALUE: "bg-yellow-500",
};

export function TimelinePanel({ patientPseudo }: TimelinePanelProps) {
  const [data, setData] = useState<PatientTimelineResponse | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!patientPseudo) { setLoading(false); return; }
    getPatientTimeline(patientPseudo)
      .then(setData)
      .catch(() => setData(null))
      .finally(() => setLoading(false));
  }, [patientPseudo]);

  if (loading) {
    return (
      <div className="flex items-center gap-2 text-xs text-gray-400 py-4">
        <div className="h-4 w-4 animate-spin rounded-full border-2 border-blue-400 border-t-transparent" aria-hidden="true" />
        Loading patient history…
      </div>
    );
  }

  if (!data || data.entries.length === 0) {
    return (
      <p className="text-xs text-gray-400 italic py-2">
        No prior visit history for this patient.
      </p>
    );
  }

  const recurring = data.entries.filter((e) => e.mention_count > 1);
  const topEntries = data.entries.slice(0, 8);

  return (
    <div
      className="space-y-3"
      aria-label={`Patient visit timeline — ${data.total_entities} entities across visits`}
    >
      <div className="flex items-center justify-between">
        <p className="text-xs font-semibold uppercase tracking-wider text-gray-500">
          Patient History
        </p>
        {recurring.length > 0 && (
          <span className="flex items-center gap-1 text-xs text-blue-600 font-medium">
            <TrendingUp className="h-3 w-3" aria-hidden="true" />
            {recurring.length} recurring
          </span>
        )}
      </div>

      <ul aria-label="Prior visit entities" className="space-y-1.5">
        {topEntries.map((entry) => (
          <li
            key={`${entry.entity_term}-${entry.first_seen}`}
            className="flex items-center gap-2 text-xs"
          >
            <span
              className={clsx(
                "h-2 w-2 shrink-0 rounded-full",
                TYPE_DOT[entry.entity_type] ?? "bg-gray-400"
              )}
              aria-hidden="true"
            />
            <span className="flex-1 truncate capitalize font-medium text-gray-700">
              {entry.entity_term}
            </span>
            {entry.mention_count > 1 && (
              <span className="shrink-0 text-blue-500 font-semibold">×{entry.mention_count}</span>
            )}
            <span className="shrink-0 text-gray-400 flex items-center gap-0.5">
              <Clock className="h-2.5 w-2.5" aria-hidden="true" />
              {new Date(entry.first_seen).toLocaleDateString(undefined, { month: "short", day: "numeric" })}
            </span>
          </li>
        ))}
      </ul>

      {data.entries.length > 8 && (
        <a
          href="/timeline"
          className="text-xs text-blue-600 hover:underline focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-blue-500 rounded"
        >
          View full timeline (+{data.entries.length - 8} more)
        </a>
      )}
    </div>
  );
}
