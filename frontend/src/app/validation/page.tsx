"use client";
import { useState } from "react";
import Link from "next/link";
import { ModelEvidence } from "@/components/ModelEvidence";

const specialties = [
  "Primary care",
  "Cardiology",
  "Endocrinology",
  "Pulmonology",
  "Neurology",
  "Oncology",
  "Psychiatry",
  "Dermatology",
  "Gastroenterology",
  "Nephrology",
  "Rheumatology",
  "Hematology",
  "Infectious diseases",
  "Pediatrics",
  "Obstetrics and gynecology",
  "Surgery",
  "Ophthalmology",
  "ENT",
  "Urology",
  "Orthopedics",
  "Geriatrics",
  "Emergency medicine",
];
const languages = [
  "English",
  "Spanish",
  "Hindi",
  "Telugu",
  "French",
  "Arabic",
  "Mandarin Chinese",
  "Bengali",
  "Portuguese",
  "Russian",
  "Urdu",
  "German",
  "Japanese",
  "Tamil",
  "Other language / dialect",
];
export default function ValidationPage() {
  const [specialty, setSpecialty] = useState(specialties[0]);
  const [language, setLanguage] = useState(languages[0]);
  return (
    <article className="mx-auto max-w-5xl space-y-7 py-8">
      <p className="eyebrow">VALIDATION YOU CAN INSPECT</p>
      <h1 className="text-4xl font-semibold tracking-tight">
        Evidence before an accuracy claim.
      </h1>
      <p className="max-w-3xl leading-7 text-gray-600">
        Every specialty and language needs its own representative, independently
        labeled evaluation. This coverage register makes the gaps visible. Its
        categories are a planning list, not an exhaustive medical or linguistic
        taxonomy.
      </p>
      <div className="grid gap-4 sm:grid-cols-3">
        {[
          ["72 / 72", "Synthetic target-context checks", "bg-teal-50"],
          ["69", "English text regression examples", "bg-indigo-50"],
          [
            "Not demonstrated",
            "Requested 98–100% model accuracy",
            "bg-amber-50",
          ],
        ].map(([n, label, color]) => (
          <div key={label} className={`rounded-2xl p-6 ${color}`}>
            <strong className="block text-2xl">{n}</strong>
            <span className="mt-2 block text-sm">{label}</span>
          </div>
        ))}
      </div>
      <ModelEvidence />
      <section className="rounded-2xl border bg-white p-6">
        <h2 className="text-xl font-semibold">Check a use case</h2>
        <div className="my-5 grid gap-5 sm:grid-cols-2">
          <label className="text-sm font-medium">
            Specialty
            <select
              value={specialty}
              onChange={(e) => setSpecialty(e.target.value)}
              className="mt-2 block w-full rounded-xl border p-3"
            >
              {specialties.map((s) => (
                <option key={s}>{s}</option>
              ))}
            </select>
          </label>
          <label className="text-sm font-medium">
            Language
            <select
              value={language}
              onChange={(e) => setLanguage(e.target.value)}
              className="mt-2 block w-full rounded-xl border p-3"
            >
              {languages.map((l) => (
                <option key={l}>{l}</option>
              ))}
            </select>
          </label>
        </div>
        <div
          role="status"
          className="rounded-xl border border-amber-200 bg-amber-50 p-5"
        >
          <h3 className="font-semibold">
            {specialty} · {language}: clinical validation not established
          </h3>
          <p className="mt-2 leading-7">
            {language === "English"
              ? "Some English context rules have synthetic regression coverage. That does not validate this specialty, medical speech, full entity extraction or trial matching."
              : "No measured evaluation set is included for this language. Whisper’s language support does not validate the English-only extraction rules in this language."}
          </p>
        </div>
      </section>
      <div className="grid gap-4 sm:grid-cols-2">
        {[
          [
            "🎙️",
            "Medical speech",
            "Word error rate has not been measured on a representative clinical recording set.",
          ],
          [
            "🔎",
            "Study retrieval",
            "Recall at k and ranking relevance need independently reviewed patient-study pairs.",
          ],
          [
            "🧾",
            "Clinical context",
            "72 expected term/context checks pass on synthetic development examples; this is not held-out NER F1.",
          ],
          [
            "📈",
            "Future probabilities",
            "No validated forecasting model is installed. Study ranking scores must not be interpreted as future disease risk.",
          ],
        ].map(([icon, title, text]) => (
          <section key={title} className="rounded-2xl border bg-white p-6">
            <span aria-hidden="true" className="text-2xl">
              {icon}
            </span>
            <h2 className="my-3 font-semibold">{title}</h2>
            <p className="leading-7 text-gray-600">{text}</p>
          </section>
        ))}
      </div>
      <p className="leading-7 text-gray-600">
        Thresholds can change how many studies are retrieved, but do not
        establish accuracy. Fine-tuning needs data rights, reviewed labels,
        patient/source-separated development and test sets, and a measured
        improvement over the existing model. The separately trained context
        candidate remains experimental and below the requested target.
      </p>
      <div className="flex flex-wrap gap-5">
        <a
          className="text-teal-800 underline"
          href="https://github.com/Kotlasuhasreddy123/Project-OmniMatch/blob/main/docs/MODELS_AND_DATA.md"
        >
          Training sources and measured results →
        </a>
        <Link href="/preview" className="text-teal-800 underline">
          Explore results layout →
        </Link>
      </div>
    </article>
  );
}
