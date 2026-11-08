# Advanced text understanding and cited study evidence

This optional local workflow adds biomedical transformers, context review, general language tone and retrieval-augmented generation (RAG). It uses published pretrained weights. I did not fine-tune these checkpoints or establish 98% clinical accuracy.

## What runs

| Task | Checkpoint | Publisher description / declared license |
|---|---|---|
| Medical term proposals | `blaze999/Medical-NER` | DeBERTa-based medical NER; MIT |
| Context second opinion | `cross-encoder/nli-MiniLM2-L6-H768` | Natural language inference trained on SNLI/MultiNLI; Apache-2.0 |
| General wording tone | `lxyuan/distilbert-base-multilingual-cased-sentiments-student` | Distilled multilingual sentiment model; Apache-2.0 |
| Dense passage retrieval | `sentence-transformers/all-MiniLM-L6-v2` | Text embedding encoder; Apache-2.0 |
| Passage reranking | `cross-encoder/ms-marco-MiniLM-L6-v2` | BERT-family query/passage reranker trained on MS MARCO; Apache-2.0 |
| Local draft generation | `google/flan-t5-small` | Instruction-tuned T5; Apache-2.0 |

The exact repository revisions are pinned in `backend/app/understanding/model_registry.py`. The loader uses local cached safetensors, disables remote Python code, and runs on CPU. The initial download contacts Hugging Face for public model files; note text is not sent to a hosted inference API.

