import { compareCases, visitChanges } from './caseReview';

test('empty and unrelated histories do not manufacture case matches', () => {
  expect(compareCases([])).toEqual([]);
  expect(compareCases(['unrelated phrase'])).toEqual([]);
});
test('duplicate terms cannot inflate overlap and ties are deterministic', () => {
  expect(compareCases(['asthma', 'asthma', 'albuterol'])[0].shared).toEqual(['asthma', 'albuterol']);
  expect(compareCases(['migraine', 'asthma']).map(item => item.id)).toEqual(['CASE-A', 'CASE-C']);
});
test('history changes do not equate absence with resolution', () => {
  expect(visitChanges(['asthma', 'albuterol'], ['asthma', 'migraine'])).toEqual({ added: ['migraine'], repeated: ['asthma'], notRepeated: ['albuterol'] });
});
test('unspecified diabetes is not silently upgraded to type 2', () => {
  expect(compareCases(['diabetes'])).toEqual([]);
});
