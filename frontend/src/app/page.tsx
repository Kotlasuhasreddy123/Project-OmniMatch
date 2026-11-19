import Link from "next/link";
import { ArrowRight, Check, FileText, ShieldCheck } from "lucide-react";

export default function HomePage() {
  const portal = process.env.NEXT_PUBLIC_PORTAL_MODE === "true";
  return <>
    <section className="hero-layout" aria-labelledby="home-title">
      <div>
        <p className="eyebrow">Clinical research, with human review</p>
        <h1 id="home-title">Turn visit information into study suggestions.</h1>
        <p className="hero-intro">Record a conversation or add a note. Review the extracted terms, explore related studies, and see what information is still needed.</p>
        <div className="hero-actions">
          <Link href={portal ? "/preview" : "/session"} className="ui-button">{portal ? "Explore sample results" : "Start a new visit"}<ArrowRight size={17} aria-hidden="true" /></Link>
          <Link href={portal ? "/guide" : "/preview"} className="ui-button ui-button-secondary">{portal ? "Set up on your computer" : "See an example"}</Link>
        </div>
        <p className="mt-5 flex items-start gap-2 text-xs leading-6 text-slate-600"><ShieldCheck size={15} className="mt-1 shrink-0 text-emerald-700" aria-hidden="true" />Synthetic patient data only. You approve the information used in every search.</p>
      </div>
      <div className="workflow-preview" aria-label="Illustrative visit-to-study workflow">
        <div className="preview-label"><strong>From visit to review</strong><span>Synthetic example</span></div>
        <article><p className="preview-card-label">01 · Visit information</p><p className="preview-card-title flex gap-2"><FileText size={16} className="mt-1 shrink-0 text-slate-500" aria-hidden="true" />“The patient has asthma and uses albuterol.”</p></article>
        <article><p className="preview-card-label">02 · Terms approved by the reviewer</p><span className="preview-chip"><Check size={12} aria-hidden="true" />Asthma</span><span className="preview-chip"><Check size={12} aria-hidden="true" />Albuterol</span></article>
        <article><p className="preview-card-label">03 · Study review</p><p className="preview-card-title">Related study information</p><p className="mt-2 text-xs leading-6 text-slate-600">Supporting terms are linked to criteria. Missing measurements remain visible for review.</p><div className="mt-3 flex items-center gap-2 text-xs text-amber-900"><span aria-hidden="true" className="h-1.5 w-1.5 rounded-full bg-amber-600" />Lung-function measurement needs checking</div></article>
      </div>
    </section>
    <section className="flow-steps" aria-label="How OmniMatch works">
      {[
        ["01", "Capture the visit", "Add a patient ID and record consent. Use voice recording or a written note."],
        ["02", "Review the information", "Check the transcript, then approve or reject each extracted medical term."],
        ["03", "Explore related studies", "Open your inbox to compare study criteria, missing information and visit history."],
      ].map(([number,title,body]) => <article className="flow-step" key={number}><span className="step-number">{number}</span><h2>{title}</h2><p>{body}</p></article>)}
    </section>
    <section className="mt-9 grid gap-5 md:grid-cols-2">
      <div className="ui-panel"><p className="eyebrow">What the results mean</p><h2 className="mt-3 text-xl font-semibold tracking-tight">A starting point for study review.</h2><p className="mt-3 text-sm leading-7 text-slate-600">Clinical trials are research studies with rules about who can participate. OmniMatch suggests studies from approved visit information. It does not predict a future disease or confirm enrollment.</p><p className="mt-3 text-xs leading-6 text-slate-600">The bundled catalog contains fictional studies. Real registry records require separate checks of recruitment status, locations and eligibility.</p></div>
      <div className="ui-panel"><p className="eyebrow">Where your work happens</p><h2 className="mt-3 text-xl font-semibold tracking-tight">Explore here. Work in your installation.</h2><p className="mt-3 text-sm leading-7 text-slate-600">The public website offers examples, account access and setup guides. Recording, AI processing and saved visits run on your computer. Each account has its own inbox and history.</p><Link href="/guide" className="ui-link mt-5">Read the setup guide <ArrowRight size={15} aria-hidden="true" /></Link></div>
    </section>
  </>;
}