Model cards: [medical NER](https://huggingface.co/blaze999/Medical-NER), [NLI](https://huggingface.co/cross-encoder/nli-MiniLM2-L6-H768), [tone](https://huggingface.co/lxyuan/distilbert-base-multilingual-cased-sentiments-student), [embeddings](https://huggingface.co/sentence-transformers/all-MiniLM-L6-v2), [reranker](https://huggingface.co/cross-encoder/ms-marco-MiniLM-L6-v2), [FLAN-T5](https://huggingface.co/google/flan-t5-small). These are publisher descriptions, not local performance claims. Retain their notices and review their terms before redistributing weights.

## How the workflow works

1. Enter a fictional English visit note on **Text & evidence** (`/research`). The maximum is 12,000 characters. This page does not activate the microphone or create an inbox visit.
2. Vocabulary rules and medical NER propose terms. Source spans and context guards keep denied, family-history and uncertain statements separate. The initial DistilBERT biomedical checkpoint missed useful terms in exploratory checks, so the optional path uses the DeBERTa checkpoint listed above. This choice is not proof of general medical superiority.
3. NLI compares the surrounding text with natural-language hypotheses for patient, denied, family and uncertain mentions. It flags disagreements; it never approves or silently changes findings. At most 12 located terms receive this second opinion, with the remaining count shown.
4. A separate DistilBERT model scores positive/neutral/negative wording. Low separation or a low top score is shown as unclear. Tone is advisory and never enters trial matching, eligibility scores or urgency decisions. Medical words such as “negative test” can confuse this general model.
5. Approve or reject every proposed patient term. Family, denied and uncertain terms remain excluded. Editing the note invalidates the previous findings and approvals.
6. Ask a study question. The API passes only approved, affirmed patient terms to Qdrant and retrieves up to 20 candidate studies. It does not search the whole registry.
7. Study titles, summaries and eligibility fields are chunked with source offsets and hashes, up to 120 passages. BM25 lexical retrieval and MiniLM dense retrieval are combined with reciprocal-rank fusion. A cross-encoder reranks the best 12 candidates. Including the study title and inclusion/exclusion section gives short criteria the context the reranker needs.
8. FLAN-T5 drafts from the selected passages. A draft is accepted only if it reproduces a complete source passage, allowing formatting-only differences in case, whitespace, quotes and asterisk bullets. Clinical words, negation and numeric signs must be preserved. Otherwise, the response explicitly falls back to cited excerpts. There is no generated eligibility confirmation, diagnosis, disease forecast or prescription.

This follows the [retrieve-and-rerank approach described by Sentence Transformers](https://www.sbert.net/examples/sentence_transformer/applications/retrieve_rerank/README.html). RAG supplies evidence context; it does not guarantee factual or clinical correctness. The quote gate checks source wording, not whether every source statement is current or whether every question is fully answered.

## Local setup with Docker

Keep the existing database volumes. Do not remove them to enable these features. Configure [approved email access](PASSWORDLESS_ACCESS.md) first; the blank WorkOS IDs intentionally keep protected pages closed.

Use the current repository root in PowerShell:

```powershell
git pull --ff-only
docker compose --env-file backend/.env build backend frontend
```

Edit `backend/.env` and set:

```dotenv
ADVANCED_NLP_ENABLED=true
```

Then run:

```powershell
docker compose up -d
docker compose exec backend python prepare_advanced_models.py
docker compose restart backend
docker compose ps
```

The model cache is in the persistent backend data volume. The first download can take several minutes and needs several GB of free disk. Start with 16 GB system memory and enough memory assigned to Docker; the basic low-memory AWS free-tier machine is not an appropriate expectation for all these models. These are planning requirements, not a measured cloud capacity guarantee. No GPU or paid inference API is required.

Alternatively, `python scripts/setup_local.py --start --advanced` enables this setting, builds the images, prepares weights and starts the services. Add `--project-name` with the existing Compose project name when upgrading an older installation. The runtime keeps only two optional models cached in memory and loads others as needed. This trades some switching time for lower model residency; it does not cap total application memory.

Open `http://localhost:3000/research`, sign in, and refresh the page after model preparation. With a development frontend, use its actual port, such as `http://localhost:3013/research`. The setup panel stays visible when required dependencies or cached model files are missing. The feature defaults to disabled and never returns fabricated model predictions when setup is incomplete.

Docker Desktop was stopped during this development run. The real models were executed locally in Python; this Docker setup still needs a fresh local rehearsal on the deployment machine.

## Reproduce the offline model evaluation

These commands create a separate environment. If using a fresh environment, install a CPU PyTorch version supported by your Python and platform using the [official PyTorch instructions](https://pytorch.org/get-started/locally/). The development machine already had CPU PyTorch installed.

```powershell
py -3 -m venv --system-site-packages .venv-advanced
.\.venv-advanced\Scripts\python.exe -m pip install -r backend/requirements-advanced.txt
.\.venv-advanced\Scripts\python.exe backend/prepare_advanced_models.py
.\.venv-advanced\Scripts\python.exe backend/evaluate_advanced.py
```

The evaluator requires no WorkOS account or running Qdrant. It runs the actual cached neural checkpoints against fictional notes and three fixed fictional studies, then writes `docs/advanced-model-evaluation.json`. This tests the model services, not a complete authenticated deployment. The ordinary test suite uses explicit stubs for integration contracts; stub tests are not included in model accuracy figures.

## Measured development results and limits

- Hybrid target-term/context presence: 9/12 checks; rules alone 6/12 on the same small new fixture set. This is target presence, not full NER precision/recall/F1.
- NLI context labels: 9/12. Its suggestions can be wrong and remain advisory.
- General tone top labels: 7/12; four cases meet the unclear-display rule. This is insufficient to infer patient emotion or clinical state.
- RAG expected-source-or-abstention: 11/12; one inhaler question is conservatively rejected. The selected source check is not clinical answer accuracy or registry-wide retrieval recall.
- Citation integrity is reported separately as matching original source slices and SHA-256 hashes. It is a mechanical integrity check, not model accuracy.

The initial RAG run with isolated fragments scored 5/12 and returned no citations because the relevance gate rejected the clinical fragments. That report is retained as `advanced-model-evaluation-initial.json`. Adding title/section context improved this development check. These are developer-inspected fixtures, not an untouched clinical test set. Full records, failures, exact revisions, versions and runtime are in the JSON report.

Whisper and the earlier experimental logistic classifier are unchanged. No new claim is made for every language, specialty, real patient population or 98% across the application.

## Demo sequence

1. Load the fictional asthma example and analyze it.
2. Review the general-tone panel as wording information only. Open the NLI section and explain any disagreement.
3. Approve asthma and albuterol individually. Leave denied COPD and family stroke excluded.
4. Ask “Which condition is excluded in the asthma study?” Review the returned COPD source excerpt and its citation.
5. Ask a disease prediction question. Explain the scope boundary and the abstention.
6. Open a citation's provenance details. The hash and character offsets identify the quoted study-field text. A `DEMO-` study is fictional and cannot accept a referral.
7. Use the regular visit workflow when you want recording, saved visits and the asynchronous inbox. This research desk does not replace those steps.
