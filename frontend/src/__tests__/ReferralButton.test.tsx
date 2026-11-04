import { render, screen } from "@testing-library/react";
import { ReferralButton } from "@/components/ui/ReferralButton";
import type { TrialMatch } from "@/types";

const simulatedMatch = {
  score: 0.7,
  phase: "Not applicable",
  status: "SIMULATED",
  brief_summary: "Synthetic test fixture",
  conditions: ["Type 2 diabetes"],
  sponsor: "Classroom",
  missing_variables: [],
  enrollment_readiness_score: 65,
  score_explanation: "Test ranking",
  nearest_site_miles: null,
  nearest_site_city: "",
  locations: [],
  criterion_evidence: [],
  nct_id: "DEMO-T2D-001",
  title: "SIMULATED Type 2 Diabetes Study",
  criterion_breakdown: [],
  freshness: {
    level: "BLOCKED",
    recommended_action: "DO_NOT_ROUTE",
    reason: "Simulated record",
    registry_status: "SIMULATED",
    last_updated: null,
    age_days: null,
    site_data_available: false,
    evaluated_at: "2026-10-15T00:00:00Z",
  },
} as TrialMatch;

test("blocks referral action for a simulated trial", () => {
  render(
    <ReferralButton
      inboxItemId="item-1"
      sessionId="session-1"
      match={simulatedMatch}
    />
  );

  expect(screen.getByText(/Referral unavailable until trial status is verified/i)).toBeInTheDocument();
  expect(screen.queryByRole("button", { name: /Initiate referral/i })).not.toBeInTheDocument();
});
