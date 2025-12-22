# MedExplain AI

MedExplain AI is an end-to-end medical report explanation assistant. It ingests a pasted report, analyzes it with a fine-tuned LLM, and returns a structured, plain-language summary with safety disclaimers. This repository is organized for a full hackathon pipeline: data prep, fine-tuning, evaluation, backend API, frontend UI, and deployment artifacts.

## Why this is judge-friendly
- Clear phases with commits and tags for each milestone.
- Reproducible scripts and configs for data prep, training, and inference.
- Safety-first responses with explicit medical disclaimers.
- Full-stack demo: FastAPI backend + React frontend.

## Quickstart (high level)
- Phase 0: scaffold + docs
- Phase 1: environment setup scripts
- Phase 2–4: data prep, training, evaluation
- Phase 5–7: backend, frontend, deployment

Detailed commands live in `docs/` and `scripts/`.

## Repository layout
- `fine-tuning/` data prep, training, evaluation scripts
- `backend/` FastAPI service with `/api/analyze`
- `frontend/` React + TypeScript UI
- `docs/` training, API, deployment, demo scripts
- `scripts/` bootstrap and git helpers
- `PROMPTS/` prompt templates and safety guidance
- `demo/` demo assets and recordings

## Safety disclaimer
MedExplain AI is for informational purposes only and does not provide medical advice. It is not a substitute for professional diagnosis or treatment.
