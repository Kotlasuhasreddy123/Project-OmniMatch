import Link from "next/link";
import { ArrowRight, ShieldCheck, FlaskConical, Inbox } from "lucide-react";

export default function HomePage() {
  return (
    <div className="flex flex-col items-center justify-center py-16 text-center">
      <h1 className="text-4xl font-bold tracking-tight text-gray-900">
        OmniMatch
      </h1>
      <p className="mt-4 max-w-2xl text-lg text-gray-600">
        Ambient AI Clinical Intelligence and Automated Trial-Routing Engine.
        Consent-gated audio capture, NLP entity extraction, and asynchronous
        trial matching — all without interrupting patient care.
      </p>
      <p className="mt-3 max-w-2xl text-sm font-medium text-amber-800">
        Classroom prototype. Use synthetic patient details only. A match is not an eligibility or enrollment decision.
      </p>

      <div className="mt-10 grid grid-cols-1 gap-6 sm:grid-cols-3">
        <div className="rounded-xl border border-gray-200 bg-white p-6 shadow-sm text-left">
          <ShieldCheck className="h-8 w-8 text-green-500" aria-hidden="true" />
          <h2 className="mt-3 text-base font-semibold">Consent Gated</h2>
          <p className="mt-1 text-sm text-gray-500">
            Microphone access is strictly blocked until explicit patient consent
            is recorded and audit-logged.
          </p>
        </div>

        <div className="rounded-xl border border-gray-200 bg-white p-6 shadow-sm text-left">
          <FlaskConical className="h-8 w-8 text-blue-500" aria-hidden="true" />
          <h2 className="mt-3 text-base font-semibold">Human-in-the-Loop</h2>
          <p className="mt-1 text-sm text-gray-500">
            Every AI-extracted entity requires explicit staff approval before
            being sent to the trial-matching engine.
          </p>
        </div>

        <div className="rounded-xl border border-gray-200 bg-white p-6 shadow-sm text-left">
          <Inbox className="h-8 w-8 text-purple-500" aria-hidden="true" />
          <h2 className="mt-3 text-base font-semibold">Async Inbox</h2>
          <p className="mt-1 text-sm text-gray-500">
            Trial matches route to an asynchronous inbox — no pop-ups during
            consultations.
          </p>
        </div>
      </div>

      <div className="mt-10 flex gap-4">
        <Link
          href="/session"
          className="flex items-center gap-2 rounded-xl bg-blue-600 px-6 py-3 text-base font-semibold text-white shadow hover:bg-blue-700 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-blue-500 focus-visible:ring-offset-2 transition-colors"
        >
          Start New Session
          <ArrowRight className="h-5 w-5" aria-hidden="true" />
        </Link>
        <Link
          href="/inbox"
          className="flex items-center gap-2 rounded-xl border border-gray-300 bg-white px-6 py-3 text-base font-semibold text-gray-700 shadow hover:bg-gray-50 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-blue-500 focus-visible:ring-offset-2 transition-colors"
        >
          View Inbox
        </Link>
      </div>
    </div>
  );
}
