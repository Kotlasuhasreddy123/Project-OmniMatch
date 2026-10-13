'use client';

/**
 * Patient Timeline page — NEW FEATURE 3
 * Shows longitudinal entity history across all visits for a patient.
 * No existing ambient or trial-matching system offers this capability.
 */

import { useState, useEffect } from "react";
import { getPatientTimeline } from "@/lib/apiClient";
import type { PatientTimelineResponse, TimelineEntry } from "@/types";
import { Clock, Tag, TrendingUp, Search } from "lucide-react";
import clsx from "clsx";

const TYPE_COLORS: Record<string, string> = {
  DISEASE: "bg-purple-100 text-purple-800",
  SYMPTOM: "bg-orange-100 text-orange-800",
  MEDICATION: "bg-blue-100 text-blue-800",
  PROCEDURE: "bg-teal-100 text-teal-800",
  LAB_VALUE: "bg-yellow-100 text-yellow-800",
};

function TimelineEntryCard({ entry }: { entry: TimelineEntry }) {
  const typeColor = TYPE_COLORS[entry.entity_type] ?? "bg-gray-100 text-gray-600";
  const firstSeen = new Date(entry.first_seen).toLocaleDateString();
  const lastSeen = new Date(entry.last_seen).toLocaleDateString();
  const isRecurring = entry.mention_count > 1;

  return (
    <div
      className={clsx(
        "flex items-start gap-4 rounded-xl border p-4",
        isRecurring ? "border-blue-200 bg-blue-50" : "border-gray-200 bg-white"
      )}
      role="article"
      aria-label={`Entity: ${entry.entity_term}, mentioned ${entry.mention_count} time${entry.mention_count !== 1 ? "s" : ""}`}
    >
      <div className="flex flex-col items-center gap-1">
        <div className={clsx("rounded-full px-2 py-0.5 text-xs font-medium", typeColor)}>
          {entry.entity_type}
        </div>
        {isRecurring && (
          <div className="flex items-center gap-0.5 text-xs text-blue-600 font-medium">
            <TrendingUp className="h-3 w-3" aria-hidden="true" />
            ×{entry.mention_count}
          </div>
        )}
      </div>

      <div className="flex-1 min-w-0">
        <p className="text-sm font-semibold text-gray-900 capitalize">{entry.entity_term}</p>
        <div className="mt-1 flex flex-wrap gap-3 text-xs text-gray-500">
          <span className="flex items-center gap-1">
            <Clock className="h-3 w-3" aria-hidden="true" />
            First: {firstSeen}
          </span>
          {firstSeen !== lastSeen && (
            <span className="flex items-center gap-1">
              <Clock className="h-3 w-3" aria-hidden="true" />
              Last: {lastSeen}
            </span>
          )}
          <span className="text-gray-400">Session: {entry.session_id}</span>
        </div>
      </div>

      <div className="shrink-0">
        <div
          className="h-2 w-2 rounded-full"
          style={{
            backgroundColor: entry.confidence >= 0.8 ? "#22c55e" :
                             entry.confidence >= 0.6 ? "#f59e0b" : "#9ca3af"
          }}
          aria-label={`Confidence: ${Math.round(entry.confidence * 100)}%`}
          title={`Confidence: ${Math.round(entry.confidence * 100)}%`}
        />
      </div>
    </div>
  );
}

