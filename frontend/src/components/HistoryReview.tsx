'use client';
import { compareCases, visitChanges } from '@/lib/caseReview';

type Visit = { session_id: string; approved_terms: string[] };
export function HistoryReview({ visits, terms }: { visits: Visit[]; terms: string[] }) {
  const changes = visits.length > 1 ? visitChanges(visits[visits.length - 2].approved_terms, visits[visits.length - 1].approved_terms) : null;
  const cases = compareCases(terms).slice(0, 3);
  return <section className="space-y-5 rounded-3xl border border-teal-200 bg-teal-50 p-6" aria-label="History comparison and fictional cases">
    <div><p className="text-xs font-bold uppercase tracking-widest text-teal-800">History into a clearer review</p><h2 className="mt-2 text-2xl font-semibold">What changed between visits?</h2><p className="mt-2 text-sm text-slate-700">We compare approved words, not disease progression. Earlier findings remain historical until reviewed again.</p></div>
    {changes ? <div className="grid gap-3 md:grid-cols-3">{[
      ['Added in latest visit', changes.added, 'bg-blue-100'],
      ['Repeated in both visits', changes.repeated, 'bg-teal-100'],
      ['Not repeated this visit', changes.notRepeated, 'bg-amber-100'],
    ].map(([title, items, color]) => <div key={title as string} className={`rounded-2xl p-4 ${color}`}><h3 className="font-semibold">{title}</h3><p className="mt-2 text-sm">{(items as string[]).join(', ') || 'None'}</p></div>)}</div> : <p className="rounded-xl bg-white p-4 text-sm">Complete two reviewed visits under the same fictional patient label to compare them.</p>}
    <p className="text-sm text-slate-700">A term not repeated is not evidence that a condition resolved or a medication stopped.</p>
    <h2 className="text-xl font-semibold">Similar fictional case examples</h2>
    <p className="text-sm text-slate-700">Six authored teaching cases, compared with the displayed approved history using exact normalized terms. These are not real patient reports, published case studies or future-outcome estimates.</p>
    {cases.length ? cases.map(item => <article key={item.id} className="rounded-2xl border border-teal-200 bg-white p-5"><div className="flex flex-wrap justify-between gap-2"><h3 className="font-semibold">{item.title}</h3><span className="rounded-full bg-teal-100 px-3 py-1 text-xs font-semibold">{item.shared.length} shared term{item.shared.length === 1 ? '' : 's'}</span></div><p className="mt-2 text-sm">Shared: {item.shared.join(', ')}</p><ol className="mt-3 list-inside list-decimal text-sm text-slate-700">{item.history.map(line => <li key={line}>{line}</li>)}</ol><p className="mt-3 text-sm"><strong>Information to verify:</strong> {item.missing}</p></article>) : <p role="status" className="rounded-xl bg-white p-4">No overlap in this six-case teaching library. This does not rule out a condition or research opportunity.</p>}
    <div className="rounded-xl bg-slate-900 p-4 text-sm text-white"><strong>Future predictions:</strong> no disease-risk or treatment-outcome model has been validated. This view supports a review of changes and missing information; it does not invent a probability or prescribe a medicine.</div>
  </section>;
}
