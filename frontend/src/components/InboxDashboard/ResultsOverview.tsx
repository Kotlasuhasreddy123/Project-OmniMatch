"use client";
import { useState } from "react";
import dynamic from "next/dynamic";
import type { InboxItem } from "@/types";

const StudyComparisonChart = dynamic(() => import("./StudyComparisonChart"), {
  ssr: false,
  loading: () => <p role="status">Loading study comparison…</p>,
});

export function ResultsOverview({
  items,
  description = "Calculated from the visits in this view. Open a visit in the inbox to inspect its supporting evidence.",
}: {
  items: InboxItem[];
  description?: string;
}) {
  const [order, setOrder] = useState("score");
  const matches = items.flatMap((item) =>
    item.matches.map((match) => ({ ...match, visit: item.session_id })),
  );
  const rules = matches.flatMap((match) => match.criterion_breakdown || []);
  const groups = [
    { label: "Supporting evidence", verdict: "MET", color: "#087f70" },
    { label: "Conflicting evidence", verdict: "NOT_MET", color: "#c03651" },
    { label: "Information missing", verdict: "MISSING", color: "#a06408" },
    { label: "Needs verification", verdict: "UNKNOWN", color: "#5865b9" },
  ];
  const ranked = [...matches]
    .sort((a, b) =>
      order === "score"
        ? b.enrollment_readiness_score - a.enrollment_readiness_score
        : a.title.localeCompare(b.title),
    )
    .slice(0, 6);
  return (
    <section
      className="results-overview"
      aria-label="Visual summary of filtered results"
    >
      <div className="overview-heading">
        <div>
          <p className="eyebrow">THE REVIEW AT A GLANCE</p>
          <h2>
            See the signal.
            <br />
            Know what to check.
          </h2>
        </div>
        <p>{description}</p>
      </div>
      <div className="metric-grid">
        {[
          [items.length, "Visits in view"],
          [matches.length, "Study suggestions"],
          [
            items.filter((i) => i.status === "unread").length,
            "Awaiting review",
          ],
          [
            rules.filter(
              (r) => r.verdict === "MISSING" || r.verdict === "UNKNOWN",
            ).length,
            "Checks to resolve",
          ],
        ].map(([value, label]) => (
          <div className="metric" key={label}>
            <strong>{value}</strong>
            <span>{label}</span>
          </div>
        ))}
      </div>
      {ranked.length > 0 && (
        <div className="visual-card mt-4">
          <h3>Compare the review scores</h3>
          <p>
            Use the chart to compare ranking values. Hover or use keyboard
            navigation for details; the full numerical list appears below.
            Repeated studies belong to separate visits.
          </p>
          <StudyComparisonChart
            data={ranked.map((m, index) => ({
              name: `${index + 1}. ${m.nct_id}`,
              score: Math.max(
                0,
                Math.min(100, m.enrollment_readiness_score || 0),
              ),
            }))}
          />
        </div>
      )}
      <div className="visual-grid">
        <div className="visual-card">
          <h3>Evidence coverage</h3>
          <p>
            Criterion checks across suggestions in view. Repeated criteria are
            counted per suggestion.
          </p>
          <div className="coverage-bar" aria-hidden="true">
            {groups.map((g) => (
              <span
                key={g.verdict}
                style={{
                  background: g.color,
                  width: `${rules.length ? (rules.filter((r) => r.verdict === g.verdict).length / rules.length) * 100 : 0}%`,
                }}
              />
            ))}
          </div>
          <dl>
            {groups.map((g) => (
              <div className="legend-row" key={g.verdict}>
                <dt>
                  <i style={{ background: g.color }} />
                  {g.label}
                </dt>
                <dd>{rules.filter((r) => r.verdict === g.verdict).length}</dd>
              </div>
            ))}
          </dl>
          {!rules.length && (
            <p>
              No criterion data yet. Complete a visit to populate this chart.
            </p>
          )}
        </div>
        <div className="visual-card">
          <div className="flex flex-wrap justify-between gap-3">
            <h3>Study comparison</h3>
            <label className="text-sm">
              Order by{" "}
              <select
                className="rounded border p-2"
                value={order}
                onChange={(e) => setOrder(e.target.value)}
              >
                <option value="score">Review score</option>
                <option value="title">Study title</option>
              </select>
            </label>
          </div>
          <p>
            Up to six suggestions. Scores rank results; they do not measure
            accuracy or chance of enrollment.
          </p>
          {ranked.map((m, index) => (
            <div className="ranking-row" key={`${m.nct_id}-${index}`}>
              <div>
                <span>{m.conditions.join(", ") || m.title}</span>
                <small>
                  {m.visit} · {m.nct_id}
                </small>
              </div>
              <div className="ranking-track">
                <span
                  style={{
                    width: `${Math.max(0, Math.min(100, m.enrollment_readiness_score || 0))}%`,
                  }}
                />
              </div>
              <strong>
                {Math.round(m.enrollment_readiness_score || 0)}
                <small>/100</small>
              </strong>
            </div>
          ))}
          {!ranked.length && (
            <p>
              No suggestions in this selection. Check the approved information
              and study catalog coverage.
            </p>
          )}
        </div>
      </div>
    </section>
  );
}
