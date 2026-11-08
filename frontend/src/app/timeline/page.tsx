'use client';

/**
 * Approved terms from fictional visits sharing a patient label.
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
  const firstSeen = new Date(entry.first_seen).toLocaleString();
  const lastSeen = new Date(entry.last_seen).toLocaleString();
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
            First recorded for this term: {firstSeen}
          </span>
          {isRecurring && (
            <span className="flex items-center gap-1">
              <Clock className="h-3 w-3" aria-hidden="true" />
              Most recently recorded: {lastSeen}
            </span>
          )}
          <span className="break-all text-gray-500">First session for this term: {entry.session_id}</span>
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

  useEffect(() => {
    const linkedPatient = new URLSearchParams(window.location.search).get("patient");
    const initial = linkedPatient ?? sessionStorage.getItem("omni_last_patient") ?? "";
    setQuery(initial);
    if (linkedPatient) {
      setLoading(true);
      getPatientTimeline(linkedPatient).then((result) => { setTimeline(result); setPatientPseudo(linkedPatient); })
        .catch((err) => setError(err instanceof Error ? err.message : "Could not load history. Sign in and try again."))
        .finally(() => setLoading(false));
    }
  }, []);

  const handleSearch = async () => {
    if (!query.trim()) return;
    setLoading(true);
    setError(null);
    setTimeline(null);
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
          See each visit and its approved terms under the same patient ID. A new symptom is first recorded in the visit where it was added, even if another visit happened earlier on the same day.
        </p>
      </div>

      {/* Search */}
      <div className="flex gap-3">
        <div className="flex-1">
          <label htmlFor="patient-search" className="block text-sm font-medium mb-1">Demo patient ID</label>
          <input
            id="patient-search"
            type="text"
            value={query}
            onChange={(e) => setQuery(e.target.value.toUpperCase())}
            onKeyDown={(e) => e.key === "Enter" && handleSearch()}
            placeholder="Use the label from the visit, for example DEMO-001"
            className="w-full rounded-lg border border-gray-300 px-4 py-2.5 text-sm focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-blue-500"
            aria-label="Demo patient ID search"
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
      <p className="text-sm text-gray-600">Enter this label on New Session before sending each visit. The session ID is different for every visit. Older inbox records were not linked to a patient, and we have kept them unchanged.</p>

      {error && <p role="alert" className="text-sm text-red-600">{error}</p>}

      {timeline && (
        <div className="space-y-6" aria-label={`Timeline for ${patientPseudo}`}>
          <h2 className="text-lg font-semibold">Approved history for {patientPseudo}</h2>
          <div className="rounded-xl border border-blue-200 bg-white p-4 space-y-2">
            <a href={`/session?patient=${encodeURIComponent(patientPseudo)}`} className="inline-block rounded bg-blue-600 px-4 py-2 text-sm text-white focus-visible:ring-2 focus-visible:ring-blue-500">Record follow-up or add a written update</a>
            <p className="text-sm text-gray-600">Use the same patient ID. On the review screen, select Load previous approved terms if you want to include relevant history, then approve it again. Earlier visits stay unchanged.</p>
          </div>
          <section aria-label="Visits in time order" className="space-y-3">
            <h2 className="font-semibold">Visits in time order ({timeline.visits?.length ?? 0})</h2>
            {(timeline.visits ?? []).map((visit, index) => <article key={visit.session_id} className="rounded-xl border bg-white p-4 space-y-1">
              <h3 className="font-semibold">Visit {index + 1} · {new Date(visit.created_at).toLocaleString()}</h3>
              <p className="text-sm">Approved terms: {visit.approved_terms.join(", ") || "None"}</p>
              <p className="text-sm text-gray-600">{visit.study_count} study suggestion{visit.study_count === 1 ? "" : "s"} · {visit.reviewed ? "Reviewed" : "Awaiting review"}{visit.archived ? " · Archived from inbox" : ""}</p>
              <p className="break-all text-xs text-gray-500">Session: {visit.session_id}</p>
            </article>)}
          </section>
          {timeline.entries.length === 0 && <p role="status" className="rounded-lg border border-gray-200 bg-white p-4">No approved terms saved for this ID yet. Complete and send a visit using this exact label, then search again. Recording alone does not save a timeline entry.</p>}
          {/* Summary */}
          <div className="flex flex-wrap gap-4">
            <div className="rounded-xl border border-gray-200 bg-white px-5 py-4">
              <p className="text-2xl font-bold text-gray-900">{timeline.total_entities}</p>
              <p className="text-sm text-gray-500">Distinct approved terms</p>
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
          <p className="mt-3 text-base font-medium text-gray-600">Find a fictional patient using the label you entered for the visit</p>
          <p className="mt-1 text-sm text-gray-600">For example DEMO-001. Use the same label on a second visit to build a shared history.</p>
        </div>
      )}
    </div>
  );
}
