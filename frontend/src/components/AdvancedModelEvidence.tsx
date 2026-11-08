import Link from "next/link";
import evidence from "@/data/advancedEvidence.json";
const names: Record<string, string> = {
  ner: "Medical term proposals",
  sentiment: "General language tone",
  assertion: "Context second opinion",
  embedding: "Dense evidence retrieval",
  reranker: "BERT-family reranking",
  generator: "Local draft generation",
};

export function AdvancedModelEvidence() {
  const rows = [
    [
      "Hybrid target/context checks",
      evidence.target_context_hybrid,
      "Expected targets present; not full NER F1",
    ],
    [
      "NLI context labels",
      evidence.nli,
      "Advisory; never automatic corrections",
    ],
    [
      "General tone top labels",
      evidence.tone,
      "General wording; not clinical state",
    ],
    [
      "RAG source or abstention",
      evidence.rag,
      "Fixed three-study fictional corpus",
    ],
  ] as const;
  return (
    <section className="space-y-6 rounded-3xl border border-teal-200 bg-gradient-to-br from-teal-50 via-white to-indigo-50 p-6 sm:p-8">
      <p className="eyebrow">
        OPTIONAL LOCAL TRANSFORMER MODE · REAL CHECKPOINT TESTS
      </p>
      <h2 className="text-3xl font-semibold tracking-tight">
        Medical text to evidence.
        <br />
        With a person in control.
      </h2>
      <div className="flex flex-wrap gap-2 text-sm">
        {[
          "Read English note",
          "Propose terms",
          "Approve each term",
          "Retrieve + rerank",
          "Check cited excerpts",
        ].map((step, index) => (
          <span key={step} className="rounded-xl border bg-white px-4 py-3">
            <strong className="mr-2 text-teal-700">{index + 1}</strong>
            {step}
          </span>
        ))}
      </div>
      <p className="leading-7 text-gray-600">
        DeBERTa medical NER, NLI context review, DistilBERT tone analysis and
        local retrieval-augmented generation are available after installation
        and configuration. They use published weights; they were not fine-tuned
        here. Default visit extraction remains the rule pipeline.
      </p>
      <div className="grid gap-4 sm:grid-cols-2">
        {rows.map(([title, metric, limit]) => (
          <article key={title} className="rounded-2xl border bg-white p-5">
            <h3 className="font-semibold">{title}</h3>
            <p className="my-3 text-3xl font-semibold">
              {metric.correct}/{metric.total}
            </p>
            <div className="h-2 rounded-full bg-slate-100" aria-hidden="true">
              <div
                className="h-2 rounded-full bg-teal-600"
                style={{ width: `${metric.fraction * 100}%` }}
              />
            </div>
            <p className="mt-3 text-sm leading-6 text-gray-600">{limit}</p>
          </article>
        ))}
      </div>
      <p className="text-sm leading-7">
        On the new target-term fixture, rules alone found{" "}
        {evidence.target_context_rules.correct}/
        {evidence.target_context_rules.total}. Hybrid proposals found{" "}
        {evidence.target_context_hybrid.correct}/
        {evidence.target_context_hybrid.total}. The tone model has{" "}
        {evidence.tone.unclear_count} unclear-display cases; sparse
        developer-authored examples do not establish language or specialty
        coverage.
      </p>
      <section className="rounded-2xl bg-white p-5">
        <h3 className="font-semibold">
          Generation is checked against the source
        </h3>
        <p className="mt-3 text-sm leading-7">
          {evidence.citations.correct}/{evidence.citations.total} returned
          citations matched their original source slices and hashes. This is a
          mechanical integrity check, not medical accuracy.{" "}
          {evidence.verified_generated_quotes} generated whole-passage quotes
          passed the gate; {evidence.extractive_fallbacks} drafts used the
          explicit cited-excerpt fallback.
        </p>
      </section>
      <details className="rounded-2xl border bg-white p-5">
        <summary className="cursor-pointer font-semibold">
          Exact pretrained models
        </summary>
        <ul className="mt-4 space-y-3 text-sm">
          {Object.entries(evidence.models).map(([task, model]) => (
            <li key={task}>
              <strong>{names[task]}</strong>
              <br />
              <a
                className="break-all text-teal-800 underline"
                href={`https://huggingface.co/${model.id}`}
              >
                {model.id}
              </a>
              <span className="block break-all text-xs text-gray-500">
                Pinned revision {model.revision}
              </span>
            </li>
          ))}
        </ul>
      </details>
      <p className="rounded-xl bg-amber-50 p-4 text-sm leading-7">
        98% across the application is not established. These are small synthetic
        development checks. No inference of diagnosis, future disease,
        prescription or enrollment is made.
      </p>
      <div className="flex flex-wrap gap-5 text-sm">
        <Link
          href="/research"
          className="rounded-full bg-teal-700 px-5 py-3 font-medium text-white"
        >
          Open local text & evidence workspace →
        </Link>
        <a
          className="py-3 underline"
          href="https://github.com/Kotlasuhasreddy123/Project-OmniMatch/blob/main/docs/ADVANCED_NLP_AND_RAG.md"
        >
          Setup, models and measured limits →
        </a>
      </div>
    </section>
  );
}
