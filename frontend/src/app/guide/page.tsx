import Link from "next/link";
export default function GuidePage() {
  return (
    <article className="mx-auto max-w-3xl space-y-8 py-10">
      <p className="eyebrow">YOUR RESEARCH WORKSPACE</p>
      <h1 className="text-4xl font-semibold tracking-tight">
        From conversation to review.
      </h1>
      <section id="study-data">
        <h2 className="text-2xl font-semibold">Understand the data</h2>
        <p className="mt-4 leading-7">
          Use fictional patient details. Sample studies exercise the software
          workflow. A study suggestion requires a person to verify its criteria
          and current recruitment information. The review score helps order
          suggestions; it is not a probability of enrollment.
          The bundled study records are fictional. They are not past patient
          cases or forecasts. For registry-backed records, check each study’s
          listed locations and eligibility rules; a suggested study does not
          establish citizenship, travel or enrollment eligibility.
        </p>
      </section>
      <section id="models" className="rounded-2xl bg-white p-6">
        <h2 className="text-2xl font-semibold">Which models are running?</h2>
        <dl className="mt-5 space-y-5">
          <div>
            <dt className="font-semibold">Speech → Whisper base by default</dt>
            <dd className="mt-1 leading-7 text-gray-600">
              OpenAI trained this model family on 680,000 hours of audio and
              transcripts. We use its published weights locally. Your
              administrator can change the Whisper size in configuration.
            </dd>
          </div>
          <div>
            <dt className="font-semibold">Study search → all-MiniLM-L6-v2</dt>
            <dd className="mt-1 leading-7 text-gray-600">
              A pretrained text encoder fine-tuned by its authors on over one
              billion sentence pairs, including scientific text and
              question-answer data. It compares text in 384 dimensions. Indexing
              studies does not retrain it.
            </dd>
          </div>
          <div>
            <dt className="font-semibold">
              Medical terms and criteria → programmed rules
            </dt>
            <dd className="mt-1 leading-7 text-gray-600">
              Our active extractor uses vocabulary and context patterns. It does
              not load a trained spaCy medical model. Human approval remains
              part of the workflow.
            </dd>
          </div>
        </dl>
        <p className="mt-5 text-sm leading-6 text-gray-600">
          We trained a separate experimental context classifier on synthetic
          annotations; it is not active in the visit pipeline. The optional
          Research workspace adds pretrained medical NER, context review and
          source-grounded answers. None of these results establish accuracy
          across all medical specialties or languages.
        </p>
        <a
          className="mt-4 inline-block text-teal-800 underline"
          href="https://github.com/Kotlasuhasreddy123/Project-OmniMatch/blob/main/docs/MODELS_AND_DATA.md"
        >
          Read the original training sources and our evaluation results →
        </a>
      </section>
      <section>
        <h2 className="text-2xl font-semibold">Try the workflow</h2>
        <ol className="mt-4 list-decimal space-y-3 pl-5">
          <li>Give the fictional patient a label such as DEMO-001, then grant consent before recording.</li>
          <li>Speak a fictional medical history and check the transcript.</li>
          <li>Approve or reject each extracted term.</li>
          <li>Complete the visit and open the inbox.</li>
          <li>
            Use the visual overview to compare suggestions, then open a visit to
            inspect evidence and missing information.
          </li>
          <li>For later information, start another visit with the same patient label. History keeps each visit separate, including visits on the same day.</li>
          <li>After reviewing a visit, archive it to clear the inbox. The saved record stays in history and can be restored.</li>
        </ol>
      </section>
      <section>
        <h2 className="text-2xl font-semibold">Install it on your computer</h2>
        <p className="mt-4 leading-7">
          Run the app, models and database locally with Docker. No AWS account
          or paid API key is required. The first build downloads the published
          model weights.
        </p>
        <a
          className="mt-4 inline-block text-teal-800 underline"
          href="https://github.com/Kotlasuhasreddy123/Project-OmniMatch/blob/main/docs/INSTALL_ON_YOUR_COMPUTER.md"
        >
          Windows, macOS and Linux installation guide →
        </a>
      </section>
      <Link
        className="inline-block rounded-full bg-teal-700 px-6 py-3 text-white"
        href="/session"
      >
        Start a visit →
      </Link>
    </article>
  );
}
