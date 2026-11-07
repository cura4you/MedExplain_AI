#!/usr/bin/env python3
"""Deprecated ambiguous command: reference text metrics are not model evaluation."""
raise SystemExit(
    "This old command did not run a model. Use fine-tuning/dataset_metrics.py for reference text statistics, "
    "or backend/live_verify.py against an explicitly configured API for synthetic live inference checks."
)
