import csv
import hashlib
import json
import math
from io import StringIO
from typing import Any

from app.errors import AppError

MAX_BYTES = 10 * 1024 * 1024


def parse_records(filename: str, content: bytes) -> tuple[str, list[dict[str, Any]]]:
    if len(content) > MAX_BYTES:
        raise AppError(413, "dataset_too_large", "Dataset exceeds the 10 MB Demo limit")
    suffix = filename.lower().rsplit(".", 1)[-1]
    try:
        text = content.decode("utf-8-sig")
        if suffix == "csv":
            return "csv", list(csv.DictReader(StringIO(text)))
        if suffix == "jsonl":
            return "jsonl", [json.loads(line) for line in text.splitlines() if line.strip()]
        if suffix == "json":
            payload = json.loads(text)
            if not isinstance(payload, list):
                raise ValueError("Alpaca JSON must be an array")
            return "alpaca", payload
    except (UnicodeDecodeError, json.JSONDecodeError, csv.Error, ValueError) as exc:
        raise AppError(400, "dataset_parse_failed", "Dataset could not be parsed") from exc
    raise AppError(415, "dataset_format_unsupported", "Use CSV, JSONL, or Alpaca JSON")


def clean_and_split(rows: list[dict[str, Any]], validation_ratio: float = 0.2) -> dict:
    clean = []
    seen = set()
    duplicates = 0
    rejected = 0
    for row in rows:
        instruction = str(row.get("instruction") or row.get("prompt") or "").strip()
        input_text = str(row.get("input") or row.get("input_text") or "").strip()
        output_text = str(row.get("output") or row.get("response") or "").strip()
        if not instruction or not output_text or len(instruction) > 4000 or len(output_text) > 8000:
            rejected += 1
            continue
        fingerprint = hashlib.sha256(
            f"{instruction}\0{input_text}\0{output_text}".lower().encode()
        ).hexdigest()
        if fingerprint in seen:
            duplicates += 1
            continue
        seen.add(fingerprint)
        bucket = int(fingerprint[:8], 16) / 0xFFFFFFFF
        clean.append(
            {
                "instruction": instruction,
                "input_text": input_text,
                "output_text": output_text,
                "split": "validation" if bucket < validation_ratio else "train",
            }
        )
    if len(clean) > 1 and not any(row["split"] == "validation" for row in clean):
        clean[-1]["split"] = "validation"
    if len(clean) > 1 and not any(row["split"] == "train" for row in clean):
        clean[0]["split"] = "train"
    lengths = sorted(len(row["instruction"]) + len(row["input_text"]) for row in clean)
    p95_index = max(math.ceil(len(lengths) * 0.95) - 1, 0) if lengths else 0
    statistics = {
        "input_length_min": min(lengths, default=0),
        "input_length_avg": round(sum(lengths) / len(lengths), 2) if lengths else 0,
        "input_length_p95": lengths[p95_index] if lengths else 0,
        "input_length_max": max(lengths, default=0),
    }
    return {
        "records": clean,
        "duplicates": duplicates,
        "rejected": rejected,
        "statistics": statistics,
    }
