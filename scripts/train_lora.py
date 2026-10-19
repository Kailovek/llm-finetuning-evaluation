"""Explicit opt-in LoRA entry point. It never resolves a remote model identifier."""

import argparse
from pathlib import Path


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Train a LoRA adapter from a local model directory"
    )
    parser.add_argument("--model-path", type=Path, required=True)
    parser.add_argument("--dataset-path", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    if not args.model_path.is_dir():
        raise SystemExit(
            "model-path must be an existing local directory; remote downloads are disabled"
        )
    if not args.dataset_path.is_file():
        raise SystemExit("dataset-path must be an existing local JSONL file")

    try:
        import torch
        from datasets import load_dataset
        from peft import LoraConfig, get_peft_model
        from transformers import (
            AutoModelForCausalLM,
            AutoTokenizer,
            DataCollatorForLanguageModeling,
            Trainer,
            TrainingArguments,
        )
    except ImportError as exc:
        raise SystemExit(
            "Install the optional 'training' dependencies before LoRA training"
        ) from exc

    tokenizer = AutoTokenizer.from_pretrained(args.model_path, local_files_only=True)
    model = AutoModelForCausalLM.from_pretrained(
        args.model_path,
        local_files_only=True,
        torch_dtype=torch.float16 if torch.cuda.is_available() else torch.float32,
    )
    model = get_peft_model(
        model,
        LoraConfig(
            task_type="CAUSAL_LM",
            r=8,
            lora_alpha=16,
            lora_dropout=0.05,
            target_modules="all-linear",
        ),
    )
    dataset = load_dataset("json", data_files=str(args.dataset_path), split="train")

    def tokenize(row):
        text = (
            f"Instruction: {row['instruction']}\n"
            f"Input: {row.get('input', '')}\n"
            f"Answer: {row['output']}"
        )
        return tokenizer(text, truncation=True, max_length=512)

    tokenized = dataset.map(tokenize, remove_columns=dataset.column_names)
    arguments = TrainingArguments(
        output_dir=str(args.output_dir),
        num_train_epochs=1,
        per_device_train_batch_size=1,
        gradient_accumulation_steps=4,
        logging_steps=5,
        save_strategy="epoch",
        report_to=[],
    )
    trainer = Trainer(
        model=model,
        args=arguments,
        train_dataset=tokenized,
        data_collator=DataCollatorForLanguageModeling(tokenizer, mlm=False),
    )
    trainer.train()
    model.save_pretrained(args.output_dir)


if __name__ == "__main__":
    main()
