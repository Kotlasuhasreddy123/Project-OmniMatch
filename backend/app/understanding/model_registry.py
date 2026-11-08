"""Reviewed public checkpoints. No remote Python code or mutable revisions."""
MODELS = {
    'ner': ('blaze999/Medical-NER', 'a9d5061193e969de80b24225f926cb224caac1ce'),
    'sentiment': ('lxyuan/distilbert-base-multilingual-cased-sentiments-student', 'cf991100d706c13c0a080c097134c05b7f436c45'),
    'assertion': ('cross-encoder/nli-MiniLM2-L6-H768', 'b95119ce93d3e065de6214e38cd4a97b0f2f2c6d'),
    'reranker': ('cross-encoder/ms-marco-MiniLM-L6-v2', '233902d25c440f23af6f7d6e94d2946bac0bee0a'),
    'generator': ('google/flan-t5-small', '0fc9ddf78a1e988dac52e2dac162b0ede4fd74ab'),
    'embedding': ('sentence-transformers/all-MiniLM-L6-v2', '1110a243fdf4706b3f48f1d95db1a4f5529b4d41'),
}
