'use client';
import { compareCases, visitChanges } from '@/lib/caseReview';

type Visit = { session_id: string; approved_terms: string[] };
export function HistoryReview({ visits, terms }: { visits: Visit[]; terms: string[] }) {
  const changes = visits.length > 1 ? visitChanges(visits[visits.length - 2].approved_terms, visits[visits.length - 1].approved_terms) : null;
  const cases = compareCases(terms).slice(0, 3);
  return <section className="ui-panel my-6 space-y-5" aria-label="History comparison and fictional cases">
    <div><p className="eyebrow">Visit comparison</p><h2 className="mt-2 text-xl font-semibold tracking-tight">What changed between visits?</h2><p className="mt-2 text-sm leading-7 text-slate-600">Compare approved terms from the latest two visits. A term not repeated does not mean a condition resolved or a medication stopped.</p></div>
    {changes ? <div className="grid gap-3 md:grid-cols-3">{[
      ['Added in latest visit', changes.added, 'bg-sky-50 border-sky-100'],
      ['Repeated in both visits', changes.repeated, 'bg-emerald-50 border-emerald-100'],
      ['Not repeated this visit', changes.notRepeated, 'bg-amber-50 border-amber-100'],
    ].map(([title, items, color]) => <div key={title as string} className={`rounded-lg border p-4 ${color}`}><h3 className="text-xs font-semibold">{title}</h3><p className="mt-2 text-sm">{(items as string[]).join(', ') || 'None'}</p></div>)}</div> : <p className="status-note">Complete two reviewed visits with the same patient ID to compare them.</p>}
    <div className="border-t border-slate-100 pt-5"><h3 className="text-base font-semibold">Related teaching cases</h3><p className="mt-2 text-xs leading-6 text-slate-600">Matched by shared terms from six fictional examples. These are not real patient reports or predictions.</p></div>
    {cases.length ? cases.map(item => <details key={item.id} className="rounded-lg border border-slate-200 bg-white"><summary className="cursor-pointer p-4 text-sm font-medium"><span>{item.title}</span><span className="ml-3 text-xs font-normal text-teal-800">{item.shared.length} shared term{item.shared.length === 1 ? '' : 's'}</span></summary><div className="space-y-3 border-t border-slate-100 p-4 text-sm"><p><strong>Shared terms:</strong> {item.shared.join(', ')}</p><ol className="list-inside list-decimal space-y-1 text-slate-600">{item.history.map(line => <li key={line}>{line}</li>)}</ol><p><strong>Information to verify:</strong> {item.missing}</p></div></details>) : <p role="status" className="text-sm text-slate-600">No shared terms in this teaching library. Other relevant cases or studies may exist.</p>}
  </section>;
}
