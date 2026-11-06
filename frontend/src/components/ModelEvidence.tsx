import evidence from "@/data/modelEvidence.json";
const percent = (value: number) => `${(value * 100).toFixed(1)}%`;

export function ModelEvidence() {
  return (
    <section className="space-y-5" aria-label="Measured model and rule results">
      <div className="rounded-2xl border bg-white p-6">
        <p className="eyebrow">ACTIVE RULE PIPELINE · DEVELOPMENT BENCHMARK</p>
        <h2 className="mt-3 text-xl font-semibold">
          Broader vocabulary. More findings captured.
        </h2>
        <p className="my-4 leading-7 text-gray-600">
          Same {evidence.broad_records} synthetic transcripts, before and after
          rule improvements. These are development results using legacy term
          matching, not unseen clinical accuracy.
        </p>
        <div className="grid gap-6 sm:grid-cols-3">
          {(["precision", "recall", "f1"] as const).map((metric) => (
            <figure
              key={metric}
              className="space-y-3 rounded-xl bg-slate-50 p-4"
            >
              <figcaption className="font-semibold capitalize">
                Negation {metric === "f1" ? "F1" : metric}
              </figcaption>
              {[
                ["Before", evidence.broad_before[metric], "bg-slate-400"],
                ["Now", evidence.broad_after[metric], "bg-teal-600"],
              ].map(([label, value, color]) => (
                <div key={String(label)}>
                  <div className="mb-1 flex justify-between text-sm">
                    <span>{label}</span>
                    <strong>{percent(Number(value))}</strong>
                  </div>
                  <div
                    className="h-2 rounded-full bg-slate-200"
                    aria-hidden="true"
                  >
                    <div
                      className={`h-2 rounded-full ${color}`}
                      style={{ width: percent(Number(value)) }}
                    />
                  </div>
                </div>
              ))}
            </figure>
          ))}
        </div>
        <p className="mt-5 rounded-xl bg-amber-50 p-4 text-sm leading-6 text-amber-950">
          The broad 95% recall target is still unmet. The separate 72/72 focused
          checks do not replace this result or establish 98% medical accuracy.
        </p>
      </div>
      <div className="rounded-2xl border border-indigo-200 bg-indigo-50 p-6">
        <p className="eyebrow">NEWLY TRAINED · EXPERIMENTAL CANDIDATE</p>
        <h2 className="mt-3 text-3xl font-semibold">
          {percent(evidence.candidate_accuracy)} internal context accuracy
        </h2>
        <p className="mt-3 leading-7">
          {evidence.candidate_correct} of {evidence.candidate_total} supplied
          term spans classified correctly across{" "}
          {evidence.split_record_counts.test} synthetic test records. This model
          classifies context after a term is located; it does not find all
          medical terms. It is not used by the live app.
        </p>
        <p className="mt-3 text-sm leading-6">
          Training / validation / test: {evidence.split_annotation_counts.train}{" "}
          / {evidence.split_annotation_counts.validation} /{" "}
          {evidence.split_annotation_counts.test} annotations, separated by
          record. Only {evidence.candidate_family_test_count} family-history
          test example; more independently reviewed data is needed.
        </p>
        <p className="mt-4 rounded-xl bg-white p-4 text-sm leading-6">
          Additional check: {percent(evidence.extra_accuracy)} ({evidence.extra_correct}/{evidence.extra_total}) on a different existing set of {evidence.extra_records} synthetic notes, using the same frozen model. This smaller classroom check has different difficulty; it does not replace the 90.0% internal result or establish 98% across the application.
        </p>
        <p className="mt-4 font-semibold text-indigo-950">
          98% minimum: not achieved. Whisper speech and study-search accuracy
          remain unmeasured.
        </p>
      </div>
    </section>
  );
}
