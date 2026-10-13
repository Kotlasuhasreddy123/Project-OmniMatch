/**
 * VerificationPanel tests — TEST-03, REQ-04
 *
 * Critical assertion: rejected entity terms must NOT appear in the
 * payload sent to onSubmit. Only approved, non-negated, patient-context
 * entities should be submitted to the match engine.
 */

import React from "react";
import { render, screen, fireEvent, waitFor } from "@testing-library/react";
import "@testing-library/jest-dom";
import { VerificationPanel } from "@/components/VerificationPanel/VerificationPanel";
import type { ClinicalEntity } from "@/types";

const mockOnSubmit = jest.fn().mockResolvedValue(undefined);

const testEntities: ClinicalEntity[] = [
  {
    term: "diabetes",
    entity_type: "DISEASE",
    negated: false,
    context: "patient",
    confidence: 0.9,
    status: "pending",
  },
  {
    term: "hypertension",
    entity_type: "DISEASE",
    negated: false,
    context: "patient",
    confidence: 0.85,
    status: "pending",
  },
  {
    term: "asthma",
    entity_type: "DISEASE",
    negated: true,      // auto-excluded
    context: "patient",
    confidence: 0.8,
    status: "pending",
  },
];

describe("VerificationPanel — REQ-04, TEST-03", () => {
  beforeEach(() => jest.clearAllMocks());

  it("renders entity chips for all non-negated entities", () => {
    render(
      <VerificationPanel
        entities={testEntities}
        sessionId="sess-vp-test"
        onSubmit={mockOnSubmit}
      />
    );
    // Should show diabetes and hypertension chips
    expect(screen.getByText("diabetes")).toBeInTheDocument();
    expect(screen.getByText("hypertension")).toBeInTheDocument();
  });

  it("Submit button is disabled when zero entities are approved", () => {
    render(
      <VerificationPanel
        entities={testEntities}
        sessionId="sess-vp-test"
        onSubmit={mockOnSubmit}
      />
    );
    const submitBtn = screen.getByRole("button", { name: /submit/i });
    expect(submitBtn).toHaveAttribute("aria-disabled", "true");
  });

  it("Submit button enables after at least one entity is approved", async () => {
    render(
      <VerificationPanel
        entities={testEntities}
        sessionId="sess-vp-test"
        onSubmit={mockOnSubmit}
      />
    );
    // Approve diabetes
    fireEvent.click(screen.getByRole("button", { name: /approve entity: diabetes/i }));

    await waitFor(() => {
      const submitBtn = screen.getByRole("button", { name: /submit/i });
      expect(submitBtn).not.toHaveAttribute("aria-disabled", "true");
    });
  });

  it("TEST-03: rejected entity terms are NOT in the onSubmit payload", async () => {
    render(
      <VerificationPanel
        entities={testEntities}
        sessionId="sess-vp-test"
        onSubmit={mockOnSubmit}
      />
    );

    // Approve diabetes, reject hypertension
    fireEvent.click(screen.getByRole("button", { name: /approve entity: diabetes/i }));
    fireEvent.click(screen.getByRole("button", { name: /reject entity: hypertension/i }));

    // Submit
    const submitBtn = screen.getByRole("button", { name: /submit/i });
    fireEvent.click(submitBtn);

    await waitFor(() => expect(mockOnSubmit).toHaveBeenCalled());

    const submittedEntities: ClinicalEntity[] = mockOnSubmit.mock.calls[0][0];

    // Only diabetes should be in the payload (approved)
    const submittedTerms = submittedEntities.map((e) => e.term);
    expect(submittedTerms).toContain("diabetes");
    expect(submittedTerms).not.toContain("hypertension"); // REJECTED — must be excluded
    expect(submittedTerms).not.toContain("asthma"); // NEGATED — must be excluded
  });

  it("TEST-03: only approved entities reach onSubmit — all statuses verified", async () => {
    render(
      <VerificationPanel
        entities={testEntities}
        sessionId="sess-vp-test"
        onSubmit={mockOnSubmit}
      />
    );

    // Approve both patient-context entities
    fireEvent.click(screen.getByRole("button", { name: /approve entity: diabetes/i }));
    fireEvent.click(screen.getByRole("button", { name: /approve entity: hypertension/i }));

    fireEvent.click(screen.getByRole("button", { name: /submit/i }));

    await waitFor(() => expect(mockOnSubmit).toHaveBeenCalled());

    const submittedEntities: ClinicalEntity[] = mockOnSubmit.mock.calls[0][0];

    // Verify every submitted entity has status=approved
    for (const entity of submittedEntities) {
      expect(entity.status).toBe("approved");
    }

    // Verify negated asthma is never submitted
    const hasAsthma = submittedEntities.some((e) => e.term === "asthma");
    expect(hasAsthma).toBe(false);
  });
});
