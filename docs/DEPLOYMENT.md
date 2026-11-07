# Deployment preparation

The current release is verified locally with a real hosted model. No new public deployment was performed as part of the model audit. The checked-in host configurations are starting templates, not evidence that a public service is configured or tested.

## Backend

Railway uses the root requirements file and starts `uvicorn backend.main:app`; Render uses `backend/requirements.txt` and `uvicorn main:app`. Configure:

- `AI_BASE_URL`, `AI_MODEL`, `AI_API_KEY` for the chosen server-side provider.
- `CORS_ORIGINS` with the exact deployed frontend origin, not a wildcard.
- A supported Python runtime and host port.
- Deployment-level request/body/rate limits and logs that do not capture report contents or secrets.

The hosted runtime does not require Torch or Transformers. Keep credentials outside Git and `VITE_*`. No automatic ERNIE endpoint is assumed; configure a genuinely running endpoint if using HF. See [backend setup](../backend/README.md).

## Frontend

The Vercel configuration builds `frontend/` and serves `frontend/dist`. Set `VITE_API_BASE_URL` to the deployed backend's HTTPS origin. Provider keys belong only on the backend.

## Before publishing

Build the frontend, run contract/browser tests, configure services and explicit CORS, then verify the candidate host with `/health`, an actual synthetic `/api/analyze` response whose source is a model, visible fallback/error paths, desktop/mobile rendering, and the live Playwright driver. Health alone does not prove inference. Agree the intended public URL before promoting it.

## Model publishing

No adapter was uploaded. `scripts/upload_to_hf.sh` is an optional publication tool that requires an explicit destination plus real saved adapter files. Only run it when you intend to publish verified artifacts.
