# API reference

## Service routes

- `GET /`: service description.
- `GET /health`: `{ "status": "ok" }`. This confirms process health, **not** provider reachability, model quality, or completed training.
- `POST /api/analyze`: structured explanation request.

The frontend's `VITE_API_BASE_URL` points to this service. Provider credentials are backend-only configuration.

## Analyze request

```json
{"report_text":"Synthetic report text.","report_type":"radiology"}
```

`report_text` is a non-whitespace string up to 20,000 characters, trimmed before inference. `report_type` must be one of `radiology`, `lab`, `pathology`, `clinical`, `discharge`, `other`. Invalid, absent, whitespace-only, oversized, or unsupported values return HTTP 422.

## Analyze response

```json
{
  "summary":"Plain-language explanation.",
  "key_findings":["A report-grounded observation."],
  "recommendations":["Discuss the original report with a clinician."],
  "disclaimer":"This information is for education only and is not medical advice. Consult a licensed clinician for diagnosis or treatment.",
  "source":"hosted_model",
  "parse_warning":false
}
```

| Source | Meaning |
| --- | --- |
| `hosted_model` | Actual configured OpenAI-compatible chat-completions response. |
| `hf_inference` | Actual configured dedicated Hugging Face text-generation endpoint response. |
| `local_model` | Actual existing local checkpoint response. |
| `fallback` | No model interpretation was produced. Any matches are explicitly labelled source-text excerpts, not confirmed clinical findings. |

The server always supplies the full mandatory disclaimer; model output cannot replace it. A structured JSON response or supported textual headings can be parsed. Text headings support aliases and multiline lists. Missing/malformed required fields, invalid list members, missing summary, or truncated oversized output set `parse_warning: true`. A provider failure or empty provider response returns a 200 **fallback** response; it is not a successful model evaluation.

The UI must display both fallback and parse warnings clearly. Empty findings do not establish normality. Model responses are not independently verified medical conclusions.

## Known operational limits

Requests make one provider attempt with configured network inactivity deadlines. An httpx inactivity timeout is not a strict overall wall-clock timeout. The browser has a separate 90-second deadline and cancellation; browser abort does not guarantee already-started provider computation stops. This anonymous portfolio API still needs deployment-level request limits, monitoring and service configuration before public release. No user-record database or report persistence is implemented.
