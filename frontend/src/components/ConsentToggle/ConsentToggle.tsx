'use client';

/**
 * ConsentToggle — explicit patient consent switch (REQ-01, REQ-09).
 *
 * WCAG 2.1 AA: role="switch", aria-checked, aria-label, aria-describedby,
 * visible focus ring, color + icon (not color alone) for state.
 */

import { ShieldCheck, ShieldOff } from "lucide-react";
import clsx from "clsx";

interface ConsentToggleProps {
  consentGranted: boolean;
  onToggle: () => Promise<void>;
  isLoading?: boolean;
  error?: string | null;
}

export function ConsentToggle({
  consentGranted,
  onToggle,
  isLoading = false,
  error,
}: ConsentToggleProps) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-6 shadow-sm">
      {/* Skip to main content for keyboard users */}
      <a
        href="#main-content"
        className="sr-only focus:not-sr-only focus:absolute focus:z-50 focus:rounded focus:bg-brand-600 focus:px-4 focus:py-2 focus:text-white"
      >
        Skip to main content
      </a>

      <div className="flex items-start justify-between gap-4">
        <div>
          <h2
            id="consent-heading"
            className="text-lg font-semibold text-gray-900"
          >
            Patient Consent
          </h2>
          <p
            id="consent-description"
            className="mt-1 text-sm text-gray-500"
          >
            Audio recording is strictly disabled until you enable consent. All
            audio is processed in memory only — no recordings are saved to disk.
          </p>
        </div>

        {/* Toggle switch — role="switch" per WCAG */}
        <button
          role="switch"
          aria-checked={consentGranted}
          aria-label="Patient consent for ambient audio recording"
          aria-describedby="consent-description"
          aria-busy={isLoading}
          disabled={isLoading}
          onClick={onToggle}
          className={clsx(
            "relative inline-flex h-8 w-14 flex-shrink-0 cursor-pointer items-center rounded-full border-2 border-transparent",
            "transition-colors duration-200 ease-in-out",
            "focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-blue-500 focus-visible:ring-offset-2",
            consentGranted ? "bg-green-500" : "bg-gray-300",
            isLoading && "opacity-60 cursor-wait"
          )}
        >
          <span className="sr-only">
            {consentGranted ? "Consent granted — click to revoke" : "Consent not granted — click to grant"}
          </span>
          <span
            aria-hidden="true"
            className={clsx(
              "pointer-events-none inline-block h-6 w-6 transform rounded-full bg-white shadow ring-0 transition duration-200 ease-in-out",
              consentGranted ? "translate-x-6" : "translate-x-0"
            )}
          />
        </button>
      </div>

      {/* Status indicator — uses icon + color, not color alone */}
      <div
        className={clsx(
          "mt-4 flex items-center gap-2 rounded-lg px-4 py-3 text-sm font-medium",
          consentGranted
            ? "bg-green-50 text-green-800"
            : "bg-red-50 text-red-800"
        )}
        aria-live="polite"
        aria-atomic="true"
      >
        {consentGranted ? (
          <>
            <ShieldCheck
              className="h-5 w-5 flex-shrink-0 text-green-600"
              aria-hidden="true"
            />
            <span>Consent active — audio recording is enabled</span>
          </>
        ) : (
          <>
            <ShieldOff
              className="h-5 w-5 flex-shrink-0 text-red-500"
              aria-hidden="true"
            />
            <span>Consent required before audio recording can begin</span>
          </>
        )}
      </div>

      {/* Error message */}
      {error && (
        <p
          role="alert"
          className="mt-3 text-sm text-red-600"
          aria-describedby="consent-heading"
        >
          {error}
        </p>
      )}
    </div>
  );
}
