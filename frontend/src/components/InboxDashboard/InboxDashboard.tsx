'use client';

/**
 * InboxDashboard — Asynchronous Clinical Trial Inbox (REQ-07, REQ-09, REQ-10).
 * Enhanced with per-criterion eligibility breakdown (Feature 1),
 * enrollment readiness score (Feature 2), geographic proximity (Feature 4),
 * and sponsor referral routing (Feature 5).
 */

import { useState, useCallback } from "react";
import {
  ChevronDown, ChevronUp, Inbox, CheckCircle2, Clock,
  FlaskConical, ListChecks, User, MapPin,
} from "lucide-react";
import clsx from "clsx";
import { EligibilityBreakdown } from "@/components/EligibilityBreakdown/EligibilityBreakdown";
import { ReferralButton } from "@/components/ui/ReferralButton";
import { TrialTrustPanel } from "@/components/TrialTrustPanel/TrialTrustPanel";
import type { InboxItem, TrialMatch } from "@/types";

interface InboxDashboardProps {
  items: InboxItem[];
  unreadCount: number;
  onMarkReviewed: (id: string) => Promise<void>;
  isLoading?: boolean;
}

function MissingVariablesList({ variables }: { variables: string[] }) {
  if (variables.length === 0) {
    return (
      <p className="text-sm text-green-700">
        ✓ All key eligibility criteria were found in the patient transcript.
      </p>
    );
  }
  return (
    <ul
      aria-label="Missing eligibility variables not found in transcript"
      className="space-y-1"
    >
      {variables.map((v, i) => (
        <li
          key={i}
          className="flex items-start gap-2 text-sm text-amber-800"
        >
          <ListChecks
            className="mt-0.5 h-4 w-4 shrink-0 text-amber-500"
            aria-hidden="true"
          />
          {v}
        </li>
      ))}
    </ul>
  );
}

function TrialMatchCard({ match, inboxItemId, sessionId }: { match: TrialMatch; inboxItemId: string; sessionId: string }) {
  const [expanded, setExpanded] = useState(false);

  return (
    <div className="rounded-lg border border-gray-200 bg-white">
      <button
        onClick={() => setExpanded((p) => !p)}
        aria-expanded={expanded}
        aria-controls={`trial-${match.nct_id}-details`}
        className={clsx(
          "flex w-full items-start justify-between gap-4 p-4 text-left",
          "focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-blue-500 focus-visible:ring-inset",
          "hover:bg-gray-50 transition-colors"
        )}
      >
        <div className="min-w-0 flex-1">
          <div className="flex flex-wrap items-center gap-2">
            <span className="text-sm font-semibold text-gray-900 truncate">{match.title}</span>
            <span className="shrink-0 rounded-full bg-blue-100 px-2 py-0.5 text-xs font-medium text-blue-700">
              {match.phase}
            </span>
            <span className={clsx(
              "shrink-0 rounded-full px-2 py-0.5 text-xs font-medium",
              match.status === "RECRUITING" ? "bg-green-100 text-green-700" : "bg-gray-100 text-gray-600"
            )}>
              {match.status}
            </span>
          </div>
          <div className="mt-1 flex flex-wrap items-center gap-3 text-xs text-gray-500">
            <span>{match.nct_id}</span>
            {/* NEW FEATURE 2: Enrollment readiness score */}
            {match.enrollment_readiness_score > 0 && (
              <span className={clsx(
                "font-semibold",
                match.enrollment_readiness_score >= 70 ? "text-green-600" :
                match.enrollment_readiness_score >= 45 ? "text-amber-600" : "text-red-500"
              )}>
                {Math.round(match.enrollment_readiness_score)}% readiness
              </span>
            )}
            {/* NEW FEATURE 4: Geographic proximity */}
            {match.nearest_site_miles != null && (
              <span className="flex items-center gap-1">
                <MapPin className="h-3 w-3" aria-hidden="true" />
                {match.nearest_site_miles <= 200
                  ? `${match.nearest_site_miles}mi — ${match.nearest_site_city}`
                  : `${match.nearest_site_city}`}
              </span>
            )}
            <span>
              {match.missing_variables.length === 0
                ? "All criteria covered"
                : `${match.missing_variables.length} missing variable${match.missing_variables.length !== 1 ? "s" : ""}`}
            </span>
          </div>
        </div>
        <span className="shrink-0" aria-hidden="true">
          {expanded ? <ChevronUp className="h-5 w-5 text-gray-400" /> : <ChevronDown className="h-5 w-5 text-gray-400" />}
        </span>
      </button>

      {expanded && (
        <div id={`trial-${match.nct_id}-details`} className="border-t border-gray-100 px-4 pb-4 pt-3 space-y-4">
          <div>
            <h4 className="text-xs font-semibold uppercase tracking-wider text-gray-500">Brief Summary</h4>
            <p className="mt-1 text-sm text-gray-700">{match.brief_summary || "No summary available."}</p>
          </div>

          {match.conditions.length > 0 && (
            <div>
              <h4 className="text-xs font-semibold uppercase tracking-wider text-gray-500">Conditions</h4>
              <div className="mt-1 flex flex-wrap gap-1">
                {match.conditions.map((c) => (
                  <span key={c} className="rounded-full bg-purple-100 px-2 py-0.5 text-xs text-purple-800">{c}</span>
                ))}
              </div>
            </div>
          )}

          {/* NEW FEATURE 1: Per-criterion eligibility breakdown */}
          {match.criterion_breakdown && match.criterion_breakdown.length > 0 && (
            <EligibilityBreakdown
              criterionBreakdown={match.criterion_breakdown}
              enrollmentReadinessScore={match.enrollment_readiness_score}
              scoreExplanation={match.score_explanation}
              nctId={match.nct_id}
            />
          )}

          {match.freshness && (
            <TrialTrustPanel
              freshness={match.freshness}
              criterionEvidence={match.criterion_evidence ?? []}
            />
          )}

          {/* Classic missing variables fallback */}
          {(!match.criterion_breakdown || match.criterion_breakdown.length === 0) && match.missing_variables.length > 0 && (
            <div>
              <h4 className="flex items-center gap-1.5 text-xs font-semibold uppercase tracking-wider text-gray-500">
                <ListChecks className="h-4 w-4" aria-hidden="true" />
                Missing Variables Checklist
              </h4>
              <ul aria-label="Missing eligibility variables" className="mt-2 space-y-1">
                {match.missing_variables.map((v, i) => (
                  <li key={i} className="flex items-start gap-2 text-sm text-amber-800">
                    <ListChecks className="mt-0.5 h-4 w-4 shrink-0 text-amber-500" aria-hidden="true" />
                    {v}
                  </li>
                ))}
              </ul>
            </div>
          )}

          <div className="flex items-center justify-between">
            <p className="flex items-center gap-1.5 text-xs text-gray-400">
              <FlaskConical className="h-3.5 w-3.5" aria-hidden="true" />
              Sponsor: {match.sponsor || "N/A"}
            </p>
            {/* NEW FEATURE 5: Referral button */}
            <ReferralButton inboxItemId={inboxItemId} match={match} sessionId={sessionId} />
          </div>
        </div>
      )}
    </div>
  );
}

