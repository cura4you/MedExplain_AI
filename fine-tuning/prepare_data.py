#!/usr/bin/env python3
import argparse
import json
import os
import random
from dataclasses import dataclass
from typing import List, Dict


@dataclass
class Example:
    prompt: str
    completion: str
    report_type: str


REPORT_TYPES = ["radiology", "lab", "clinical", "other"]
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


def generate_examples(total: int, seed: int) -> List[Example]:
    random.seed(seed)
    examples: List[Example] = []
    for _ in range(total):
        report_type = random.choice(REPORT_TYPES)
        findings = random.sample(CONDITIONS, k=2)
        report_text = f"The report notes {findings[0]} and {findings[1]}."
        prompt = build_prompt(report_text, report_type)
        completion = build_completion(report_type, findings)
        examples.append(Example(prompt=prompt, completion=completion, report_type=report_type))
    return examples


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

    total = max(args.total, 3000)
    eval_count = int(total * args.eval_ratio)
    train_count = total - eval_count

    examples = generate_examples(total=total, seed=args.seed)

    train_rows = [
        {"prompt": ex.prompt, "completion": ex.completion, "report_type": ex.report_type}
        for ex in examples[:train_count]
    ]
    eval_rows = [
        {"prompt": ex.prompt, "completion": ex.completion, "report_type": ex.report_type}
        for ex in examples[train_count:]
    ]

    os.makedirs(args.output_dir, exist_ok=True)
    processed_dir = os.path.join(args.output_dir, "processed")
    os.makedirs(processed_dir, exist_ok=True)
    train_path = os.path.join(args.output_dir, "train_data.jsonl")
    eval_path = os.path.join(args.output_dir, "eval_data.jsonl")

    write_jsonl(train_path, train_rows)
    write_jsonl(eval_path, eval_rows)

    stats_path = os.path.join(processed_dir, "stats.json")
    write_stats(stats_path, total, train_count, eval_count, examples)


if __name__ == "__main__":
    main()
