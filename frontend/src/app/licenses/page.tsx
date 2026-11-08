import Link from "next/link";
const components = [
  [
    "Medical-NER (DeBERTa)",
    "MIT (publisher-declared)",
    "https://huggingface.co/blaze999/Medical-NER",
  ],
  [
    "NLI MiniLM",
    "Apache-2.0",
    "https://huggingface.co/cross-encoder/nli-MiniLM2-L6-H768",
  ],
  [
    "DistilBERT sentiment student",
    "Apache-2.0",
    "https://huggingface.co/lxyuan/distilbert-base-multilingual-cased-sentiments-student",
  ],
  [
    "MS MARCO MiniLM reranker",
    "Apache-2.0",
    "https://huggingface.co/cross-encoder/ms-marco-MiniLM-L6-v2",
  ],
  [
    "FLAN-T5 small",
    "Apache-2.0",
    "https://huggingface.co/google/flan-t5-small",
  ],
  [
    "Transformers library",
    "Apache-2.0",
    "https://github.com/huggingface/transformers/blob/main/LICENSE",
  ],
  [
    "OmniMatch source",
    "MIT",
    "https://github.com/Kotlasuhasreddy123/Project-OmniMatch/blob/main/LICENSE",
  ],
  [
    "Whisper code and weights",
    "MIT",
    "https://github.com/openai/whisper/blob/main/LICENSE",
  ],
  [
    "all-MiniLM-L6-v2 weights",
    "Apache-2.0",
    "https://huggingface.co/sentence-transformers/all-MiniLM-L6-v2",
  ],
  [
    "Sentence Transformers",
    "Apache-2.0",
    "https://github.com/huggingface/sentence-transformers/blob/main/LICENSE",
  ],
  [
    "Qdrant",
    "Apache-2.0",
    "https://github.com/qdrant/qdrant/blob/master/LICENSE",
  ],
  ["FastAPI", "MIT", "https://github.com/fastapi/fastapi/blob/master/LICENSE"],
  [
    "PyTorch",
    "BSD-3-Clause and third-party notices",
    "https://github.com/pytorch/pytorch/blob/main/LICENSE",
  ],
  [
    "React / Next.js / Recharts",
    "MIT",
    "https://github.com/recharts/recharts/blob/main/LICENSE",
  ],
  [
    "Lucide icons",
    "ISC",
    "https://github.com/lucide-icons/lucide/blob/main/LICENSE",
  ],
  [
    "WorkOS AuthKit browser SDK",
    "MIT; hosted service has separate terms",
    "https://github.com/workos/authkit-js/blob/main/LICENSE",
  ],
];
export default function LicensesPage() {
  return (
    <article className="mx-auto max-w-4xl space-y-7 py-8">
      <p className="eyebrow">OPEN SOURCE & MODEL NOTICES</p>
      <h1 className="text-4xl font-semibold tracking-tight">
        Built with open tools.
        <br />
        Respecting their licenses.
      </h1>
      <p className="leading-7 text-gray-600">
        The project license applies to OmniMatch code. Dependencies, model
        weights and hosted services retain their own terms. Keep their copyright
        and license notices when redistributing. Approval of an account does not
        change the rights granted by the public source license.
      </p>
      <div className="overflow-x-auto rounded-2xl border bg-white">
        <table className="w-full text-left text-sm">
          <caption className="sr-only">
            Core components and license references
          </caption>
          <thead className="bg-teal-50">
            <tr>
              <th className="p-4">Component</th>
              <th className="p-4">License / terms</th>
            </tr>
          </thead>
          <tbody>
            {components.map(([name, license, url]) => (
              <tr key={name} className="border-t">
                <th scope="row" className="p-4 font-medium">
                  {name}
                </th>
                <td className="p-4">
                  <a className="text-teal-800 underline" href={url}>
                    {license} ↗
                  </a>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      <p className="leading-7 text-gray-600">
        The detailed frontend notice file includes license text from installed
        production packages. Backend distributions retain dependency license
        files in their installed packages. Optional platform binaries and
        additional dependencies must retain their own accompanying notices.
      </p>
      <a
        className="inline-block rounded-full bg-teal-700 px-6 py-3 text-white"
        href={`${process.env.NEXT_PUBLIC_BASE_PATH || ""}/third-party-notices.txt`}
      >
        Read bundled frontend notices
      </a>
      <p className="text-sm leading-6 text-gray-600">
        WorkOS and GitHub hosting are services governed by their respective
        terms, even when a free tier is used. No license or third-party brand
        implies endorsement of OmniMatch. No medical regulatory approval is
        represented.
      </p>
      <Link href="/policies" className="inline-block underline">
        Privacy and acceptable use →
      </Link>
    </article>
  );
}
