"use client";
import { useEffect, useRef, useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { getCurrentUser } from "@/lib/auth";
import {
  analyzeNote,
  askStudyEvidence,
  getAdvancedModelStatus,
} from "@/lib/apiClient";
import type {
  AdvancedModelStatus,
  DeepEntity,
  NoteUnderstanding,
  StudyEvidenceAnswer,
} from "@/types";

const example =
  "The fictional patient has asthma and uses albuterol. The patient denies COPD. Her mother had a stroke. She says: I am worried about joining research and would like the study information explained clearly.";
const labels: Record<string, string> = {
  patient: "Patient mention",
  negated: "Denied",
  family: "Family history",
  hypothetical: "Uncertain / hypothetical",
};

export default function ResearchPage() {
  const router = useRouter();
  const version = useRef(0);
  const [text, setText] = useState("");
  const [confirmed, setConfirmed] = useState(false);
  const [status, setStatus] = useState<AdvancedModelStatus | null>(null);
  const [analysis, setAnalysis] = useState<NoteUnderstanding | null>(null);
  const [entities, setEntities] = useState<DeepEntity[]>([]);
  const [question, setQuestion] = useState(
    "Which information is required for the asthma study?",
  );
  const [result, setResult] = useState<StudyEvidenceAnswer | null>(null);
  const [busy, setBusy] = useState("");
  const [error, setError] = useState("");
  useEffect(() => {
    if (!getCurrentUser()) {
      router.replace("/login");
      return;
    }
    getAdvancedModelStatus()
      .then(setStatus)
      .catch(() =>
        setError(
          "The advanced API could not be reached. Update the backend and follow the local setup guide.",
        ),
      );
  }, [router]);
  function updateText(value: string) {
    version.current += 1;
    setText(value);
    setAnalysis(null);
    setEntities([]);
    setResult(null);
    setError("");
  }
  async function understand() {
    const requestVersion = version.current;
    setBusy("analysis");
    setError("");
    setResult(null);
    try {
      const response = await analyzeNote(text);
      if (requestVersion === version.current) {
        setAnalysis(response);
        setEntities(
          response.entities.map((entity) => ({ ...entity, status: "pending" })),
        );
      }
    } catch (err) {
      if (requestVersion === version.current)
        setError(err instanceof Error ? err.message : "Analysis failed.");
    } finally {
      setBusy("");
    }
  }
  function decide(index: number, decision: "approved" | "rejected") {
    version.current += 1;
    setResult(null);
    setEntities((previous) =>
      previous.map((entity, i) =>
        i === index ? { ...entity, status: decision } : entity,
      ),
    );
  }
  const approved = entities.filter(
    (entity) =>
      entity.status === "approved" &&
      !entity.negated &&
      entity.context === "patient",
  );
  async function ask() {
    const requestVersion = version.current;
    setBusy("answer");
    setError("");
    setResult(null);
    try {
      const response = await askStudyEvidence(question, approved);
      if (requestVersion === version.current) setResult(response);
    } catch (err) {
      if (requestVersion === version.current)
        setError(
          err instanceof Error ? err.message : "Evidence search failed.",
        );
    } finally {
      setBusy("");
    }
  }
  const ready =
    status?.enabled &&
    status.dependencies_ready &&
    ["ner", "sentiment", "assertion"].every((task) =>
      status.models.some((model) => model.task === task && model.cached),
    );
  const ragReady =
    status?.enabled &&
    status.dependencies_ready &&
    ["embedding", "reranker", "generator"].every((task) =>
      status.models.some((model) => model.task === task && model.cached),
    );
  return (
    <article className="mx-auto max-w-5xl space-y-7 py-8">
      <p className="eyebrow">LOCAL TEXT UNDERSTANDING & STUDY EVIDENCE</p>
      <h1 className="text-4xl font-semibold tracking-tight">
        Read the visit.
        <br />
        Review the terms. Check the source.
      </h1>
      <p className="max-w-3xl leading-7 text-gray-600">
        Biomedical transformers suggest terms, a second model checks their
        context, and retrieval finds study evidence. Approve each patient term
        before asking a study question. This research desk does not save a visit
        or send a referral.
      </p>
      {status && (!ready || !ragReady) && (
        <section
          role="status"
          className="rounded-2xl border border-amber-200 bg-amber-50 p-6"
        >
          <h2 className="font-semibold">Local model setup is needed</h2>
          <p className="mt-2 leading-7">
            Enable ADVANCED_NLP_ENABLED and cache the pinned models. No hosted
            AI API is used. First downloads and CPU warm-up can take several
            minutes.
          </p>
          <a
            className="mt-3 inline-block underline"
            href="https://github.com/Kotlasuhasreddy123/Project-OmniMatch/blob/main/docs/ADVANCED_NLP_AND_RAG.md"
          >
            Open setup instructions →
          </a>
        </section>
      )}
      {error && (
        <p role="alert" className="rounded-xl bg-rose-50 p-5 text-rose-900">
          {error}
        </p>
      )}
      <section className="rounded-2xl border bg-white p-6">
        <p className="eyebrow">01 · UNDERSTAND A FICTIONAL NOTE</p>
        <label className="mt-4 block font-semibold" htmlFor="research-note">
          Visit text
        </label>
        <textarea
          id="research-note"
          value={text}
          maxLength={12000}
          rows={7}
          onChange={(event) => updateText(event.target.value)}
          className="mt-3 w-full rounded-xl border p-4 leading-7"
          placeholder="Paste a fictional visit conversation or note. Do not enter real patient information."
        />
        <div className="mt-3 flex flex-wrap justify-between gap-3 text-sm text-gray-600">
          <span>{text.length} / 12,000 characters</span>
          <button
            className="underline"
            onClick={() => {
              updateText(example);
              setConfirmed(true);
            }}
          >
            Load a fictional example
          </button>
        </div>
        <label className="my-5 flex items-center gap-3 text-sm">
          <input
            type="checkbox"
            checked={confirmed}
            onChange={(event) => setConfirmed(event.target.checked)}
          />
          I confirm this note contains fictional information only.
        </label>
        <button
          onClick={understand}
          disabled={!text.trim() || !confirmed || !ready || Boolean(busy)}
          className="rounded-full bg-teal-700 px-6 py-3 font-semibold text-white disabled:opacity-40"
        >
          {busy === "analysis"
            ? "Reading with local models…"
            : "Analyze text with transformers"}
        </button>
      </section>
      {analysis && (
        <>
          <section className="rounded-2xl border border-indigo-200 bg-indigo-50 p-6">
            <h2 className="text-xl font-semibold">General language tone</h2>
            <p className="my-3 leading-7">
              {analysis.sentiment.meaning} These scores are uncalibrated model
              outputs.
            </p>
            <div className="grid gap-4 sm:grid-cols-3">
              {Object.entries(analysis.sentiment.scores).map(
                ([label, score]) => (
                  <div key={label} className="rounded-xl bg-white p-4">
                    <div className="flex justify-between text-sm capitalize">
                      <span>{label}</span>
                      <strong>{(score * 100).toFixed(1)}%</strong>
                    </div>
                    <div
                      className="mt-3 h-2 rounded-full bg-indigo-100"
                      aria-hidden="true"
                    >
                      <div
                        className="h-2 rounded-full bg-indigo-500"
                        style={{ width: `${score * 100}%` }}
                      />
                    </div>
                  </div>
                ),
              )}
            </div>
            {analysis.sentiment.partial && (
              <p className="mt-4 text-sm font-medium">
                Only the beginning of this note was used for tone analysis.
                Clinical term extraction scans the full allowed note.
              </p>
            )}
          </section>
          <section className="space-y-4 rounded-2xl border bg-white p-6">
            <p className="eyebrow">02 · YOUR REVIEW CONTROLS THE SEARCH</p>
            <h2 className="text-xl font-semibold">
              {approved.length} approved patient terms
            </h2>
            <p className="text-sm leading-6 text-gray-600">
              Rules and the biomedical model can disagree or miss details.
              Scores are not medical certainty. Family, denied and uncertain
              terms stay out of the patient query.
            </p>
            {entities.map((entity, index) => (
              <div
                key={`${entity.term}-${entity.start}-${index}`}
                className={`rounded-xl border p-4 ${entity.status === "approved" ? "border-teal-300 bg-teal-50" : "bg-slate-50"}`}
              >
                <div className="flex flex-wrap items-start justify-between gap-3">
                  <div>
                    <strong>{entity.term}</strong>
                    <p className="mt-1 text-sm text-gray-600">
                      {entity.entity_type} ·{" "}
                      {entity.source === "rules"
                        ? "Vocabulary rules"
                        : "Biomedical transformer"}{" "}
                      · {entity.negated ? "Denied" : labels[entity.context]}
                    </p>
                  </div>
                  {entity.context === "patient" && !entity.negated ? (
                    <div className="flex gap-2">
                      <button
                        disabled={Boolean(busy)}
                        aria-pressed={entity.status === "approved"}
                        onClick={() => decide(index, "approved")}
                        className="rounded-full border bg-white px-4 py-2"
                      >
                        Approve
                      </button>
                      <button
                        disabled={Boolean(busy)}
                        aria-pressed={entity.status === "rejected"}
                        onClick={() => decide(index, "rejected")}
                        className="rounded-full border bg-white px-4 py-2"
                      >
                        Reject
                      </button>
                    </div>
                  ) : (
                    <span className="rounded-full bg-amber-100 px-3 py-1 text-sm">
                      Excluded from patient search
                    </span>
                  )}
                </div>
              </div>
            ))}
            {entities.length === 0 && (
              <p>
                No supported findings were proposed. Review the wording and
                coverage before continuing.
              </p>
            )}
            <details className="rounded-xl bg-amber-50 p-4">
              <summary className="cursor-pointer font-medium">
                Second-model context review
              </summary>
              <p className="my-3 text-sm leading-6">
                {analysis.assertion_reviewed_count} located terms checked;{" "}
                {analysis.assertion_unreviewed_count} not checked. A
                disagreement is a review flag, not an automatic correction.
              </p>
              {analysis.assertion_reviews.map((review, index) => (
                <p key={index} className="my-2 text-sm">
                  {review.term}: rules say {labels[review.rule_label]}; NLI
                  suggests {labels[review.nli_label]}.{" "}
                  {review.disagreement
                    ? "Review disagreement."
                    : "Models agree."}{" "}
                  {review.low_separation ? "Model alternatives are close." : ""}
                </p>
              ))}
            </details>
          </section>
          <section className="rounded-2xl border bg-white p-6">
            <p className="eyebrow">03 · ASK THE STUDY RECORDS</p>
            <label
              htmlFor="study-question"
              className="mt-4 block text-xl font-semibold"
            >
              What information do you want to check?
            </label>
            <p className="my-3 text-sm leading-6 text-gray-600">
              Ask about indexed study requirements. Approved patient terms
              select the study candidates. Language tone never affects the
              search.
            </p>
            <textarea
              id="study-question"
              value={question}
              onChange={(event) => {
                version.current += 1;
                setQuestion(event.target.value);
                setResult(null);
              }}
              maxLength={400}
              rows={2}
              className="w-full rounded-xl border p-4"
            />
            <button
              onClick={ask}
              disabled={
                !ragReady ||
                approved.length === 0 ||
                question.trim().length < 3 ||
                Boolean(busy)
              }
              className="mt-4 rounded-full bg-slate-900 px-6 py-3 font-semibold text-white disabled:opacity-40"
            >
              {busy === "answer"
                ? "Retrieving and checking evidence…"
                : "Find a cited study answer"}
            </button>
          </section>
        </>
      )}
      {result && (
        <section
          aria-label="Study evidence result"
          className="space-y-5 rounded-2xl border border-teal-200 bg-teal-50 p-6"
        >
          <h2 className="text-2xl font-semibold">
            {result.abstained
              ? "More evidence is needed"
              : "Answer with source evidence"}
          </h2>
          <p className="whitespace-pre-wrap leading-8">{result.answer}</p>
          <p className="text-sm leading-6">
            Searched {result.scope.retrieved_studies} candidate studies
            {result.scope.passages_considered !== undefined
              ? ` and ${result.scope.passages_considered} passages`
              : ""}
            . This is not a search of the entire registry.{" "}
            {result.scope.passages_truncated
              ? "The passage limit was reached."
              : ""}
          </p>
          {result.generation_mode === "extractive_grounding_fallback" && (
            <p className="rounded-xl bg-white p-4 text-sm leading-6">
              The generated draft did not exactly preserve a whole source
              passage. The system returned cited excerpts instead.
            </p>
          )}
          {result.sources.map((source) => (
            <article
              key={source.source_id}
              className="rounded-xl border bg-white p-5"
            >
              <h3 className="font-semibold">
                [{source.source_id}] {source.title}
              </h3>
              <p className="mt-2 text-sm text-gray-600">
                {source.nct_id} · {source.section} ·{" "}
                {source.field.replaceAll("_", " ")}
              </p>
              <blockquote className="my-4 border-l-2 border-teal-500 pl-4 leading-7">
                {source.quote}
              </blockquote>
              {/^NCT\d{8}$/.test(source.nct_id) && (
                <a
                  className="text-sm underline"
                  href={`https://clinicaltrials.gov/study/${source.nct_id}`}
                  target="_blank"
                  rel="noreferrer"
                >
                  Open registry record ↗
                </a>
              )}
              <details className="mt-3 text-xs text-gray-600">
                <summary className="cursor-pointer">
                  Check source provenance
                </summary>
                <p className="mt-2 break-all">
                  Character range {source.start}–{source.end}; SHA-256{" "}
                  {source.quote_sha256}
                </p>
              </details>
            </article>
          ))}
        </section>
      )}
      <div className="flex flex-wrap gap-5 text-sm">
        <Link href="/session" className="underline">
          Open the regular visit workflow →
        </Link>
        <Link href="/models" className="underline">
          Models and measured limitations →
        </Link>
      </div>
    </article>
  );
}
