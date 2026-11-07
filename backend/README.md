# Backend service

The FastAPI service accepts report text and returns a structured explanation. It can call a configured OpenAI-compatible provider, a dedicated Hugging Face text-generation endpoint, or an existing compatible local checkpoint. Backend-side inference failures return an explicitly labelled fallback; fallback is never evidence that a model ran.

## Run

```sh
python3 -m venv .venv
.venv/bin/pip install -r backend/requirements.txt
cp backend/.env.example backend/.env
# Configure AI_BASE_URL, AI_MODEL, AI_API_KEY and CORS_ORIGINS.
.venv/bin/uvicorn backend.main:app --host 127.0.0.1 --port 8000
```

`backend/.env` is loaded without overwriting environment variables. Only lightweight web-service dependencies are needed. `requirements-local-model.txt` adds Torch, Transformers and Accelerate for an independently obtained compatible local model; these are not required for hosted inference.

## Configuration

- `AI_BASE_URL`, `AI_MODEL`, `AI_API_KEY`: OpenAI-compatible chat-completions provider, model and server-only credential. A configured generic provider produces `source: hosted_model`.
- `AI_TIMEOUT_SECONDS`: bounded per-network-operation timeout (1–60, default 45 seconds), one request attempt. This is an inactivity timeout, not a strict overall wall-clock deadline.
- `HF_INFERENCE_URL`: explicit running text-generation endpoint; no obsolete public endpoint is assumed. Optional `HF_TOKEN` is sent only by the backend. Produces `hf_inference`.
- `MODEL_LOCAL_PATH`: an existing compatible checkpoint directory, if you choose to install the optional runtime. Missing/incompatible weights return fallback. ERNIE GPU loading and fine-tuned weights have not been verified.
- `CORS_ORIGINS`: comma-separated frontend origins. Default `http://localhost:5173`.

Priority is local checkpoint when explicitly configured, then configured hosted provider, then explicit HF endpoint. With no usable provider, the response is `fallback`.

## Checks

```sh
.venv/bin/python -m unittest discover -s backend/tests -v
python3 -m unittest discover -s fine-tuning -p 'test_*.py' -v
```

See [API contract](../docs/API.md) and [verified model/claims audit](../docs/live-model-verification/README.md). No model key is returned to the browser, printed, or committed.
