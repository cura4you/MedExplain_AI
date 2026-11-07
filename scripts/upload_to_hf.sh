#!/usr/bin/env bash
set -euo pipefail
if [[ -z "${HF_TOKEN:-}" ]]; then
  echo "HF_TOKEN is required to upload to Hugging Face." >&2
  exit 1
fi
MODEL_DIR=${1:-fine-tuning/output}
REPO_ID=${2:?Pass the intended Hugging Face owner/repository explicitly}
python3 - "$MODEL_DIR" "$REPO_ID" <<'PY'
from huggingface_hub import HfApi, upload_folder
from pathlib import Path
import os
import sys
model_dir, repo_id = sys.argv[1:]
folder = Path(model_dir)
if not (folder / 'adapter_config.json').is_file() or not any((folder / name).is_file() for name in ['adapter_model.safetensors', 'adapter_model.bin']):
    raise SystemExit('Saved adapter configuration and weights are required; nothing uploaded.')
token = os.environ.get('HF_TOKEN')
if not token:
    raise SystemExit('HF_TOKEN is required')
api = HfApi()
api.create_repo(repo_id, exist_ok=True, token=token)
upload_folder(repo_id=repo_id, folder_path=model_dir, token=token)
print('Adapter uploaded to the explicitly selected repository.')
PY
