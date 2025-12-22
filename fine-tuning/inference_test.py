#!/usr/bin/env python3
import argparse
import os
import yaml


def load_config(path: str) -> dict:
    with open(path, "r", encoding="utf-8") as handle:
        return yaml.safe_load(handle)


def main() -> None:
    parser = argparse.ArgumentParser(description="Quick inference test for fine-tuned model.")
    parser.add_argument("--config", default=os.path.join("fine-tuning", "config.yaml"))
    parser.add_argument(
        "--prompt",
        default=(
            "System: You are MedExplain, a medical report explanation assistant.\n"
            "User report type: radiology\n"
            "User report text: The report notes mild cardiomegaly and no acute disease.\n"
            "Task: Provide a structured explanation for a non-medical reader.\n"
            "Required format:\n"
            "- Summary: <plain-language summary>\n"
            "- Key findings: <comma-separated list>\n"
            "- Recommendations: <safe next steps>\n"
            "- Disclaimer: <safety notice>\n"
        ),
    )
    args = parser.parse_args()

    config = load_config(args.config)
    model_name = config["model"]["name"]
    output_dir = config["training"]["output_dir"]

    try:
        from unsloth import FastLanguageModel
        from transformers import TextStreamer
    except ImportError as exc:
        raise SystemExit("Missing inference deps. Install requirements.txt and extras for unsloth.") from exc

    model, tokenizer = FastLanguageModel.from_pretrained(
        model_name=model_name,
        max_seq_length=config["model"]["max_seq_length"],
        dtype=None,
        load_in_4bit=config["model"]["load_in_4bit"],
    )

    if os.path.exists(output_dir):
        model = FastLanguageModel.get_peft_model(model)
        model.load_adapter(output_dir)

    FastLanguageModel.for_inference(model)
    streamer = TextStreamer(tokenizer)
    inputs = tokenizer(args.prompt, return_tensors="pt").to(model.device)
    model.generate(**inputs, streamer=streamer, max_new_tokens=256)


if __name__ == "__main__":
    main()
