import Link from "next/link";
import { ResultsOverview } from "@/components/InboxDashboard/ResultsOverview";
import type { InboxItem, TrialMatch } from "@/types";

// Deliberately invented display fixtures. Never inserted into the inbox or used as clinical rules.
function study(
  id: string,
  condition: string,
  score: number,
  missing: boolean,
): TrialMatch {
  return {
    nct_id: id,
    title: `Sample ${condition} research review`,
    score: 0.6,
    phase: "Not applicable",
    status: "SIMULATED",
    brief_summary: "Illustrative display fixture",
    conditions: [condition],
    sponsor: "Classroom example",
    missing_variables: missing ? ["Measurement required"] : [],
    criterion_breakdown: [
      {
        criterion_text: "Condition recorded",
        verdict: "MET",
        matched_entity: condition,
        confidence: 1,
        is_inclusion: true,
        explanation: "Invented display example",
      },
      {
        criterion_text: "Measurement recorded",
        verdict: missing ? "UNKNOWN" : "MET",
        matched_entity: null,
        confidence: 0,
        is_inclusion: true,
        explanation: "Invented display example",
      },
    ],
    enrollment_readiness_score: score,
    score_explanation: "Invented display value, not a clinical assessment",
    nearest_site_miles: null,
    nearest_site_city: "",
    locations: [],
    criterion_evidence: [],
    freshness: {
      level: "BLOCKED",
      recommended_action: "DO_NOT_ROUTE",
      reason: "Display fixture",
      registry_status: "SIMULATED",
      last_updated: null,
      age_days: null,
      site_data_available: false,
      evaluated_at: "2026-11-04T00:00:00Z",
    },
  };
}

const fixtures: InboxItem[] = [
  {
    id: "preview-1",
    session_id: "EXAMPLE-VISIT-1",
    created_at: "2026-11-04T10:00:00Z",
    status: "unread",
    approved_entities: ["asthma"],
    matches: [
      study("EXAMPLE-A", "Asthma", 72, true),
      study("EXAMPLE-B", "Asthma", 48, true),
    ],
  },
  {
    id: "preview-2",
    session_id: "EXAMPLE-VISIT-2",
    created_at: "2026-11-04T11:00:00Z",
    status: "reviewed",
    approved_entities: ["diabetes"],
    matches: [study("EXAMPLE-C", "Diabetes", 81, false)],
  },
];

export default function PreviewPage() {
  return (
    <article className="py-8">
      <p className="eyebrow">EXPLORE THE RESULTS WORKSPACE</p>
      <h1 className="mt-4 max-w-3xl text-4xl font-semibold tracking-tighter sm:text-6xl">
        Evidence you can see.
        <br />A review you can follow.
      </h1>
      <p className="mt-5 max-w-2xl leading-7 text-gray-600">
        These are invented display examples, including the scores. They
        demonstrate the layout and interactions and are separate from your saved
        inbox records.
      </p>
      <ResultsOverview
        items={fixtures}
        description="Illustrative totals from two invented visits. These display fixtures demonstrate the workspace and are separate from your inbox."
      />
      <div className="flex flex-wrap gap-4">
        <Link
          href="/session"
          className="rounded-full bg-teal-700 px-6 py-3 font-medium text-white"
        >
          Try a visit →
        </Link>
        <Link href="/inbox" className="rounded-full border px-6 py-3">
          Open my inbox
        </Link>
      </div>
    </article>
  );
}
