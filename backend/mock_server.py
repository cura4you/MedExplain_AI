"""
mock_server.py — patches call_hf_inference to return a slightly-off format
(model forgets the "Summary:" prefix) so parse_structured_response fires and
returns the silent failure: { "summary": "Summary unavailable from model response." }

Run:
    python3 mock_server.py

Then in another terminal (or browser/Postman):
    curl -s -X POST http://127.0.0.1:8000/api/analyze \
      -H "Content-Type: application/json" \
      -d '{"report_text": "elevated WBC, mild tachycardia", "report_type": "blood test"}' \
      | python3 -m json.tool
"""

import main  # import the real app

# ── Patch: replace call_hf_inference with one that returns a
#    slightly-off model response (no "Summary:" prefix on the summary line)
def _bad_hf_inference(prompt: str):
    return [
        {
            "generated_text": (
                # model forgot the "Summary:" label — uses "Overview:" instead
                "Overview: The blood test shows elevated white blood cell count.\n"
                "Key findings: elevated WBC, mild tachycardia\n"
                "Recommendations: follow up with physician\n"
                "Disclaimer: Not medical advice.\n"
            )
        }
    ]

main.call_hf_inference = _bad_hf_inference

# ── Start the patched server ──────────────────────────────────────────────────
import uvicorn
uvicorn.run(main.app, host="127.0.0.1", port=8000)