function InboxItemRow({
  item,
  onMarkReviewed,
}: {
  item: InboxItem;
  onMarkReviewed: (id: string) => Promise<void>;
}) {
  const [expanded, setExpanded] = useState(false);
  const [marking, setMarking] = useState(false);

  const handleMark = async () => {
    setMarking(true);
    await onMarkReviewed(item.id);
    setMarking(false);
  };

  const createdAt = new Date(item.created_at).toLocaleString();

  return (
    <article
      className={clsx(
        "rounded-xl border shadow-sm transition-all",
        item.status === "unread"
          ? "border-blue-200 bg-blue-50"
          : "border-gray-200 bg-white"
      )}
      aria-label={`Inbox item for session ${item.session_id}, ${item.status}`}
    >
      {/* Item header */}
      <button
        onClick={() => setExpanded((p) => !p)}
        aria-expanded={expanded}
        aria-controls={`inbox-${item.id}-content`}
        className={clsx(
          "flex w-full items-start justify-between gap-4 p-5 text-left",
          "focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-blue-500 focus-visible:ring-inset",
          "hover:bg-white/60 transition-colors rounded-t-xl"
        )}
      >
        <div className="min-w-0 flex-1 space-y-1">
          <div className="flex flex-wrap items-center gap-2">
            {item.status === "unread" ? (
              <span
                className="flex items-center gap-1 rounded-full bg-blue-600 px-2.5 py-0.5 text-xs font-semibold text-white"
                aria-label="Unread inbox item"
              >
                <Inbox className="h-3 w-3" aria-hidden="true" />
                New
              </span>
            ) : (
              <span className="flex items-center gap-1 text-xs text-gray-400">
                <CheckCircle2 className="h-3 w-3" aria-hidden="true" />
                Reviewed
              </span>
            )}
            <span className="text-sm font-semibold text-gray-900">
              {item.matches.length} trial{item.matches.length !== 1 ? "s" : ""} matched
            </span>
          </div>

          <div className="flex flex-wrap gap-3 text-xs text-gray-500">
            <span className="flex items-center gap-1">
              <User className="h-3 w-3" aria-hidden="true" />
              Session: {item.session_id}
            </span>
            <span className="flex items-center gap-1">
              <Clock className="h-3 w-3" aria-hidden="true" />
              {createdAt}
            </span>
          </div>

          {/* Approved entities summary */}
          <div className="flex flex-wrap gap-1">
            {item.approved_entities.slice(0, 5).map((term) => (
              <span
                key={term}
                className="rounded-full bg-gray-100 px-2 py-0.5 text-xs text-gray-600"
              >
                {term}
              </span>
            ))}
            {item.approved_entities.length > 5 && (
              <span className="text-xs text-gray-400">
                +{item.approved_entities.length - 5} more
              </span>
            )}
          </div>
        </div>

        <span className="shrink-0" aria-hidden="true">
          {expanded ? (
            <ChevronUp className="h-5 w-5 text-gray-400" />
          ) : (
            <ChevronDown className="h-5 w-5 text-gray-400" />
          )}
        </span>
      </button>

      {/* Expanded trial list */}
      {expanded && (
        <div
          id={`inbox-${item.id}-content`}
          className="border-t border-gray-200 p-5 space-y-3"
        >
          <h3 className="text-sm font-semibold text-gray-700">
            Matched Trials
          </h3>
          {item.matches.length === 0 ? (
            <p className="text-sm text-gray-500">No matches found for this session.</p>
          ) : (
            <div className="space-y-2">
              {item.matches.map((match) => (
                <TrialMatchCard
                  key={match.nct_id}
                  match={match}
                  inboxItemId={item.id}
                  sessionId={item.session_id}
                />
              ))}
            </div>
          )}

          {item.status === "unread" && (
            <button
              onClick={handleMark}
              disabled={marking}
              aria-busy={marking}
              aria-label="Mark this inbox item as reviewed"
              className={clsx(
                "mt-2 flex items-center gap-2 rounded-lg border border-gray-300 bg-white px-4 py-2 text-sm font-medium text-gray-700",
                "hover:bg-gray-50 transition-colors",
                "focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-blue-500 focus-visible:ring-offset-1",
                marking && "opacity-60 cursor-wait"
              )}
            >
              <CheckCircle2 className="h-4 w-4 text-green-500" aria-hidden="true" />
              {marking ? "Marking…" : "Mark as Reviewed"}
            </button>
          )}
        </div>
      )}
    </article>
  );
}

