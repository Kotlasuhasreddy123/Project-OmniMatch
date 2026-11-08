"""Download pinned public weights once. No patient text is sent to a provider."""
import argparse
from app.understanding.model_registry import MODELS


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--only', nargs='+', choices=list(MODELS), default=list(MODELS))
    args = parser.parse_args()
    from huggingface_hub import snapshot_download
    for name in args.only:
        repo, revision = MODELS[name]
        path = snapshot_download(repo_id=repo, revision=revision, allow_patterns=[
            'config.json', 'model.safetensors', 'tokenizer.json', 'tokenizer_config.json',
            'special_tokens_map.json', 'vocab.txt', 'vocab.json', 'merges.txt',
            'spiece.model', 'spm.model', 'sentencepiece.bpe.model', 'generation_config.json', 'added_tokens.json',
            'README.md', 'LICENSE*', 'NOTICE*',
        ])
        print(f'{name}: {repo}@{revision} cached at {path}', flush=True)
