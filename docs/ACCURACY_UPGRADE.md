# Accuracy work and limits November 2026

This update improves specific English development tasks. It does not establish 98 percent accuracy across OmniMatch, every specialty or every language. No publisher checkpoint was fine-tuned on medical internet content.

## Changes

- Added a pinned CC0 Human Disease Ontology snapshot: 30,995 unambiguous English term variants and 20 ambiguous terms from a source with 12,419 active concepts. Ambiguous terms show a subtype-review note instead of silently selecting a concept. The importer, source URL, SHA256 and license are included.
- Shared explicit patient-subject scope between rule and hybrid extraction. Family and negation labels no longer carry over the tested subject-change examples.
- Enriched RAG ranking with literal entity types from the original passage. The quotation, offsets, hash, relevance gate and abstention behavior remain unchanged. No new facts or diagnostic synonyms are generated for ranking.
- Compared Whisper base and small on eight offline fictional TTS notes. Small is now the accuracy-focused default; base remains a faster option.

## Measured development results

| Task | Before this update | After |
| --- | --- | --- |
| Broad negation precision | 86.7 percent | 87.8 percent |
| Broad negation recall | 70.3 percent | 82.3 percent |
| Broad negation F1 | 77.6 percent | 85.0 percent |
| Real hybrid target/context cases | 9 of 12 | 12 of 12 |
| RAG expected source or abstention | 11 of 12 | 12 of 12 |
| RAG returned citation integrity | 8 of 8 | 9 of 9 |
| Targeted context regression | 72 of 72 | 72 of 72 |
| Additional exact-set synthetic scenarios | New | 72 of 72 |
| Offline TTS word error rate | base 8.9 percent | small 3.3 percent |

These columns are task-specific, not an overall application score. The broad corpus was previously inspected; its legacy substring scorer and annotation limits remain. The extra scenarios are author-created and templated. The RAG corpus contains three invented studies. Citation integrity does not prove relevance or clinical correctness. The tone classifier remains a separate general-language tool; its result must not be used for diagnosis, urgency or matching.

The TTS assessment used one Microsoft David Desktop voice and 90 reference words. Raw word errors were 8 for base and 3 for small. Numbers and possessives were not specially forgiven after inspection. Small generally needed roughly 9 to 13 seconds for a short warmed example versus about 3 for base; its first timing included download/startup. No raw audio was saved. This does not measure real clinical speech, accents, noise, multi-speaker conversations or a new clinical test set.

## Reproduce

```powershell
python backend/evaluate_broad.py
python backend/evaluate_context.py
python backend/evaluate_final_scenarios.py
python scripts/export_model_evidence.py
python scripts/export_advanced_evidence.py
```

The real transformer evaluation requires the configured Docker/model environment and cached weights: `python backend/evaluate_advanced.py`. The offline Windows TTS generator emits in-memory audio to the speech evaluator; never redirect its audio batch to a file. `backend/evaluate_speech.py` documents the scoring procedure.

To use the faster speech profile, set `WHISPER_MODEL=base` in the ignored backend environment file and recreate the backend. The default `small` model needs more memory and latency. Existing installations must update their own setting; changing the example file alone does not change an existing environment.

## Evidence files

- `broad-negation-after.json`: current broad metric and source hashes.
- `advanced-model-evaluation.json`: real pinned-checkpoint development outcomes.
- `final-scenario-results.json`: exact term/context/negation sets, including extra findings.
- `speech-base-development.json` and `speech-small-development.json`: text-only TTS outcomes.

## What is still required

The broad recall target is still unmet. Independently labeled, permitted and representative encounters are needed before further fitting and a frozen external evaluation. Record speaker/encounter-separated partitions, medication and number errors, uncertainty, rare-family examples, retrieval relevance and user acceptance. Do not tune repeatedly on a final test set or average unrelated scores into a claim of clinical accuracy.

Sources: [Disease Ontology pinned repository](https://github.com/DiseaseOntology/HumanDiseaseOntology/tree/bd7dcdf405e03d3f896089ece856209861946e56), [ConText research](https://pmc.ncbi.nlm.nih.gov/articles/PMC2757457/), and [Whisper research](https://proceedings.mlr.press/v202/radford23a.html).

## Software verification

The final local real-stack run completed with 250 backend tests passed and one expected failure for the unmet broad-recall target. Frontend verification completed with 69 tests passed. A test pass rate measures software checks, not medical model accuracy.
