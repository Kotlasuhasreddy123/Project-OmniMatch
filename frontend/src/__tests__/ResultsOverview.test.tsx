import { render, screen } from "@testing-library/react";
import { ResultsOverview } from "@/components/InboxDashboard/ResultsOverview";
import type { InboxItem, TrialMatch } from "@/types";

jest.mock(
  "next/dynamic",
  () => () =>
    function Chart() {
      return <div>Comparison chart</div>;
    },
);

test("explains empty charts without manufacturing suggestions", () => {
  render(<ResultsOverview items={[]} />);
  expect(
    screen.getByText(/No suggestions in this selection/),
  ).toBeInTheDocument();
  expect(screen.getByText(/No criterion data yet/)).toBeInTheDocument();
});

test("recomputes metrics when the visible records change", () => {
  const item: InboxItem = {
    id: "one",
    session_id: "visit",
    created_at: "2026-11-04",
    status: "unread",
    matches: [],
    approved_entities: [],
  };
  const { rerender } = render(<ResultsOverview items={[item]} />);
  expect(screen.getByText("Visits in view").previousSibling).toHaveTextContent(
    "1",
  );
  expect(screen.getByText("Awaiting review").previousSibling).toHaveTextContent(
    "1",
  );
  rerender(<ResultsOverview items={[]} />);
  expect(screen.getByText("Visits in view").previousSibling).toHaveTextContent(
    "0",
  );
});

test("counts criterion checks per suggestion and orders scores numerically", () => {
  const match: TrialMatch = {
    nct_id: "EXAMPLE",
    title: "Sample study",
    score: 0.6,
    phase: "None",
    status: "SIMULATED",
    brief_summary: "Example",
    conditions: ["Example condition"],
    sponsor: "Example",
    missing_variables: [],
    criterion_breakdown: [
      {
        criterion_text: "Lab",
        verdict: "UNKNOWN",
        matched_entity: null,
        confidence: 0,
        is_inclusion: true,
        explanation: "Missing lab",
      },
    ],
    enrollment_readiness_score: 20,
    score_explanation: "Example",
    nearest_site_miles: null,
    nearest_site_city: "",
    locations: [],
    criterion_evidence: [],
    freshness: {
      level: "BLOCKED",
      recommended_action: "DO_NOT_ROUTE",
      reason: "Example",
      registry_status: "SIMULATED",
      last_updated: null,
      age_days: null,
      site_data_available: false,
      evaluated_at: "2026-11-04",
    },
  };
  render(
    <ResultsOverview
      items={[
        {
          id: "one",
          session_id: "visit",
          created_at: "2026-11-04",
          status: "unread",
          approved_entities: [],
          matches: [
            match,
            { ...match, nct_id: "SECOND", enrollment_readiness_score: 80 },
          ],
        },
      ]}
    />,
  );
  expect(
    screen.getByText("Study suggestions").previousSibling,
  ).toHaveTextContent("2");
  expect(
    screen.getByText("Checks to resolve").previousSibling,
  ).toHaveTextContent("2");
  expect(
    screen.getByText("Needs verification").parentElement,
  ).toHaveTextContent("2");
  const values = screen
    .getAllByText(/\/100/)
    .map((node) => node.parentElement?.textContent);
  expect(values).toEqual(["80/100", "20/100"]);
});
