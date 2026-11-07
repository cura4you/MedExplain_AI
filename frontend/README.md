# MedExplain AI frontend

A responsive React and TypeScript report workspace with a warm neutral/deep teal identity, fictional examples, structured explanations, source-text comparison, and accessible status feedback.

## Run

Use Node.js 24 (the Vite toolchain requires Node 20.19+ or 22.12+).

```sh
cd frontend
npm ci
cp .env.example .env
# Set VITE_API_BASE_URL to your FastAPI backend.
npm run dev
```

The frontend defaults to `http://localhost:8000`. Allow the frontend origin in the backend's `CORS_ORIGINS` configuration. Real inference requires a working backend model configuration; a keyword fallback is explicitly labelled and is not a model-generated interpretation.

```sh
npm run build
npm run preview
```

## Browser verification

```sh
npx playwright install chromium
# With the frontend already running:
UI_BASE=http://localhost:5173 npm run test:e2e
```

The suite uses synthetic API fixtures to exercise loading, successful and incomplete responses, fallback, HTTP/network/schema errors, cancellation, stale-response prevention, exports, tabs, and responsive layouts. No real patient information or inference token is needed.

To include the actual backend fallback check, point the frontend at an isolated FastAPI instance with no remote model credentials, set a deliberately unavailable local inference endpoint, and configure CORS for the frontend origin. Then add `UI_REAL_BACKEND=true`. This tests integration with the real backend fallback; it does not establish live Hugging Face inference.

See [redesign review and screenshots](../docs/frontend-redesign/README.md). Vite migration notes: [official guide](https://vite.dev/guide/migration).