export default function TimelinePage() {
  const [patientPseudo, setPatientPseudo] = useState("");
  const [query, setQuery] = useState("");
  const [timeline, setTimeline] = useState<PatientTimelineResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSearch = async () => {
    if (!query.trim()) return;
    setLoading(true);
    setError(null);
    try {
      const result = await getPatientTimeline(query.trim());
      setTimeline(result);
      setPatientPseudo(query.trim());
    } catch (err) {
      setError(err instanceof Error ? err.message : "Could not load timeline.");
    } finally {
      setLoading(false);
    }
  };

  const groupedByType = timeline
    ? timeline.entries.reduce<Record<string, TimelineEntry[]>>((acc, e) => {
        const t = e.entity_type;
        if (!acc[t]) acc[t] = [];
        acc[t].push(e);
        return acc;
      }, {})
    : {};

  return (
    <div className="mx-auto max-w-4xl space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Patient Visit Timeline</h1>
        <p className="mt-1 text-sm text-gray-500">
          View cumulative clinical entities across all visit sessions for a patient.
          This longitudinal view is unique to OmniMatch — no single-session system provides this.
        </p>
      </div>

      {/* Search */}
      <div className="flex gap-3">
        <div className="flex-1">
          <label htmlFor="patient-search" className="sr-only">Patient pseudonym</label>
          <input
            id="patient-search"
            type="text"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && handleSearch()}
            placeholder="Enter patient pseudonym (e.g. REDACTED or session-derived ID)"
            className="w-full rounded-lg border border-gray-300 px-4 py-2.5 text-sm focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-blue-500"
            aria-label="Patient pseudonym search"
          />
        </div>
        <button
          onClick={handleSearch}
          disabled={loading || !query.trim()}
          aria-label="Search patient timeline"
          className="flex items-center gap-2 rounded-lg bg-blue-600 px-4 py-2.5 text-sm font-medium text-white hover:bg-blue-700 disabled:opacity-60 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-blue-500 transition-colors"
        >
          <Search className="h-4 w-4" aria-hidden="true" />
          {loading ? "Loading…" : "Search"}
        </button>
      </div>

      {error && <p role="alert" className="text-sm text-red-600">{error}</p>}

      {timeline && (
        <div className="space-y-6" aria-label={`Timeline for ${patientPseudo}`}>
          {/* Summary */}
          <div className="flex flex-wrap gap-4">
            <div className="rounded-xl border border-gray-200 bg-white px-5 py-4">
              <p className="text-2xl font-bold text-gray-900">{timeline.total_entities}</p>
              <p className="text-sm text-gray-500">Total unique entities</p>
            </div>
            <div className="rounded-xl border border-gray-200 bg-white px-5 py-4">
              <p className="text-2xl font-bold text-blue-600">
                {timeline.entries.filter((e) => e.mention_count > 1).length}
              </p>
              <p className="text-sm text-gray-500">Recurring across visits</p>
            </div>
            <div className="rounded-xl border border-gray-200 bg-white px-5 py-4">
              <p className="text-2xl font-bold text-purple-600">
                {Object.keys(groupedByType).length}
              </p>
              <p className="text-sm text-gray-500">Entity types found</p>
            </div>
          </div>

          {/* Grouped by type */}
          {Object.entries(groupedByType).map(([type, entries]) => (
            <section key={type} aria-labelledby={`type-${type}`}>
              <h2
                id={`type-${type}`}
                className="mb-3 flex items-center gap-2 text-sm font-semibold uppercase tracking-wider text-gray-500"
              >
                <Tag className="h-4 w-4" aria-hidden="true" />
                {type} ({entries.length})
              </h2>
              <div className="space-y-2" role="list" aria-label={`${type} entities`}>
                {entries.map((entry) => (
                  <div key={`${entry.entity_term}-${entry.first_seen}`} role="listitem">
                    <TimelineEntryCard entry={entry} />
                  </div>
                ))}
              </div>
            </section>
          ))}
        </div>
      )}

      {!timeline && !loading && (
        <div className="flex flex-col items-center justify-center rounded-xl border border-dashed border-gray-300 py-16 text-center">
          <Clock className="h-12 w-12 text-gray-300" aria-hidden="true" />
          <p className="mt-3 text-base font-medium text-gray-500">Enter a patient pseudonym to view their visit timeline</p>
          <p className="mt-1 text-sm text-gray-400">Entities accumulate across multiple sessions, unlocking richer trial matching over time.</p>
        </div>
      )}
    </div>
  );
}
