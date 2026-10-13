/**
 * ConsentToggle tests — TEST-01, REQ-01, REQ-09
 *
 * Validates:
 * - Toggle renders with correct WCAG aria attributes
 * - Correct state shown when off/on
 * - onToggle callback called on click
 * - aria-checked reflects consent state
 */

import React from "react";
import { render, screen, fireEvent } from "@testing-library/react";
import "@testing-library/jest-dom";
import { ConsentToggle } from "@/components/ConsentToggle/ConsentToggle";

const mockToggle = jest.fn();

describe("ConsentToggle — REQ-01, REQ-09", () => {
  beforeEach(() => jest.clearAllMocks());

  describe("WCAG 2.1 AA Accessibility", () => {
    it("renders with role=switch", () => {
      render(
        <ConsentToggle
          consentGranted={false}
          onToggle={mockToggle}
        />
      );
      expect(screen.getByRole("switch")).toBeInTheDocument();
    });

    it("has correct aria-label", () => {
      render(
        <ConsentToggle
          consentGranted={false}
          onToggle={mockToggle}
        />
      );
      const toggle = screen.getByRole("switch");
      expect(toggle).toHaveAttribute(
        "aria-label",
        "Patient consent for ambient audio recording"
      );
    });

    it("has aria-describedby pointing to description element", () => {
      render(
        <ConsentToggle
          consentGranted={false}
          onToggle={mockToggle}
        />
      );
      const toggle = screen.getByRole("switch");
      expect(toggle).toHaveAttribute("aria-describedby", "consent-description");
      expect(document.getElementById("consent-description")).toBeInTheDocument();
    });

    it("aria-checked is false when consent not granted", () => {
      render(
        <ConsentToggle
          consentGranted={false}
          onToggle={mockToggle}
        />
      );
      expect(screen.getByRole("switch")).toHaveAttribute("aria-checked", "false");
    });

    it("aria-checked is true when consent is granted", () => {
      render(
        <ConsentToggle
          consentGranted={true}
          onToggle={mockToggle}
        />
      );
      expect(screen.getByRole("switch")).toHaveAttribute("aria-checked", "true");
    });

    it("aria-busy is set when loading", () => {
      render(
        <ConsentToggle
          consentGranted={false}
          onToggle={mockToggle}
          isLoading={true}
        />
      );
      expect(screen.getByRole("switch")).toHaveAttribute("aria-busy", "true");
    });
  });

  describe("Consent State Behavior", () => {
    it("shows 'Consent required' message when consent is OFF", () => {
      render(
        <ConsentToggle
          consentGranted={false}
          onToggle={mockToggle}
        />
      );
      expect(
        screen.getByText(/consent required before audio recording/i)
      ).toBeInTheDocument();
    });

    it("shows 'Consent active' message when consent is ON", () => {
      render(
        <ConsentToggle
          consentGranted={true}
          onToggle={mockToggle}
        />
      );
      expect(
        screen.getByText(/consent active/i)
      ).toBeInTheDocument();
    });

    it("calls onToggle when button is clicked", () => {
      render(
        <ConsentToggle
          consentGranted={false}
          onToggle={mockToggle}
        />
      );
      fireEvent.click(screen.getByRole("switch"));
      expect(mockToggle).toHaveBeenCalledTimes(1);
    });

    it("does NOT call onToggle when loading/disabled", () => {
      render(
        <ConsentToggle
          consentGranted={false}
          onToggle={mockToggle}
          isLoading={true}
        />
      );
      fireEvent.click(screen.getByRole("switch"));
      expect(mockToggle).not.toHaveBeenCalled();
    });
  });

  describe("Error Display", () => {
    it("renders error message with role=alert when error is present", () => {
      render(
        <ConsentToggle
          consentGranted={false}
          onToggle={mockToggle}
          error="Failed to log consent"
        />
      );
      expect(screen.getByRole("alert")).toHaveTextContent("Failed to log consent");
    });
  });
});
