import Link from "next/link";

const sections = [
  [
    "Terms of use",
    "OmniMatch is operated by Suhas Reddy Kotla as a synthetic-data academic research application. Use it only if you are legally able to agree to these terms. Access can be suspended for misuse, security concerns or an ended research program. Features can change or become unavailable. The software is supplied under its published license without warranties, subject to rights and liabilities that applicable law does not allow us to exclude. It is not offered for clinical diagnosis, prescribing, emergency decisions or patient enrollment decisions.",
  ],
  [
    "Privacy notice",
    "The public website serves documentation and interface files through GitHub Pages. GitHub can process request metadata such as IP address and browser details under its own privacy policy. Account registration, email delivery, identity verification, organization membership and sessions are handled by WorkOS when configured. Your signup email and account information are used to review access and operate accounts. The public site does not receive clinical audio or visit notes. No analytics or advertising SDK is added by OmniMatch.",
  ],
  [
    "Local data and model handling",
    "The installed application processes synthetic audio in memory and sends it to its local Whisper service. Approved information, visit results and audit events are stored in the installation’s database; study vectors are stored in local Qdrant. The browser may retain the current transcript or review state in session storage. The public portal does not process those visits. Model downloads contact the model providers on first use. External registry links or optional sync/webhook settings contact the services chosen by the installation owner. User inputs are not used to train model weights automatically.",
  ],
  [
    "Retention and deletion",
    "Local database records and model caches persist until the installation owner deletes them. Marking reviewed or archiving does not erase a record. The browser’s session storage normally ends with its tab/session; WorkOS browser-mode refresh state can persist until sign-out or storage clearing. WorkOS account records remain while the account is active; the operator reviews deletion requests through the contact below and performs provider-side account deletion when appropriate. Provider security/operational logs follow the provider’s retention terms. No automatic 30- or 90-day deletion schedule is currently implemented. Contact the operator for access, correction, export or deletion requests; applicable legal rights remain available.",
  ],
  [
    "AI disclosure and limits",
    "Whisper and MiniLM are pretrained general models. Clinical extraction and eligibility checks use programmed rules and a limited study catalog. Ranking scores order suggestions and are not disease probabilities, diagnostic accuracy, or chances of enrollment. The example-results page labels its invented display values. Clinical validation across every specialty and language has not been completed. No future disease forecast or medicine recommendation is generated.",
  ],
  [
    "Acceptable use",
    "Use synthetic examples only. Do not upload real patient records, patient identifiers, recordings of real consultations, trade secrets, illegal content, harassment, malware, or material you lack permission to use. Your registration email is permitted account data. Do not impersonate a clinician, bypass access checks, spam access requests, probe another user’s installation without authorization, or present research scores as medical advice. Do not upload hate or exploitative material. Report concerns without including sensitive case details.",
  ],
  [
    "Human oversight",
    "A person reviews the transcript and explicitly approves or rejects each extracted term before matching. Review every suggestion and unresolved criterion against its source. Missing information is not evidence that a criterion is satisfied. A flagged extraction error should be corrected or rejected; stop the workflow if the result cannot be reviewed reliably.",
  ],
  [
    "Content and incident reporting",
    "This application is a constrained research workflow rather than an unrestricted chatbot. Input size limits and account permissions provide basic controls; no comprehensive automated hate-content or clinical-safety classifier is claimed. Use the contact link to report abuse, incorrect results or vulnerabilities. The operator investigates, can suspend accounts or disable access, and coordinates fixes and notifications where required. Do not send passwords, access tokens or patient information in a report.",
  ],
  [
    "Intellectual property and licenses",
    "You retain the rights you already have in your inputs. We do not claim ownership of your inputs or reviewed notes. Rights in generated outputs depend on applicable law and underlying rights; originality and accuracy are not guaranteed. OmniMatch source is public under MIT; libraries and model weights retain their own licenses. Account approval does not override the public source license or prevent others from copying or modifying the source. See the license notices for details.",
  ],
  [
    "Account access and sessions",
    "WorkOS signup requests are reviewed by the owner. Approved users receive invitations and must receive the required organization permissions before local API access. Existing accounts and organization provisioning settings must also be reviewed by the owner. Password and social providers must be disabled in the provider dashboard for email-code-only access. Revoking a role/session may take until an already-issued access token expires to affect a local API; configure short token lifetimes. Public client-only authentication uses provider-managed browser storage; signing out and using a trusted browser matter.",
  ],
];

export default function PoliciesPage() {
  return (
    <article className="mx-auto max-w-4xl space-y-7 py-8">
      <p className="eyebrow">POLICIES & TRANSPARENCY</p>
      <h1 className="text-4xl font-semibold tracking-tight">
        Know what you share.
        <br />
        Know what the system does.
      </h1>
      <p className="leading-7 text-gray-600">
        Effective November 5, 2026. These notices describe the implemented
        research application. They are not a certification of GDPR, CCPA, HIPAA
        or medical-device compliance.
      </p>
      {sections.map(([title, text]) => (
        <section key={title} className="rounded-2xl border bg-white p-6">
          <h2 className="text-xl font-semibold">{title}</h2>
          <p className="mt-3 leading-7 text-gray-600">{text}</p>
        </section>
      ))}
      <section className="rounded-2xl bg-teal-50 p-6">
        <h2 className="text-xl font-semibold">Contact the operator</h2>
        <p className="mt-3">
          Suhas Reddy Kotla ·{" "}
          <a className="underline" href="mailto:suhasreddykotla222@gmail.com">
            suhasreddykotla222@gmail.com
          </a>
        </p>
        <p className="mt-3 leading-7">
          For account requests, privacy requests, an incorrect result or
          security concerns. Please send only the minimum details needed; omit
          patient information and credentials.
        </p>
      </section>
      <p className="text-sm leading-6 text-gray-600">
        Provider notices:{" "}
        <a
          href="https://docs.github.com/en/site-policy/privacy-policies/github-general-privacy-statement"
          className="underline"
        >
          GitHub privacy
        </a>{" "}
        ·{" "}
        <a href="https://workos.com/legal/privacy" className="underline">
          WorkOS privacy
        </a>
        . Governance references:{" "}
        <a
          href="https://www.nist.gov/itl/ai-risk-management-framework"
          className="underline"
        >
          NIST AI RMF
        </a>{" "}
        and{" "}
        <a
          href="https://ico.org.uk/for-organisations/uk-gdpr-guidance-and-resources/artificial-intelligence/guidance-on-ai-and-data-protection/how-do-we-ensure-transparency-in-ai/"
          className="underline"
        >
          ICO AI transparency guidance
        </a>
        .
      </p>
      <Link href="/licenses" className="inline-block text-teal-800 underline">
        Software and model licenses →
      </Link>
    </article>
  );
}
