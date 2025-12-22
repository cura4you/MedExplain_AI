#!/usr/bin/env bash
set -euo pipefail

if [[ -z "${HF_TOKEN:-}" ]]; then
  echo "HF_TOKEN is required to upload to Hugging Face." >&2
  exit 1
fi

MODEL_DIR=${1:-fine-tuning/output}
REPO_ID=${2:-medexplain-ai}

python3 - <<PY
from huggingface_hub import HfApi, upload_folder
import os

repo_id = "${REPO_ID}"
model_dir = "${MODEL_DIR}"

token = os.environ.get("HF_TOKEN")
if not token:
    raise SystemExit("HF_TOKEN is required")

api = HfApi()
api.create_repo(repo_id, exist_ok=True, token=token)
upload_folder(repo_id=repo_id, folder_path=model_dir, token=token)
print(f"Uploaded {model_dir} to {repo_id}")
PY
