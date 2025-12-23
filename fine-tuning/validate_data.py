#!/usr/bin/env python3
import argparse
import json
import os
from typing import Dict, List


REQUIRED_FIELDS = ("prompt", "completion", "report_type")
REQUIRED_SECTIONS = ("Summary:", "Key findings:", "Recommendations:", "Disclaimer:")


def load_jsonl(path: str) -> List[Dict[str, str]]:
    rows = []
    with open(path, "r", encoding="utf-8") as handle:
        for line in handle:
            rows.append(json.loads(line))
    return rows


def validate_rows(rows: List[Dict[str, str]]) -> Dict[str, int]:
    stats = {
        "rows": len(rows),
        "missing_fields": 0,
        "missing_sections": 0,
    }

    for row in rows:
        if any(field not in row or not row[field] for field in REQUIRED_FIELDS):
            stats["missing_fields"] += 1
        completion = row.get("completion", "")
        if not all(section in completion for section in REQUIRED_SECTIONS):
            stats["missing_sections"] += 1

    return stats


def main() -> None:
    parser = argparse.ArgumentParser(description="Validate prepared training data.")
    parser.add_argument(
        "--train-path",
        default=os.path.join("fine-tuning", "data", "train_data.jsonl"),
    )
    parser.add_argument(
        "--eval-path",
        default=os.path.join("fine-tuning", "data", "eval_data.jsonl"),
    )
    parser.add_argument(
        "--output-path",
        default=os.path.join("fine-tuning", "data", "processed", "validation.json"),
    )
    args = parser.parse_args()

    train_rows = load_jsonl(args.train_path)
    eval_rows = load_jsonl(args.eval_path)

    payload = {
        "train": validate_rows(train_rows),
        "eval": validate_rows(eval_rows),
    }

    os.makedirs(os.path.dirname(args.output_path), exist_ok=True)
    with open(args.output_path, "w", encoding="utf-8") as handle:
        json.dump(payload, handle, indent=2)


if __name__ == "__main__":
    main()
