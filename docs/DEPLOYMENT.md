# Vercel deployment

The full application is deployed at **https://medexplain-ai-cura4you.vercel.app** under the owner's `mohammad-petiwalas-projects` Vercel scope. The connected repository is `cura4you/MedExplain_AI`.

## One project, two services

`vercel.json` explicitly declares:

- `frontend`: root `frontend/`, Vite, `npm ci`, `npm run build`, output `dist`.
- `backend`: root `backend/`, FastAPI, entrypoint `main:app`, Python 3.12.
- Public `/api/*` and `/health` route to the backend with their original paths. Other traffic routes to the frontend.

The production frontend uses same-origin API calls when `VITE_API_BASE_URL` is unset. Development retains the localhost API default. There is no separate backend hosting account or database to provision.

This uses [Vercel Services](https://vercel.com/docs/services) and its [service configuration](https://vercel.com/docs/services/config-reference). `.vercelignore` excludes local environments, model/training data, docs/screenshots, test drivers, and installed dependencies from source uploads. Only lightweight web dependencies are installed for the Python service; Torch and local model weights are not included.

## Server configuration

Set these with the Vercel environment manager for Production and Preview:

- `AI_BASE_URL`: configured OpenAI-compatible provider origin/base path.
- `AI_MODEL`: a model available to the account; this release uses `gemini-3.1-flash-lite`.
- `AI_API_KEY`: server-only credential; never put it in a `VITE_*` variable.
- `AI_TIMEOUT_SECONDS`: this deployment uses 35 seconds per network operation. It is not a strict overall wall-clock deadline.
- `CORS_ORIGINS`: `https://medexplain-ai-cura4you.vercel.app`. Requests from each deployment's own frontend are same-origin.

Leave `MODEL_LOCAL_PATH`, legacy HF overrides and production `VITE_API_BASE_URL` unset for this hosted path. Store secrets through the provider's environment manager, not in Git, command arguments, screenshots, or documentation. Changing server environment values requires a new deployment.

## Deploy and verify

The existing local checkout is linked to project `prj_WMDJRUBAw2xw0l5Pn7z5bhLfoOk9`. Use the intended owner scope:

```sh
vercel deploy --prod --scope mohammad-petiwalas-projects
```

For your own installation, link your own project and configure its environment first. The Git connection is verified for the organization repository; pushes can also trigger Vercel builds.

`/health` verifies process health only. Confirm actual inference with synthetic text and require `source: hosted_model`. Reproduce the hosted checks:

```sh
.venv/bin/python backend/live_verify.py \
  --base-url https://medexplain-ai-cura4you.vercel.app \
  --model-label gemini-3.1-flash-lite --output-dir /private/tmp/medexplain-hosted-api

UI_BASE=https://medexplain-ai-cura4you.vercel.app \
LIVE_UI_ARTIFACTS=/private/tmp/medexplain-hosted-browser \
  node frontend/scripts/live-check.mjs
```

The host applies its function/resource limits; provider allowance and availability are external dependencies. This portfolio service has no application report database, but hosting and model providers can retain operational data under their policies. Public API rate/spend controls, monitoring, restore requirements if storage is added, and clinical validation remain separate operational work.

[Recorded production results](deployment/README.md) · [API contract](API.md) · [Local model audit](live-model-verification/README.md)

Railway and Render files remain alternative deployment templates. No such deployment was made in this release. No trained ERNIE adapter was uploaded or verified.
