import Link from "next/link";
import { ArrowUpRight } from "lucide-react";

export function PublicResources() {
  return <section aria-labelledby="public-resources-heading">
    <h2 id="public-resources-heading" className="text-base font-semibold tracking-tight">Explore without waiting for approval</h2>
    <p className="mt-1 text-xs leading-6 text-slate-600">These resources are public. Saved visits require an approved account and the installed app.</p>
    <div className="resource-cards">
      {[
        ["/preview", "Sample results", "See how study scores and evidence are presented."],
        ["/guide", "Installation guide", "Set up OmniMatch and follow your first visit."],
        ["/models", "Models and data", "Understand the AI, data sources and measured results."],
      ].map(([href,title,detail]) => <Link key={href} href={href} className="resource-card"><strong>{title}<ArrowUpRight size={15} aria-hidden="true" /></strong><p>{detail}</p></Link>)}
    </div>
  </section>;
}
