# Training Guide

## Overview
This project uses a data-prep pipeline to generate JSONL training/eval data, then fine-tunes a base LLM with LoRA adapters.

## Base model
- Hugging Face: `baidu/ERNIE-4.5-VL-28B-A3B-Thinking`

## Workflow
1) Prepare data with `fine-tuning/prepare_data.py`.
2) Train with `fine-tuning/train_model.py`.
3) Evaluate with `fine-tuning/evaluate_model.py`.

## Commands used
```bash
python3 fine-tuning/prepare_data.py --total 8000 --eval-ratio 0.1
python3 fine-tuning/train_model.py --config fine-tuning/config.yaml
python3 fine-tuning/evaluate_model.py --eval-path fine-tuning/data/eval_data.jsonl
```

## GPU-ready training
Run this on a GPU machine with enough VRAM for the base model:
```bash
python3 fine-tuning/train_model.py --config fine-tuning/config.yaml
```

Expected runtime (guide):
- Small test run (1 epoch, 8k rows): ~1–2 hours on a single A100-class GPU.
- Adjust `fine-tuning/config.yaml` for batch size and epochs to fit your hardware.

## Latest results
Sample `eval_results.json` (regenerate by running the evaluation command above):
```json
{
  "count": 800,
  "avg_completion_chars": 182.5,
  "disclaimer_rate": 1.0
}
```

## Notes
- Training artifacts and stats are stored under `fine-tuning/data/processed/`.
- The prompt template includes safety disclaimers for medical information.
