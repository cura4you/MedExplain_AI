#!/usr/bin/env python3
import argparse
import json
import os
import random
import itertools
from dataclasses import dataclass
from typing import List, Dict


@dataclass
class Example:
    prompt: str
    completion: str
    report_type: str


REPORT_TYPES = ["radiology", "lab", "pathology", "clinical", "discharge", "other"]
CONDITIONS = [
    "mild cardiomegaly",
    "no acute disease",
    "elevated glucose",
    "iron deficiency anemia",
    "possible pneumonia",
    "normal renal function",
    "borderline high cholesterol",
    "mild dehydration",
]
PROMPT_TEMPLATE = (
    "System: You are MedExplain, a medical report explanation assistant.\n"
    "You must be clear, concise, and avoid giving medical advice.\n"
    "User report type: {report_type}\n"
    "User report text: {report_text}\n"
    "Task: Provide a structured explanation for a non-medical reader.\n"
    "Required format:\n"
    "- Summary: <plain-language summary>\n"
    "- Key findings: <comma-separated list>\n"
    "- Recommendations: <safe next steps>\n"
    "- Disclaimer: <safety notice>\n"
)
DISCLAIMER = (
    "This information is for education only and is not medical advice. "
    "Consult a licensed clinician for diagnosis or treatment."
)


def build_prompt(report_text: str, report_type: str) -> str:
    return PROMPT_TEMPLATE.format(report_type=report_type, report_text=report_text)


def build_completion(report_type: str, key_findings: List[str]) -> str:
    findings = "; ".join(key_findings)
    return (
        f"Summary: This {report_type} report indicates {findings}.\n"
        f"Key findings: {', '.join(key_findings)}.\n"
        "Recommendations: Discuss these findings with a licensed clinician.\n"
        f"Disclaimer: {DISCLAIMER}"
    )


def write_jsonl(path: str, rows: List[Dict[str, str]]) -> None:
    with open(path, "w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row) + "\n")


def write_stats(path: str, total: int, train_count: int, eval_count: int, examples: List[Example]) -> None:
    type_counts: Dict[str, int] = {report_type: 0 for report_type in REPORT_TYPES}
    for example in examples:
        type_counts[example.report_type] += 1

    payload = {
        "total": total,
        "train": train_count,
        "eval": eval_count,
        "report_type_counts": type_counts,
    }
    with open(path, "w", encoding="utf-8") as handle:
        json.dump(payload, handle, indent=2)


def main() -> None:
    parser = argparse.ArgumentParser(description="Prepare fine-tuning data.")
    parser.add_argument("--total", type=int, default=8000)
    parser.add_argument("--eval-ratio", type=float, default=0.1)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument(
        "--output-dir",
        default=os.path.join("fine-tuning", "data"),
    )
    args = parser.parse_args()

    total = args.total
    if total < 2 * len(REPORT_TYPES):
        raise SystemExit("--total must allow at least one row per report type in both splits.")
    eval_count = int(total * args.eval_ratio)
    train_count = total - eval_count

    if not 0 < args.eval_ratio < 1:
        raise SystemExit("--eval-ratio must be strictly between 0 and 1.")
    if train_count < len(REPORT_TYPES) or eval_count < len(REPORT_TYPES):
        raise SystemExit("Each split needs at least one row per report type.")
    # Hold out whole unique template cases BEFORE oversampling. The templates
    # are deliberately small synthetic demonstrations, not a clinical dataset.
    rng = random.Random(args.seed)
    train_cases, eval_cases = [], []
    pairs = list(itertools.combinations(CONDITIONS, 2))
    rng.shuffle(pairs)
    heldout = max(1, min(len(pairs) - 1, round(len(pairs) * args.eval_ratio)))
    # All report types share the same holdout assignment: relabelling a case
    # must not leak an evaluation report into the training split.
    for report_type in REPORT_TYPES:
        for index, findings in enumerate(pairs):
            report_text = f"The report notes {findings[0]} and {findings[1]}."
            row = {"prompt": build_prompt(report_text, report_type),
                   "completion": build_completion(report_type, list(findings)), "report_type": report_type}
            (eval_cases if index < heldout else train_cases).append(row)
    def expand(cases, count):
        # Cycle through report types even when a small smoke dataset is requested.
        balanced = sorted(cases, key=lambda row: (row["prompt"].split("User report text:")[-1], row["report_type"]))
        rows = [dict(balanced[i % len(balanced)]) for i in range(count)]
        rng.shuffle(rows)
        return rows
    train_rows = expand(train_cases, train_count)
    eval_rows = expand(eval_cases, eval_count)
    examples = [Example(**row) for row in train_rows + eval_rows]

    os.makedirs(args.output_dir, exist_ok=True)
    processed_dir = os.path.join(args.output_dir, "processed")
    os.makedirs(processed_dir, exist_ok=True)
    train_path = os.path.join(args.output_dir, "train_data.jsonl")
    eval_path = os.path.join(args.output_dir, "eval_data.jsonl")

    write_jsonl(train_path, train_rows)
    write_jsonl(eval_path, eval_rows)

    stats_path = os.path.join(processed_dir, "stats.json")
    write_stats(stats_path, total, train_count, eval_count, examples)
    with open(stats_path, encoding="utf-8") as handle:
        stats = json.load(handle)
    stats.update(scope="Oversampled synthetic template demonstrations, not independent clinical cases or model evaluation.",
        unique_train_prompts=len({r["prompt"] for r in train_rows}), unique_eval_prompts=len({r["prompt"] for r in eval_rows}),
        available_unique_template_cases=len(pairs), heldout_template_cases=heldout)
    with open(stats_path, "w", encoding="utf-8") as handle:
        json.dump(stats, handle, indent=2)


if __name__ == "__main__":
    main()
