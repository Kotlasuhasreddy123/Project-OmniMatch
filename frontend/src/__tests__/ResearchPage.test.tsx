import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import ResearchPage from "@/app/research/page";
import {
  analyzeNote,
  askStudyEvidence,
  getAdvancedModelStatus,
} from "@/lib/apiClient";

const mockRouter = { replace: jest.fn() };
jest.mock("next/navigation", () => ({ useRouter: () => mockRouter }));
jest.mock("@/lib/auth", () => ({
  getCurrentUser: () => ({ sub: "synthetic-user" }),
}));
jest.mock("@/lib/apiClient", () => ({
  analyzeNote: jest.fn(),
  askStudyEvidence: jest.fn(),
  getAdvancedModelStatus: jest.fn(),
}));
const result = {
  entities: [
    {
      term: "asthma",
      entity_type: "DISEASE",
      context: "patient",
      negated: false,
      status: "pending",
      confidence: 0.8,
      source: "rules",
      start: 1,
      end: 7,
    },
    {
      term: "stroke",
      entity_type: "DISEASE",
      context: "family",
      negated: false,
      status: "pending",
      confidence: 0.8,
      source: "rules",
      start: 9,
      end: 15,
    },
    {
      term: "COPD",
      entity_type: "DISEASE",
      context: "patient",
      negated: true,
      status: "pending",
      confidence: 0.8,
      source: "rules",
      start: 16,
      end: 20,
    },
  ],
  assertion_reviews: [],
  assertion_reviewed_count: 3,
  assertion_unreviewed_count: 0,
  sentiment: {
    label: "negative",
    scores: { positive: 0.1, neutral: 0.1, negative: 0.8 },
    partial: false,
    meaning: "General wording only.",
  },
  limits: [],
};
beforeEach(() => {
  jest.clearAllMocks();
  (getAdvancedModelStatus as jest.Mock).mockResolvedValue({
    enabled: true,
    dependencies_ready: true,
    local_only: true,
    models: [
      "ner",
      "sentiment",
      "assertion",
      "embedding",
      "reranker",
      "generator",
    ].map((task) => ({ task, cached: true })),
  });
  (analyzeNote as jest.Mock).mockResolvedValue(result);
  (askStudyEvidence as jest.Mock).mockResolvedValue({
    answer: "Study excerpt [S1]",
    sources: [],
    abstained: false,
    generation_mode: "extractive_grounding_fallback",
    scope: { retrieved_studies: 1, passages_considered: 2 },
  });
});

async function analyzeExample() {
  render(<ResearchPage />);
  fireEvent.click(
    screen.getByRole("button", { name: "Load a fictional example" }),
  );
  const button = screen.getByRole("button", {
    name: "Analyze text with transformers",
  });
  await waitFor(() => expect(button).toBeEnabled());
  fireEvent.click(button);
  await screen.findByRole("heading", { name: "0 approved patient terms" });
}

test("sentiment and model suggestions never bypass per-term approval", async () => {
  await analyzeExample();
  const ask = screen.getByRole("button", { name: "Find a cited study answer" });
  expect(ask).toBeDisabled();
  expect(screen.getAllByRole("button", { name: "Approve" })).toHaveLength(1);
  fireEvent.click(screen.getByRole("button", { name: "Approve" }));
  fireEvent.click(ask);
  await waitFor(() => expect(askStudyEvidence).toHaveBeenCalledTimes(1));
  await screen.findByRole("region", { name: "Study evidence result" });
  const terms = (askStudyEvidence as jest.Mock).mock.calls[0][1];
  expect(terms.map((entity: { term: string }) => entity.term)).toEqual([
    "asthma",
  ]);
  expect(terms[0].status).toBe("approved");
});

test("editing a note invalidates the previous model findings and approvals", async () => {
  await analyzeExample();
  fireEvent.click(screen.getByRole("button", { name: "Approve" }));
  fireEvent.change(screen.getByLabelText("Visit text"), {
    target: { value: "A different fictional visit." },
  });
  expect(
    screen.queryByRole("button", { name: "Find a cited study answer" }),
  ).not.toBeInTheDocument();
  expect(
    screen.queryByRole("button", { name: "Approve" }),
  ).not.toBeInTheDocument();
});

test("missing local dependencies keep analysis disabled", async () => {
  (getAdvancedModelStatus as jest.Mock).mockResolvedValue({
    enabled: true,
    dependencies_ready: false,
    models: [],
  });
  render(<ResearchPage />);
  fireEvent.click(
    screen.getByRole("button", { name: "Load a fictional example" }),
  );
  await screen.findByRole("heading", { name: "Local model setup is needed" });
  expect(
    screen.getByRole("button", { name: "Analyze text with transformers" }),
  ).toBeDisabled();
});
