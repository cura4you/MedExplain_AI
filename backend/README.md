# Backend Service

## Run locally
```bash
cd backend
cp .env.example .env
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

## Environment
- `HF_TOKEN` should be set for Hugging Face Inference API access.
- `MODEL_NAME` defaults to `baidu/ERNIE-4.5-VL-28B-A3B-Thinking`.
- `MODEL_LOCAL_PATH` (optional) points to a fine-tuned model directory; if present, the backend will load it instead of calling HF.

## API
- `POST /api/analyze` with JSON body:
```json
{
  "report_text": "Paste a medical report",
  "report_type": "radiology"
}
```
