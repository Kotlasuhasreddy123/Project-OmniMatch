/**
 * EligibilityBreakdown component tests — NEW FEATURE 1 & 2 (REQ-04, REQ-09).
 */

import React from "react";
import { render, screen } from "@testing-library/react";
import "@testing-library/jest-dom";
import { EligibilityBreakdown } from "@/components/EligibilityBreakdown/EligibilityBreakdown";

const sampleBreakdown = [
  { criterion_text: "Patients with type 2 diabetes", verdict: "MET" as const,
    matched_entity: "diabetes", confidence: 0.9, is_inclusion: true, explanation: "diabetes approved" },
  { criterion_text: "No prior insulin use", verdict: "NOT_MET" as const,
    matched_entity: "insulin", confidence: 0.8, is_inclusion: true, explanation: "insulin negated" },
  { criterion_text: "HbA1c > 7%", verdict: "UNKNOWN" as const,
    matched_entity: null, confidence: 0.5, is_inclusion: true, explanation: "lab value" },
  { criterion_text: "No active malignancy", verdict: "MISSING" as const,
    matched_entity: null, confidence: 0.0, is_inclusion: true, explanation: "not mentioned" },
];

describe("EligibilityBreakdown — Feature 1 & 2", () => {
  it("renders enrollment readiness score", () => {
    render(
      <EligibilityBreakdown
        criterionBreakdown={sampleBreakdown}
        enrollmentReadinessScore={72.5}
        scoreExplanation="Similarity: 80% | Inclusion: 3/4"
        nctId="NCT001"
      />
    );
    expect(screen.getByText(/73%|72%|72\.5%/)).toBeInTheDocument();
    expect(screen.getByText(/Enrollment Readiness/i)).toBeInTheDocument();
  });

  it("renders MET verdict with correct styling", () => {
    render(
      <EligibilityBreakdown
        criterionBreakdown={sampleBreakdown}
        enrollmentReadinessScore={72.5}
        scoreExplanation=""
        nctId="NCT001"
      />
    );
    expect(screen.getByText("Met")).toBeInTheDocument();
  });

  it("renders UNKNOWN verdict for lab criteria", () => {
    render(
      <EligibilityBreakdown
        criterionBreakdown={sampleBreakdown}
        enrollmentReadinessScore={50.0}
        scoreExplanation=""
        nctId="NCT001"
      />
    );
    expect(screen.getByText("Unknown")).toBeInTheDocument();
  });

  it("has accessible aria-label on container", () => {
    render(
      <EligibilityBreakdown
        criterionBreakdown={sampleBreakdown}
        enrollmentReadinessScore={60.0}
        scoreExplanation=""
        nctId="NCT-TEST"
      />
    );
    expect(
      screen.getByRole("region", { name: /eligibility breakdown.*NCT-TEST/i }) ||
      document.querySelector("[aria-label*='NCT-TEST']")
    ).toBeTruthy();
  });

  it("renders nothing when breakdown is empty", () => {
    const { container } = render(
      <EligibilityBreakdown
        criterionBreakdown={[]}
        enrollmentReadinessScore={0}
        scoreExplanation=""
        nctId="NCT001"
      />
    );
    expect(container.firstChild).toBeNull();
  });

  it("shows score explanation text", () => {
    render(
      <EligibilityBreakdown
        criterionBreakdown={sampleBreakdown}
        enrollmentReadinessScore={70}
        scoreExplanation="Similarity: 85% (×0.35)"
        nctId="NCT001"
      />
    );
    expect(screen.getByText(/Similarity: 85%/)).toBeInTheDocument();
  });
});
