# Assertion-classifier experiments

These JSON artifacts are experimental and are not loaded by the live NLP endpoint.

- `context-candidate-v1`: initial hash-only split, 38/43 internal test predictions correct. Validation/test omitted family-history examples. Retained as a diagnostic result, not a valid three-class evaluation.
- `context-candidate-v2`: corrected record-separated family-stratified split. 54/60 internal test predictions correct; only one family-history test annotation. Not clinical validation and not eligible for live promotion.

Both use the repository's synthetic development corpus. It was previously used for rule development. Neither experiment supplies an independent external evaluation. Do not compare their percentages as the same test set or present either as overall medical accuracy.

The frozen v2 candidate additionally scores 107/108 (99.07%) on the second existing 20-note classroom corpus. See `context-candidate-v2/extra_corpus_report.json`. This different, small development check does not override the 90% internal test or establish an overall 98% requirement.

See `docs/MODEL_TRAINING_RESULTS.md` for data, exclusions, parameters and reproduction commands. Training a new experiment refuses to overwrite existing model weights.
