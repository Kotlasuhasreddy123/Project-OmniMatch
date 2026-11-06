# Models, training and measured results

## What the application uses

| Component | What it does | Training and data | Current status |
|---|---|---|---|
| OpenAI Whisper `base` | Turns recorded speech into text | Publisher-trained multilingual checkpoint, 74 million parameters. The Whisper family was trained on 680,000 hours of internet audio/transcript pairs. | Active; downloaded pretrained weights. No project fine-tuning or measured medical speech word error rate. |
| `sentence-transformers/all-MiniLM-L6-v2` | Converts approved terms and study text into 384-number vectors for search | Publisher-trained encoder; its model card describes over one billion sentence pairs from broad text sources. | Active; unchanged weights. No independently labeled trial-retrieval evaluation. |
| English vocabulary and NegEx-style context rules | Finds supported terms and flags negation, family history and uncertainty | Programmed rules, not learned weights. Vocabulary and context handling improved in this update. | Active. Every term still needs human approval. |
| TF-IDF + logistic regression assertion candidate | Classifies a supplied term span as affirmed, negated or family history | Newly fitted here using the repository's synthetic annotated transcripts. | Experimental only. Not connected to the live API. |
| `cross-encoder/nli-MiniLM2-L6-H768` wrapper | Optional zero-shot NLI experiment | Named checkpoint in an unused code path. No project fine-tuning or verified local medical result. | Not active. The legacy filename `biobert_v3.py` is misleading: it is NOT BioBERT. |

spaCy is an installed dependency; the live endpoint does not load a trained spaCy medical model. Qdrant is a database. Eligibility scoring and the standalone NegEx/NegBio-inspired/ensemble experiments are rules, not additional trained medical models. No forecasting or prescribing model is installed.

Publisher references: [Whisper model card](https://github.com/openai/whisper/blob/main/model-card.md), [MiniLM model card](https://huggingface.co/sentence-transformers/all-MiniLM-L6-v2). These describe the publishers' training, not OmniMatch's measured performance.

## What improved in the live rules

I expanded the manually maintained English vocabulary and corrected context handling for longer lists, positive statements following a denial, and uncertainty such as “pneumonia cannot be excluded.” Uncertain findings use the existing hypothetical category so they are excluded from confirmed patient matching.

| Existing 100-transcript synthetic development benchmark | Before | After |
|---|---:|---:|
| Negation precision | 77.05% | 86.72% |
| Negation recall | 29.75% | 70.25% |
| Negation F1 | 42.92% | 77.62% |

The broader 95% recall requirement is still unmet. The separate 69-example focused regression remains 72/72 target checks. Neither result is general medical accuracy. The broad benchmark uses legacy substring matching, can credit partial terms and has incomplete annotations. I inspected it while developing the vocabulary; it is development evidence, not unseen validation. The before/after JSON reports include counts, failures and source hashes.

## What I actually trained

I trained a small CPU-based assertion classifier, separate from the active rules. It receives text AND a known term's start/end positions. This bypasses entity discovery, so its score cannot be used as end-to-end extraction accuracy.

- Source: 100 synthetic classroom transcripts already in the repository; no patient records, internet scraping or recordings.
- Data review: 13 annotation entries with absent, repeated or overlapping spans were excluded and listed for manual review. Labels were not silently invented.
- Corrected split: 69 training records, 15 validation records and 16 test records. All mentions from a record stay together. Family-history records are stratified across partitions.
- Aligned annotations: 216 training, 54 validation and 60 test examples. Only ONE family-history example appears in validation and one in test; this is far too little to validate that class.
- Features: the target term is masked; up to 12 words on each side, with word unigrams/bigrams and TF-IDF weights.
- Training: balanced logistic regression, seed 42, maximum 1,000 iterations. I compared regularization values C = 0.1, 1 and 10 using validation macro F1. Validation selected C = 10. Test labels were not used to choose C.
- Export: plain JSON coefficients, vocabulary and IDF weights. The portable predictor reproduces all saved test predictions. Existing candidate files are not overwritten by the training command.

**Corrected internal test result: 54/60 = 90.0% accuracy; macro F1 = 92.98%.** A constant majority-class baseline scores 41.67%. The simple term-level Wilson interval is approximately 79.85–95.34%; mentions are correlated within records, so this interval may understate uncertainty. This is not independent clinical validation and does not meet the requested 98%.

The first hash-only split scored 38/43 (88.37%) but contained no family examples in validation/test. I retained that diagnostic experiment as `context-candidate-v1`. I corrected the split design in `context-candidate-v2`; these are different test sets, so their percentages must not be presented as a like-for-like improvement. The candidate is not promoted to the live workflow.

## Run the training and tests yourself

From the repository root in Windows PowerShell:

```powershell
py -3.11 -m venv .venv-training
.\.venv-training\Scripts\python.exe -m pip install -r backend/requirements-training.txt
.\.venv-training\Scripts\python.exe backend/train_context_candidate.py --output-dir backend/experiments/my-run-01
py -3 backend/evaluate_broad.py
py -3 backend/evaluate_context.py
```

Choose a new output directory for each experiment. On macOS/Linux use `python3.11` and `.venv-training/bin/python`. The candidate training needs no GPU, cloud account or paid API. The saved `training_report.json` contains parameters, record assignments, class counts, excluded labels, test predictions and hashes. `context_candidate.json` contains fitted weights. Model changes are not automatically deployed.

## What is needed for a credible 98% claim

Define the task first: transcription uses word error rate, entity extraction uses precision/recall/F1, and study retrieval uses reviewed relevance and recall@k. A single “98% AI accuracy” number cannot represent all three.

Next, build a larger independently reviewed synthetic corpus with balanced family, negation, uncertainty and confirmed cases, full span labels, hard negatives, longer conversations and variations in wording. Split records and template/source families before model selection. Keep a locked test set and report each supported specialty/language separately. Speech needs synthetic recordings with independently prepared reference transcripts; retrieval needs reviewed visit-study relevance labels.

More fitting passes on the same small test corpus would not establish reliability. The present result is below 98%; the application remains in progress and requires human review. No parameter setting can guarantee 98% across medicine and languages.
