import Link from "next/link";
import { ArrowRight, ShieldCheck, FlaskConical, Inbox } from "lucide-react";

export default function HomePage() {
  return (
    <div className="flex flex-col items-center justify-center rounded-[2rem] bg-gradient-to-b from-teal-50 via-white to-white px-6 py-20 text-center">
      <p className="eyebrow">OMNIMATCH · CLINICAL RESEARCH, CONNECTED</p>
      <h1 className="mt-6 max-w-4xl text-5xl font-semibold tracking-tighter text-gray-900 sm:text-7xl">
        A conversation. A clearer research path.
      </h1>
      <p className="mt-4 max-w-2xl text-lg text-gray-600">
        Bring visit information, human review, and study evidence into one considered workspace.
        For clinicians, research coordinators, and academic teams exploring the path from a fictional visit to study review.
      </p>
      <div className="mt-6 max-w-2xl rounded-xl border border-gray-200 bg-white p-5 text-left text-sm text-gray-700">
        <h2 className="font-semibold text-gray-900">What does a trial mean here?</h2>
        <p className="mt-2">A clinical trial is a research study with rules about who may take part. The sample catalog demonstrates how approved visit information can support study review. Available conditions depend on the indexed catalog. These are research matches, not disease forecasts.</p>
        <a href="/guide" className="mt-3 inline-block text-blue-700 underline">Read the simple project guide and demo script</a>
      </div>
      <p className="mt-3 max-w-2xl text-sm font-medium text-amber-800">
        Use synthetic patient details. A study suggestion still needs eligibility review.
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
          Explore Visual Results
        </Link>
      </div>
    </div>
  );
}
