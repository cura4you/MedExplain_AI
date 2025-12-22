# Deployment

## Local
- Backend: `uvicorn backend.main:app --reload`
- Frontend: `npm run dev` (from `frontend/`)

## Hugging Face (model)
- Use `scripts/upload_to_hf.sh` once created in Phase 7.

## Railway/Render (backend)
- Use the provided config file in Phase 7.

## Vercel (frontend)
- Deploy `frontend/` with the Phase 7 config.