export function InboxDashboard({
  items,
  unreadCount,
  onMarkReviewed,
  isLoading = false,
}: InboxDashboardProps) {
  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">
            Clinical Trial Inbox
          </h1>
          <p className="mt-1 text-sm text-gray-500">
            Trial matches are routed here after each visit session completes.
            No real-time alerts — review at your convenience.
          </p>
        </div>
        {unreadCount > 0 && (
          <span
            className="rounded-full bg-blue-600 px-3 py-1 text-sm font-semibold text-white"
            aria-label={`${unreadCount} unread inbox items`}
            aria-live="polite"
          >
            {unreadCount} new
          </span>
        )}
      </div>

      {/* Loading */}
      {isLoading && (
        <div
          role="status"
          aria-label="Loading inbox items"
          className="flex items-center justify-center py-16"
        >
          <div className="h-8 w-8 animate-spin rounded-full border-4 border-blue-600 border-t-transparent" />
          <span className="sr-only">Loading…</span>
        </div>
      )}

      {/* Empty state */}
      {!isLoading && items.length === 0 && (
        <div className="flex flex-col items-center justify-center rounded-xl border border-dashed border-gray-300 py-16 text-center">
          <Inbox className="h-12 w-12 text-gray-300" aria-hidden="true" />
          <p className="mt-3 text-base font-medium text-gray-500">
            No inbox items yet
          </p>
          <p className="mt-1 text-sm text-gray-400">
            Complete a visit session to see matched trials here.
          </p>
        </div>
      )}

      {/* Inbox items */}
      {!isLoading && items.length > 0 && (
        <div
          className="space-y-4"
          role="feed"
          aria-label="Clinical trial inbox"
          aria-busy={isLoading}
        >
          {items.map((item) => (
            <InboxItemRow
              key={item.id}
              item={item}
              onMarkReviewed={onMarkReviewed}
            />
          ))}
        </div>
      )}
    </div>
  );
}
