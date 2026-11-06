export function CaseBadge({ conditions }: { conditions: string[] }) {
  const text = conditions.join(" ").toLowerCase();
  const [icon, label, color] = /asthma|copd|lung|breath/.test(text)
    ? ["🫁", "Respiratory research", "bg-sky-50 text-sky-900"]
    : /diabet|thyroid|metabolic/.test(text)
      ? ["🧪", "Metabolic research", "bg-violet-50 text-violet-900"]
      : /heart|hypertension|cardio/.test(text)
        ? ["🫀", "Cardiovascular research", "bg-rose-50 text-rose-900"]
        : /migraine|epilepsy|neuro/.test(text)
          ? ["🧠", "Neurology research", "bg-indigo-50 text-indigo-900"]
          : ["🔬", "Research review", "bg-teal-50 text-teal-900"];
  return (
    <span
      className={`inline-flex items-center gap-2 rounded-full px-3 py-1 text-xs font-medium ${color}`}
    >
      <span aria-hidden="true">{icon}</span>
      {label}
    </span>
  );
}
