#!/usr/bin/env python3
import argparse
import json
import os
import re
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
        "unique_prompts": len({r.get("prompt", "") for r in rows}),
        "duplicate_prompt_rows": len(rows) - len({r.get("prompt", "") for r in rows}),
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


def case_key(row):
    """Canonicalize the bundled template case independently of report type/order."""
    prompt = row.get("prompt", "")
    match = re.search(r"User report text:\s*([^\n]+)", prompt)
    text = (match.group(1) if match else prompt).strip().lower().rstrip(".")
    text = re.sub(r"^the report notes\s+", "", text)
    return tuple(sorted(part.strip() for part in text.split(" and ")))


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

    overlap = {r.get("prompt") for r in train_rows} & {r.get("prompt") for r in eval_rows}
    payload["cross_split_overlap"] = len(overlap)
    case_overlap = {case_key(row) for row in train_rows} & {case_key(row) for row in eval_rows}
    payload["cross_split_template_case_overlap"] = len(case_overlap)
    payload["scope"] = "Synthetic reference data checks only; no model inference or clinical validation."
    payload["passed"] = not overlap and not case_overlap and all(
        payload[split][key] == 0 for split in ["train", "eval"] for key in ["missing_fields", "missing_sections"])
    os.makedirs(os.path.dirname(args.output_path) or ".", exist_ok=True)
    with open(args.output_path, "w", encoding="utf-8") as handle:
        json.dump(payload, handle, indent=2)
    if not payload["passed"]:
        raise SystemExit("Dataset validation failed; inspect validation output.")


if __name__ == "__main__":
    main()
