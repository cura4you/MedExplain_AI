# Backend Service

## Run locally
```bash
cd backend
cp .env.example .env
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

## API
- `POST /api/analyze` with JSON body:
```json
{
  "report_text": "Paste a medical report",
  "report_type": "radiology"
}
```
