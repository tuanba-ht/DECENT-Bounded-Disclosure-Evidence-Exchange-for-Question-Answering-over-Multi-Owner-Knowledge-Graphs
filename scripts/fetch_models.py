"""Download the open-weight models used for the cross-model parser comparison.

All are in the same 7-8B class as the primary model.
"""
from __future__ import annotations

import sys
from pathlib import Path

from huggingface_hub import snapshot_download

MODELS = {
    "mistral-7b-instruct-v03": "mistralai/Mistral-7B-Instruct-v0.3",
    "olmo2-7b-instruct": "allenai/OLMo-2-1124-7B-Instruct",
    "granite-31-8b-instruct": "ibm-granite/granite-3.1-8b-instruct",
}

# Skip duplicate weight formats; the loader only needs safetensors.
IGNORE = ["*.pth", "*.bin", "*.gguf", "*.msgpack", "*.h5", "consolidated*"]


def main() -> None:
    dest_root = Path(sys.argv[1] if len(sys.argv) > 1 else "models")
    dest_root.mkdir(parents=True, exist_ok=True)
    for local, repo in MODELS.items():
        target = dest_root / local
        print(f"[fetch] {repo} -> {target}", flush=True)
        snapshot_download(repo_id=repo, local_dir=str(target), ignore_patterns=IGNORE, max_workers=4)
        print(f"[done ] {local}", flush=True)


if __name__ == "__main__":
    main()
