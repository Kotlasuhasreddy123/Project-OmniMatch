/** Authored fictional teaching cases, not patient records or outcome training data. */
export const CASES = [
  { id: 'CASE-A', title: 'Asthma follow-up', terms: ['asthma', 'albuterol', 'wheezing'], history: ['Visit 1: asthma and albuterol recorded.', 'Visit 2: wheezing added for review.'], missing: 'Current symptoms, medication use and protocol-specific measures need verification.' },
  { id: 'CASE-B', title: 'Diabetes research review', terms: ['type 2 diabetes', 'metformin', 'high blood pressure'], history: ['Visit 1: type 2 diabetes and metformin recorded.', 'Visit 2: high blood pressure added.'], missing: 'Age, HbA1c, kidney function and the exact study criteria remain unverified.' },
  { id: 'CASE-C', title: 'Migraine history review', terms: ['migraine', 'headache'], history: ['Visit 1: migraine recorded.', 'Visit 2: headache mentioned again.'], missing: 'Episode frequency, history and study-specific criteria need verification.' },
  { id: 'CASE-D', title: 'Arthritis visit review', terms: ['rheumatoid arthritis', 'methotrexate', 'pain'], history: ['Visit 1: rheumatoid arthritis recorded.', 'Visit 2: methotrexate and pain added.'], missing: 'Treatment history and protocol-specific measures remain unverified.' },
  { id: 'CASE-E', title: 'Respiratory research review', terms: ['copd', 'cough', 'shortness of breath'], history: ['Visit 1: COPD recorded.', 'Visit 2: cough and shortness of breath added.'], missing: 'Current clinical status and protocol-specific respiratory measures need verification.' },
  { id: 'CASE-F', title: 'Thyroid history review', terms: ['hypothyroidism', 'levothyroxine', 'fatigue'], history: ['Visit 1: hypothyroidism and levothyroxine recorded.', 'Visit 2: fatigue added.'], missing: 'Current laboratory results and study-specific criteria remain unverified.' },
] as const;

export function normalizeTerm(term: string): string {
  const value = term.trim().toLowerCase().replace(/\s+/g, ' ');
  return ({ hypertension: 'high blood pressure' } as Record<string, string>)[value] ?? value;
}

export function compareCases(approvedTerms: string[]) {
  const input = new Set(approvedTerms.map(normalizeTerm).filter(Boolean));
  return CASES.map(item => ({ ...item, shared: item.terms.filter(term => input.has(normalizeTerm(term))) }))
    .filter(item => item.shared.length > 0)
    .sort((a, b) => b.shared.length - a.shared.length || a.id.localeCompare(b.id));
}

export function visitChanges(previous: string[], latest: string[]) {
  const before = new Set(previous.map(normalizeTerm));
  const after = new Set(latest.map(normalizeTerm));
  return {
    added: [...after].filter(term => !before.has(term)),
    repeated: [...after].filter(term => before.has(term)),
    notRepeated: [...before].filter(term => !after.has(term)),
  };
}
