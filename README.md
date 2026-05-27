<div align="center">

<img src="https://img.shields.io/badge/MedExplain-AI-ff8b5e?style=for-the-badge&logo=heart&logoColor=white" alt="MedExplain AI" height="40"/>

# MedExplain AI

**Translate clinical language into calm, human guidance.**

Paste any medical report → get a structured plain-language explanation with safety-first recommendations, powered by a fine-tuned LLM.

<br/>

[![Python](https://img.shields.io/badge/Python-3.11+-3776AB?style=flat-square&logo=python&logoColor=white)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.110+-009688?style=flat-square&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![React](https://img.shields.io/badge/React-18-61DAFB?style=flat-square&logo=react&logoColor=black)](https://react.dev)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.4-3178C6?style=flat-square&logo=typescript&logoColor=white)](https://typescriptlang.org)
[![Vite](https://img.shields.io/badge/Vite-5-646CFF?style=flat-square&logo=vite&logoColor=white)](https://vitejs.dev)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow?style=flat-square)](LICENSE)

<br/>

[**Quick Start**](#-quick-start) · [**API Reference**](#-api-reference) · [**Training Pipeline**](#-training-pipeline) · [**Deployment**](#-deployment)

</div>

---

## What it does

MedExplain AI takes a pasted medical report — radiology, lab results, pathology, clinical notes, or discharge summaries — and returns a structured, plain-language breakdown that a non-medical reader can actually understand.

```
Input:  "Chest X-ray demonstrates mild cardiomegaly with no acute
         pulmonary infiltrates. Mild pleural effusion noted bilaterally."

Output: {
  "summary":         "Your chest X-ray shows a slightly enlarged heart
                      and a small amount of fluid around both lungs.
                      No signs of pneumonia were found.",
  "key_findings":    ["cardiomegaly", "bilateral pleural effusion"],
  "recommendations": ["Follow up with your cardiologist promptly.",
                      "Seek urgent care if shortness of breath worsens."],
  "disclaimer":      "This is for education only — not medical advice.",
  "source":          "hf_inference",
  "parse_warning":   false
}
```

Every response includes a mandatory safety disclaimer and a `parse_warning` flag that fires when the model's output couldn't be fully parsed — so the frontend can surface a visible warning instead of silently showing broken results.

---

## ✨ Features

| | Feature | Detail |
|---|---|---|
| 🧠 | **Fine-tuned LLM** | ERNIE-4.5-VL-28B fine-tuned with LoRA on 7,200 structured medical explanation examples |
| 🏥 | **6 report types** | Radiology · Lab/Blood · Pathology · Clinical notes · Discharge summary · Other |
| ⚠️ | **Parse warning flag** | `parse_warning: true` when model output is malformed — no more silent failures |
| 🔄 | **Graceful fallback** | Keyword-scan fallback (20-term vocabulary) when the model is unreachable |
| 🛡️ | **Safety-first** | Mandatory disclaimer on every response, non-negotiable |
| 🚀 | **Deploy anywhere** | Railway · Render · Vercel configs included out of the box |

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                        Browser / Client                      │
│                React + TypeScript (Vite)                     │
└───────────────────────────┬─────────────────────────────────┘
                            │  POST /api/analyze
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                    FastAPI Backend                           │
│                                                             │
│  build_prompt()  ──►  call_hf_inference()                   │
│                            │                                │
│                    ┌───────┴────────┐                       │
│                    │                │                       │
│             HF Inference API   Local model weights          │
│                    │                │                       │
│                    └───────┬────────┘                       │
│                            │                                │
│              parse_structured_response()                    │
│              (alias-aware label matching)                   │
│                            │                                │
│                     fallback_parse()  ◄── on any failure    │
└───────────────────────────┬─────────────────────────────────┘
                            │
                     AnalyzeResponse
              { summary, key_findings, recommendations,
                disclaimer, source, parse_warning }
```

---

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- Node.js 18+

### 1 · Backend

```bash
cd backend
pip install -r requirements.txt

# Optional: set your HuggingFace token for model inference
export HF_TOKEN=hf_...
export MODEL_NAME=baidu/ERNIE-4.5-VL-28B-A3B-Thinking   # default

uvicorn main:app --reload --host 127.0.0.1 --port 8000
```

> Backend is live at `http://127.0.0.1:8000`  
> Swagger UI at `http://127.0.0.1:8000/docs`

### 2 · Frontend

```bash
cd frontend
npm install

# Point the frontend at your backend
echo "VITE_API_BASE_URL=http://localhost:8000" > .env

npm run dev
```

> Frontend is live at `http://localhost:5173`

---

## 📡 API Reference

### `POST /api/analyze`

**Request**
```json
{
  "report_text": "Paste the full report text here.",
  "report_type": "radiology | lab | pathology | clinical | discharge | other"
}
```

**Response**
```json
{
  "summary":         "string — plain-language summary",
  "key_findings":    ["string"],
  "recommendations": ["string"],
  "disclaimer":      "string — always present",
  "source":          "hf_inference | local_model | fallback",
  "parse_warning":   false
}
```

**`source` values**

| Value | Meaning |
|---|---|
| `hf_inference` | Generated by HuggingFace Inference API |
| `local_model` | Generated by locally-loaded model weights |
| `fallback` | Model unavailable — keyword scan used instead |

**`parse_warning` flag**  
`true` when the model's output used unexpected label names (e.g. `"Overview:"` instead of `"Summary:"`) and the summary couldn't be extracted. The parser now accepts aliases — `Impression`, `Assessment`, `Overview`, `Conclusion` — but sets this flag if none matched, so the frontend can show a visible warning rather than silently returning broken output.

See [`docs/API.md`](docs/API.md) for full reference including error codes.

---

## 🧬 Training Pipeline

The fine-tuning pipeline runs in four stages:

```bash
# 1. Generate 8,000 structured training examples
python3 fine-tuning/prepare_data.py --total 8000 --eval-ratio 0.1

# 2. Validate the generated data
python3 fine-tuning/validate_data.py

# 3. Fine-tune with LoRA adapters
python3 fine-tuning/train_model.py --config fine-tuning/config.yaml

# 4. Evaluate on held-out examples
python3 fine-tuning/evaluate_model.py --eval-path fine-tuning/data/eval_data.jsonl
```

### Training config (LoRA)

| Parameter | Value |
|---|---|
| Base model | `baidu/ERNIE-4.5-VL-28B-A3B-Thinking` |
| LoRA rank `r` | 16 |
| LoRA alpha | 32 |
| Dropout | 0.05 |
| Quantization | 4-bit (`load_in_4bit`) |
| Max seq length | 2048 |
| Batch size | 2 (grad accum × 4) |
| Learning rate | 2e-4 |
| Epochs | 1 |
| Precision | FP16 |

### Dataset stats

| Split | Count | Report types |
|---|---|---|
| Train | 7,200 | Radiology · Lab · Clinical · Other |
| Eval | 800 | Same distribution |
| **Total** | **8,000** | — |

### Latest eval results

```
count              : 800 examples
avg_completion_chars: 337.7 chars
disclaimer_rate    : 100%   ← safety disclaimer present on every output
```

---

## 🚢 Deployment

Three deployment targets are pre-configured:

<details>
<summary><strong>Railway (backend)</strong></summary>

`railway.toml` is included. Push to Railway and it auto-detects the config:

```toml
[build]
builder = "NIXPACKS"

[deploy]
startCommand = "uvicorn backend.main:app --host 0.0.0.0 --port $PORT"
restartPolicyType = "ON_FAILURE"
```

Set environment variables in the Railway dashboard:
- `HF_TOKEN` — your HuggingFace API token
- `CORS_ORIGINS` — your frontend URL (e.g. `https://medexplain.vercel.app`)

</details>

<details>
<summary><strong>Render (backend)</strong></summary>

`render.yaml` is included:

```yaml
services:
  - type: web
    name: medexplain-backend
    env: python
    rootDir: backend
    buildCommand: pip install -r requirements.txt
    startCommand: uvicorn main:app --host 0.0.0.0 --port $PORT
```

</details>

<details>
<summary><strong>Vercel (frontend)</strong></summary>

`vercel.json` is included. Connect the repo in Vercel and add:
- `VITE_API_BASE_URL` = your backend URL

```json
{
  "buildCommand": "cd frontend && npm install && npm run build",
  "outputDirectory": "frontend/dist"
}
```

</details>

---

## 📁 Project Structure

```
MedExplain_AI/
├── backend/
│   ├── main.py                # FastAPI app — build_prompt, parse_structured_response, fallback_parse
│   └── requirements.txt
│
├── frontend/
│   ├── src/
│   │   ├── App.tsx            # Main UI — input panel, results, parse_warning banner
│   │   ├── styles.css         # Design system
│   │   └── main.tsx
│   ├── package.json
│   └── vite.config.ts
│
├── fine-tuning/
│   ├── prepare_data.py        # Generates 8k JSONL training examples
│   ├── train_model.py         # LoRA fine-tuning
│   ├── evaluate_model.py      # Eval on held-out set
│   ├── validate_data.py       # Schema validation
│   ├── config.yaml            # Training hyperparameters
│   └── data/
│       ├── train_data.jsonl
│       ├── eval_data.jsonl
│       └── processed/         # eval_results.json, stats.json
│
├── docs/
│   ├── API.md                 # Full API reference
│   ├── TRAINING.md            # Training guide
│   ├── DEPLOYMENT.md          # Deploy instructions
│   ├── DEBUG_LOG.md           # Bug log with root causes + fixes
│   └── DEMO_SCRIPT.md
│
├── scripts/
│   ├── run_codex_bootstrap.sh
│   ├── git_checkpoint.sh
│   └── upload_to_hf.sh        # Push model to HuggingFace Hub
│
├── PROMPTS/                   # Prompt templates and safety guidance
├── railway.toml               # Railway deployment config
├── render.yaml                # Render deployment config
└── vercel.json                # Vercel deployment config
```

---

## 🛡️ Safety

Every response from MedExplain AI includes a non-removable disclaimer:

> *"This information is for education only and is not medical advice. Consult a licensed clinician for diagnosis or treatment."*

The `parse_warning` flag exists specifically to prevent silent failures from reaching users without a visible warning. A `200 OK` response does not mean the output is complete — always check this field in any integration.

**MedExplain AI is not a medical device and must not be used for clinical decision-making.**

---

<div align="center">

Built by [@moh0405](https://github.com/moh0405)

</div>
