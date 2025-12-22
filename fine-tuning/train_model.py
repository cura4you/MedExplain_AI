#!/usr/bin/env python3
import argparse
import os
import yaml


def load_config(path: str) -> dict:
    with open(path, "r", encoding="utf-8") as handle:
        return yaml.safe_load(handle)


def main() -> None:
    parser = argparse.ArgumentParser(description="Train LoRA adapters with Unsloth.")
    parser.add_argument("--config", default=os.path.join("fine-tuning", "config.yaml"))
    args = parser.parse_args()

    config = load_config(args.config)
    model_name = config["model"]["name"]
    output_dir = config["training"]["output_dir"]

    try:
        from unsloth import FastLanguageModel
        from datasets import load_dataset
        from trl import SFTTrainer
        from transformers import TrainingArguments
    except ImportError as exc:
        raise SystemExit("Missing training deps. Install requirements.txt and extras for unsloth.") from exc

    model, tokenizer = FastLanguageModel.from_pretrained(
        model_name=model_name,
        max_seq_length=config["model"]["max_seq_length"],
        dtype=None,
        load_in_4bit=config["model"]["load_in_4bit"],
    )

    model = FastLanguageModel.get_peft_model(
        model,
        r=config["lora"]["r"],
        target_modules=config["lora"]["target_modules"],
        lora_alpha=config["lora"]["alpha"],
        lora_dropout=config["lora"]["dropout"],
        bias="none",
        use_gradient_checkpointing="unsloth",
    )

    dataset = load_dataset(
        "json",
        data_files={
            "train": config["data"]["train_path"],
            "validation": config["data"]["eval_path"],
        },
    )

    def format_example(example: dict) -> dict:
        text = f"{example['prompt']}\n{example['completion']}"
        return {"text": text}

    dataset = dataset.map(format_example)

    training_args = TrainingArguments(
        output_dir=output_dir,
        per_device_train_batch_size=config["training"]["batch_size"],
        gradient_accumulation_steps=config["training"]["grad_accum_steps"],
        num_train_epochs=config["training"]["epochs"],
        learning_rate=config["training"]["learning_rate"],
        warmup_steps=config["training"]["warmup_steps"],
        logging_steps=config["training"]["logging_steps"],
        save_steps=config["training"]["save_steps"],
        evaluation_strategy="steps",
        eval_steps=config["training"]["eval_steps"],
        fp16=config["training"]["fp16"],
        bf16=config["training"]["bf16"],
    )

    trainer = SFTTrainer(
        model=model,
        tokenizer=tokenizer,
        train_dataset=dataset["train"],
        eval_dataset=dataset["validation"],
        dataset_text_field="text",
        max_seq_length=config["model"]["max_seq_length"],
        args=training_args,
    )

    trainer.train()
    trainer.save_model(output_dir)


if __name__ == "__main__":
    main()
