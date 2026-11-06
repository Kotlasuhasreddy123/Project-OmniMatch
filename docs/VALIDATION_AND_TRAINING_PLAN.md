# Model improvement and coverage plan

No new model has been trained in this release. No result establishes 98–100% clinical accuracy, all-specialty validation or all-language validation. The active extraction rules are English. Whisper and MiniLM use published pretrained weights; their training sources are documented in MODELS_AND_DATA.md.

## What we can measure now

The text-context regression checks contain 69 synthetic English development examples with 72 expected term/context assertions. Passing them demonstrates those assertions only. They are not independent clinical validation, speech word error rate, complete NER precision/recall, or trial retrieval quality. The validation page keeps these distinctions visible.

The older 100-transcript synthetic set in `backend/app/data/training_transcripts.json` gives negation precision 0.770, recall 0.297 and F1 0.429 using its existing substring-matching evaluation procedure. Many expected terms are absent from the extraction vocabulary. Its 95% recall acceptance test is explicitly marked as a strict expected failure, not a pass. This is an unresolved release limitation. Neither this set nor the focused regression set establishes clinical performance. The small passing set must not be substituted for this broader failing target.

## Before fine-tuning

1. Define a specific task and population: for example English adult pulmonary research retrieval. Specify inclusion/exclusion rules, language, specialty and the intended human review step.
2. Assemble permitted synthetic academic examples with documented sources, licenses and reviewer labels. Do not scrape all internet medicine or copy protected patient records. Keep diagnosis/forecasting/prescribing outside this research matching task.
3. Have reviewers label each visit-study pair as relevant or irrelevant, with reasons and disagreements recorded. Split by patient and source before training. Check duplicated text across splits. Reserve an untouched test set.
4. Compare the pretrained MiniLM baseline with a candidate trained only on the training split. Select parameters and thresholds using validation data, never the reserved test set.
5. Measure retrieval recall@5/10, precision@5 and ranking relevance on candidate study lists. Report counts, uncertainty intervals and failure cases separately for each supported specialty/language. Pair-classification accuracy alone is insufficient for retrieval acceptance.

## Candidate experiment parameters

These are starting values for an experiment, not accuracy guarantees: keep `sentence-transformers/all-MiniLM-L6-v2` as the baseline, seed 42, maximum input length 256 tokens, batch size 16, learning rate 0.00002, 1–3 epochs, and cosine-similarity loss on reviewed positive/negative text pairs. Confirm memory use and package compatibility before running. Save a separate candidate directory and never overwrite the deployed model automatically.

For speech, evaluate the unchanged Whisper base model on independently transcribed synthetic recordings first. Measure word error rate, medical-term errors, accents, noise and recording length. Changing the Whisper model size is not fine-tuning and does not validate downstream extraction.

For extraction, report entity precision/recall/F1 and separate negation, family, hypothetical and historical context errors. A trained multilingual extractor would need reviewed multilingual examples; translating the interface cannot supply that validation.

## Release decision

Keep a versioned manifest of model revision, data hashes, permitted use, split assignments, reviewers, parameters, hardware, baseline/candidate results and unresolved errors. Require human approval before replacing a model. Mark unsupported slices as unmeasured. Do not turn a ranking score into a disease probability or tune until a test score looks good.

The required independently reviewed corpus has not been supplied. Fine-tuning and representative clinical evaluation therefore remain pending. The coverage selector on the website is a planning register; it does not imply that each selectable category has been tested.

Reference: [NIST AI Risk Management Framework](https://www.nist.gov/itl/ai-risk-management-framework).
