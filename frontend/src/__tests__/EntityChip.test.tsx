/**
 * EntityChip tests — TEST-03, REQ-04, REQ-09
 *
 * Validates:
 * - Approve/reject buttons have unique aria-labels (WCAG)
 * - Approved/rejected state reflected visually and via aria-pressed
 * - Rejected entities are visually marked as rejected
 * - Callbacks fire correctly
 */

import React from "react";
import { render, screen, fireEvent } from "@testing-library/react";
import "@testing-library/jest-dom";
import { EntityChip } from "@/components/EntityChip/EntityChip";
import type { ClinicalEntity } from "@/types";

const mockApprove = jest.fn();
const mockReject = jest.fn();

const pendingEntity: ClinicalEntity = {
  term: "diabetes",
  entity_type: "DISEASE",
  negated: false,
  context: "patient",
  confidence: 0.9,
  status: "pending",
};

const negatedEntity: ClinicalEntity = {
  term: "hypertension",
  entity_type: "DISEASE",
  negated: true,
  context: "patient",
  confidence: 0.85,
  status: "pending",
};

const familyEntity: ClinicalEntity = {
  term: "cancer",
  entity_type: "DISEASE",
  negated: false,
  context: "family",
  confidence: 0.8,
  status: "pending",
};

describe("EntityChip — REQ-04, REQ-09, TEST-03", () => {
  beforeEach(() => jest.clearAllMocks());

  describe("WCAG Accessibility", () => {
    it("approve button has unique aria-label with entity term", () => {
      render(
        <EntityChip
          entity={pendingEntity}
          onApprove={mockApprove}
          onReject={mockReject}
        />
      );
      expect(
        screen.getByRole("button", { name: /approve entity: diabetes/i })
      ).toBeInTheDocument();
    });

    it("reject button has unique aria-label with entity term", () => {
      render(
        <EntityChip
          entity={pendingEntity}
          onApprove={mockApprove}
          onReject={mockReject}
        />
      );
      expect(
        screen.getByRole("button", { name: /reject entity: diabetes/i })
      ).toBeInTheDocument();
    });

    it("has role=group with descriptive aria-label", () => {
      render(
        <EntityChip
          entity={pendingEntity}
          onApprove={mockApprove}
          onReject={mockReject}
        />
      );
      expect(screen.getByRole("group")).toHaveAttribute(
        "aria-label",
        expect.stringContaining("diabetes")
      );
    });
  });

  describe("Approve/Reject Behavior — TEST-03", () => {
    it("calls onApprove with entity term when Approve clicked", () => {
      render(
        <EntityChip
          entity={pendingEntity}
          onApprove={mockApprove}
          onReject={mockReject}
        />
      );
      fireEvent.click(screen.getByRole("button", { name: /approve entity: diabetes/i }));
      expect(mockApprove).toHaveBeenCalledWith("diabetes");
      expect(mockReject).not.toHaveBeenCalled();
    });

    it("calls onReject with entity term when Reject clicked", () => {
      render(
        <EntityChip
          entity={pendingEntity}
          onApprove={mockApprove}
          onReject={mockReject}
        />
      );
      fireEvent.click(screen.getByRole("button", { name: /reject entity: diabetes/i }));
      expect(mockReject).toHaveBeenCalledWith("diabetes");
      expect(mockApprove).not.toHaveBeenCalled();
    });

    it("approved entity shows aria-pressed=true on Approve button", () => {
      const approvedEntity = { ...pendingEntity, status: "approved" as const };
      render(
        <EntityChip
          entity={approvedEntity}
          onApprove={mockApprove}
          onReject={mockReject}
        />
      );
      const approveBtn = screen.getByRole("button", { name: /approve entity: diabetes/i });
      expect(approveBtn).toHaveAttribute("aria-pressed", "true");
    });

    it("rejected entity shows aria-pressed=true on Reject button", () => {
      const rejectedEntity = { ...pendingEntity, status: "rejected" as const };
      render(
        <EntityChip
          entity={rejectedEntity}
          onApprove={mockApprove}
          onReject={mockReject}
        />
      );
      const rejectBtn = screen.getByRole("button", { name: /reject entity: diabetes/i });
      expect(rejectBtn).toHaveAttribute("aria-pressed", "true");
    });
  });

  describe("Negated/Family Entities — REQ-03", () => {
    it("negated entity shows 'Negated' badge", () => {
      render(
        <EntityChip
          entity={negatedEntity}
          onApprove={mockApprove}
          onReject={mockReject}
        />
      );
      expect(screen.getByText("Negated")).toBeInTheDocument();
    });

    it("negated entity shows exclusion notice", () => {
      render(
        <EntityChip
          entity={negatedEntity}
          onApprove={mockApprove}
          onReject={mockReject}
        />
      );
      expect(screen.getByText(/excluded from query.*negated/i)).toBeInTheDocument();
    });

    it("family context entity shows 'Family History' badge", () => {
      render(
        <EntityChip
          entity={familyEntity}
          onApprove={mockApprove}
          onReject={mockReject}
        />
      );
      expect(screen.getByText("Family History")).toBeInTheDocument();
    });

    it("negated entity does NOT show approve/reject buttons", () => {
      render(
        <EntityChip
          entity={negatedEntity}
          onApprove={mockApprove}
          onReject={mockReject}
        />
      );
      expect(
        screen.queryByRole("button", { name: /approve entity/i })
      ).not.toBeInTheDocument();
      expect(
        screen.queryByRole("button", { name: /reject entity/i })
      ).not.toBeInTheDocument();
    });
  });
});
