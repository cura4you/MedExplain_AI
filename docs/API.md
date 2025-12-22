# API

## Base URL
- Local: `http://localhost:8000`

## POST /api/analyze
Request body:
```json
{
  "report_text": "<paste report>",
  "report_type": "radiology | lab | clinical | other"
}
```

Response body:
```json
{
  "summary": "...",
  "key_findings": ["..."],
  "recommendations": ["..."],
  "disclaimer": "..."
}
```
