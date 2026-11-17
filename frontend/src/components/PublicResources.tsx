import Link from "next/link";

export function PublicResources() {
  return (
    <section aria-labelledby="public-resources-heading" className="rounded-3xl border border-teal-100 bg-teal-50/70 p-6">
      <p className="text-xs font-semibold uppercase tracking-widest text-teal-700">Open to everyone</p>
      <h2 id="public-resources-heading" className="mt-2 text-2xl font-semibold">Explore without waiting for approval</h2>
      <p className="mt-2 text-sm leading-6 text-gray-600">No account is needed for these resources. Approval is required only for the protected workspace and saved visits.</p>
      <div className="mt-5 grid gap-3 sm:grid-cols-3">
        {[
          ["/preview", "Sample results", "Explore charts, study suggestions and visit comparisons."],
          ["/guide", "Installation guide", "Learn the workflow and set up your own computer."],
          ["/models", "Models and data", "See what the models do and what was measured."],
        ].map(([href, title, detail]) => (
          <Link key={href} href={href} className="rounded-2xl border border-teal-100 bg-white p-4 transition hover:border-teal-500 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-teal-600">
            <span className="font-semibold text-teal-900">{title} →</span>
            <span className="mt-2 block text-sm leading-6 text-gray-600">{detail}</span>
          </Link>
        ))}
      </div>
      <a href="https://github.com/Kotlasuhasreddy123/Project-OmniMatch" className="mt-4 inline-block rounded text-sm font-medium text-teal-800 underline focus-visible:ring-2 focus-visible:ring-teal-600">Download the source and read the setup instructions ↗</a>
    </section>
  );
}
