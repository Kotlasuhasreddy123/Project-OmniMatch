import Link from "next/link";
import { ModelEvidence } from "@/components/ModelEvidence";

const rows = [
  [
    "Whisper base",
    "Active · pretrained",
    "Speech → reviewed transcript",
    "Publisher-trained multilingual speech weights. No project fine-tuning; clinical word error rate is not measured.",
  ],
  [
    "all-MiniLM-L6-v2",
    "Active · pretrained",
    "Approved terms → study search vectors",
    "384-dimensional text encoder. Published weights are unchanged; trial-retrieval relevance is not independently measured.",
  ],
  [
    "English vocabulary + context rules",
    "Active · programmed",
    "Find supported terms and their context",
    "Rules cover negation, family history and hypothetical/uncertain language. They are not a trained medical NER model.",
  ],
  [
    "TF-IDF + logistic regression",
    "New · experimental only",
    "Known term span → affirmed / negated / family",
    "Fitted on synthetic classroom annotations with record-separated partitions. Below the requested 98%; not connected to the live API.",
  ],
  [
    "NLI MiniLM wrapper",
    "Unused experiment",
    "Optional assertion experiment",
    "The checkpoint named in legacy biobert_v3.py is cross-encoder/nli-MiniLM2-L6-H768, not BioBERT. No local medical validation.",
  ],
];
export default function ModelsPage() {
  return (
    <article className="mx-auto max-w-5xl space-y-8 py-8">
      <p className="eyebrow">MODELS & TRAINING · OPEN EVIDENCE</p>
      <h1 className="text-4xl font-semibold tracking-tight">
        What runs. What learned.
        <br />
        What still needs proof.
      </h1>
      <p className="max-w-3xl leading-7 text-gray-600">
        Speech recognition, term extraction and study search are different
        tasks. A ranking score is not accuracy, and a small text test does not
        validate medical speech or all specialties.
      </p>
      <div className="space-y-4">
        {rows.map(([name, status, purpose, detail]) => (
          <section key={name} className="rounded-2xl border bg-white p-6">
            <div className="flex flex-wrap items-center justify-between gap-3">
              <h2 className="text-xl font-semibold">{name}</h2>
              <span className="rounded-full bg-teal-50 px-3 py-1 text-sm text-teal-900">
                {status}
              </span>
            </div>
            <p className="mt-3 font-medium">{purpose}</p>
            <p className="mt-2 leading-7 text-gray-600">{detail}</p>
          </section>
        ))}
      </div>
      <ModelEvidence />
      <p className="rounded-2xl bg-amber-50 p-6 leading-7">
        spaCy is installed but no trained spaCy medical model is loaded by the
        live endpoint. Qdrant is a database. Eligibility scores and the
        standalone rule experiments have no learned diagnostic weights. No
        disease-forecasting or prescribing model is installed.
      </p>
      <div className="flex flex-wrap gap-5">
        <a
          href="https://github.com/Kotlasuhasreddy123/Project-OmniMatch/blob/main/docs/MODEL_TRAINING_RESULTS.md"
          className="text-teal-800 underline"
        >
          Data, parameters, results and training commands →
        </a>
        <Link href="/validation" className="text-teal-800 underline">
          Specialty and language coverage →
        </Link>
      </div>
    </article>
  );
}
