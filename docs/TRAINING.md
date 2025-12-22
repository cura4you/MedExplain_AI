# Training Guide

## Overview
This project uses a data-prep pipeline to generate JSONL training/eval data, then fine-tunes a base LLM with LoRA adapters.

## Workflow
1) Prepare data with `fine-tuning/prepare_data.py`.
2) Train with `fine-tuning/train_model.py`.
3) Evaluate with `fine-tuning/evaluate_model.py`.

## Notes
- Training artifacts and stats are stored under `fine-tuning/data/processed/`.
- The prompt template includes safety disclaimers for medical information.
