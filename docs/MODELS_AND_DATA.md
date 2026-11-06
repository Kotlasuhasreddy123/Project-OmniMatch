# Which models does OmniMatch use?

## 1. Speech: OpenAI Whisper base

The backend loads the multilingual `base` checkpoint by default (74 million parameters). OpenAI trained this model family on 680,000 hours of internet audio paired with transcripts across English and other languages. We download the published weights and run inference locally. We have not fine-tuned Whisper on our conversations, patient records or synthetic demo scripts. This is a general speech model, so medical names, accents and noisy recordings still need transcription review.

Source: [Whisper model card](https://github.com/openai/whisper/blob/main/model-card.md). The exact original recordings are not supplied as an OmniMatch dataset. A trained speech model is not evidence of accuracy on a particular clinic's recordings.

## 2. Study retrieval: all-MiniLM-L6-v2

The backend loads `sentence-transformers/all-MiniLM-L6-v2`, which produces 384-dimensional vectors. Its authors fine-tuned a pre-trained MiniLM encoder with a contrastive objective on more than one billion sentence pairs. Sources listed in the model card include Reddit conversation pairs, S2ORC scientific text, WikiAnswers, PAQ, Stack Exchange, MS MARCO and other question-answer and sentence datasets. These are broad text sources, not a verified patient-to-clinical-trial training set. We use the published model weights without additional training.

Source: [MiniLM model card and dataset table](https://huggingface.co/sentence-transformers/all-MiniLM-L6-v2). Indexing a study in Qdrant computes and stores embeddings; it does not train or fine-tune MiniLM. Qdrant is a database, not a trained medical model.

## 3. Clinical terms and context: programmed rules

The active extraction endpoint calls `backend/app/nlp/negex_pipeline.py`. It uses a medical vocabulary and regular expressions to identify terms, negation, family history and hypothetical statements. Although spaCy is an installed dependency, this active extractor does not load a trained spaCy medical NER model. Its confidence values are heuristics. Criterion checks and review-score arithmetic are also rules rather than learned diagnostic models.

The two learned models are already trained by their publishers. Our own pipeline needs representative evaluation and carefully reviewed improvements; it does not start as an untrained medical model. No additional weight training has been performed for this release. Fine-tuning requires a defined task, licensed/consented data, independent labels and a held-out evaluation set. The three fictional catalog studies and our synthetic scripts do not establish broad medical coverage.

## What we checked and fixed

Run `python backend/evaluate_context.py` from the repository root. It uses only Python's standard library and the real extraction module. The fixtures contain 69 synthetic text examples and 72 expected target-term/context checks. Before corrections, 70/72 passed. After preserving specific diabetes terms and retaining hypothetical/confirmed mentions separately, 72/72 pass. The baseline and result JSON files under `docs/` include dataset and source hashes.

These are development regression results on known vocabulary, not an independent clinical test set. This metric checks whether an expected term/context combination is present. It does not measure all false positive entities, NER F1, audio word error rate, trial-retrieval relevance, eligibility correctness, or medication/disease prediction. It was used to fix the rules, so it must not be presented as unseen evaluation performance.

## What remains before medical claims

Use consented/synthetic recordings with independently prepared transcripts to measure speech word error rate. Use independently annotated conversations to measure entity precision/recall/F1 and context errors. Use reviewed patient-study pairs to measure retrieval recall at k. Keep development and held-out sets separate by patient and source. Only fine-tune after a baseline and rights to the data are established, then compare both models on a locked evaluation set. Do not adjust model weights on the evaluation examples to reach a target percentage.

Whisper can detect multiple speech languages, but the current term vocabulary and rules are English. Multilingual speech support does not make the entire application multilingual. This repository remains for synthetic-data research demonstrations.
