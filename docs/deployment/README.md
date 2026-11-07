# Public release — 2026-11-07

URL: **https://medexplain-ai-cura4you.vercel.app**

Vercel project: `medexplain-ai-cura4you` (`prj_WMDJRUBAw2xw0l5Pn7z5bhLfoOk9`), under `mohammad-petiwalas-projects`. Initial verified deployment: `dpl_BPXNwFLeBk4GthFjQ1VjUVxD1nDF`. The React/Vite and Python/FastAPI services share the public origin. Git connection to `cura4you/MedExplain_AI` was confirmed.

## Hosted checks

| Scope | Result | Evidence |
| --- | --- | --- |
| API process health | `/health` returned `{"status":"ok"}` | Checked independently from inference. |
| Actual hosted model API | 7/7 passed, covering six types and one embedded-instruction case | [API report](public-api/api-report.json), [synthetic transcripts](public-api/synthetic-transcripts.json) |
| Actual Playwright to API to model | 4/4 passed: real results, comparison/export, changed sample, mobile | [Browser report](public-browser/browser-report.json) |
| UI regressions against public frontend | 17/17 passed at 11 widths; API responses intercepted for deterministic failure/state checks | [UI report](public-ui/report.json) |

The real-model checks reject `fallback`, require complete parsing and the mandatory notice, and check selected fictional facts. They establish working application integration, not comprehensive medical accuracy or prompt-injection resistance. UI fixture checks intentionally use mocked API responses; the actual-model browser checks do not.

## Exact screenshots

[Public homepage](homepage.png) · [Empty workspace](workspace.png) · [Mobile homepage](mobile-home.png) · [Actual public model response](public-browser/live-model-result.png) · [Actual public mobile result](public-browser/live-model-mobile.png)

[Capture source](capture-source.json). All inputs and displayed clinical records are fictional. Provider credentials were stored in Vercel server environment settings, never in the frontend, screenshots, or evidence.

The repository retains earlier local verification and its training-claim audit. No completed ERNIE fine-tune, local checkpoint, GPU run, or clinical certification is claimed by this deployment.
