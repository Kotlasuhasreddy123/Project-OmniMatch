import { render, screen } from "@testing-library/react";
import { ResultsOverview } from "@/components/InboxDashboard/ResultsOverview";
import type { InboxItem } from "@/types";

test("explains empty charts without manufacturing suggestions", () => {
  render(<ResultsOverview items={[]} />);
  expect(screen.getByText(/No suggestions in this selection/)).toBeInTheDocument();
  expect(screen.getByText(/No criterion data yet/)).toBeInTheDocument();
});

test("recomputes metrics when the visible records change", () => {
  const item: InboxItem = { id:"one",session_id:"visit",created_at:"2026-11-04",status:"unread",matches:[],approved_entities:[] };
  const { rerender } = render(<ResultsOverview items={[item]} />);
  expect(screen.getByText("Visits in view").previousSibling).toHaveTextContent("1");
  expect(screen.getByText("Awaiting review").previousSibling).toHaveTextContent("1");
  rerender(<ResultsOverview items={[]} />);
  expect(screen.getByText("Visits in view").previousSibling).toHaveTextContent("0");
});
