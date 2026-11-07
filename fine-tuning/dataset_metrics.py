#!/usr/bin/env python3
import argparse
import json
import os
from typing import Dict, List


def load_jsonl(path: str) -> List[Dict[str, str]]:
    rows = []
    with open(path, "r", encoding="utf-8") as handle:
        for line in handle:
            rows.append(json.loads(line))
    return rows


def compute_metrics(rows: List[Dict[str, str]]) -> Dict[str, float]:
    if not rows:
        return {"count": 0, "avg_completion_chars": 0.0, "disclaimer_rate": 0.0}

    total_chars = 0
    disclaimer_hits = 0
    for row in rows:
        completion = row.get("completion", "")
        total_chars += len(completion)
        if "Disclaimer:" in completion:
            disclaimer_hits += 1

    return {
        "count": len(rows),
        "avg_completion_chars": total_chars / len(rows),
        "disclaimer_rate": disclaimer_hits / len(rows),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Measure reference text statistics; this does not run a model.")
    parser.add_argument(
        "--eval-path",
        default=os.path.join("fine-tuning", "data", "eval_data.jsonl"),
    )
    parser.add_argument(
        "--output-path",
        default=os.path.join("fine-tuning", "data", "processed", "eval_results.json"),
    )
    args = parser.parse_args()

    rows = load_jsonl(args.eval_path)
    metrics = compute_metrics(rows)
    metrics["scope"] = "Reference completion text statistics only; not model output or clinical evaluation."
    metrics["model_inference_performed"] = False

    os.makedirs(os.path.dirname(args.output_path), exist_ok=True)
    with open(args.output_path, "w", encoding="utf-8") as handle:
        json.dump(metrics, handle, indent=2)


if __name__ == "__main__":
    main()
