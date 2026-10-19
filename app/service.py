import json
from contextlib import suppress
from time import perf_counter
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.dataset_pipeline import clean_and_split, parse_records
from app.db import DatasetRecord, JobRecord, SampleRecord
from app.demo_model import infer
from app.errors import AppError
from app.schemas import DatasetSummary, JobResponse


def import_dataset(db: Session, name: str, filename: str, content: bytes) -> DatasetSummary:
    source_format, rows = parse_records(filename, content)
    result = clean_and_split(rows)
    records = result["records"]
    if not records:
        raise AppError(400, "dataset_empty", "No valid instruction samples remained")
    train_count = sum(row["split"] == "train" for row in records)
    validation_count = len(records) - train_count
    dataset = DatasetRecord(
        name=name.strip(),
        format=source_format,
        record_count=len(records),
        train_count=train_count,
        validation_count=validation_count,
        duplicate_count=result["duplicates"],
        rejected_count=result["rejected"],
        statistics_json=json.dumps(result["statistics"]),
    )
    db.add(dataset)
    db.flush()
    db.add_all(SampleRecord(dataset_id=dataset.id, **record) for record in records)
    db.commit()
    db.refresh(dataset)
    return _dataset_summary(dataset)


def get_dataset(db: Session, dataset_id: UUID) -> DatasetSummary:
    dataset = db.get(DatasetRecord, str(dataset_id))
    if dataset is None:
        raise AppError(404, "dataset_not_found", "Dataset was not found")
    return _dataset_summary(dataset)


def validate_training(db: Session, dataset_id: UUID, mode: str, app_env: str) -> JobResponse:
    dataset = db.get(DatasetRecord, str(dataset_id))
    if dataset is None:
        raise AppError(404, "dataset_not_found", "Dataset was not found")
    if mode == "lora":
        if app_env == "demo":
            raise AppError(
                409,
                "training_resource_required",
                "LoRA is opt-in and disabled in Demo mode; provide a local model in Full mode",
            )
        raise AppError(
            501,
            "training_cli_required",
            "Run scripts/train_lora.py with an explicit local model path",
        )
    checks = {
        "schema_valid": True,
        "has_train_split": dataset.train_count > 0,
        "has_validation_split": dataset.validation_count > 0,
        "model_downloaded": False,
        "training_started": False,
        "message": "Dataset validated; no model training was performed.",
    }
    job = JobRecord(
        kind="training",
        status="succeeded",
        dataset_id=dataset.id,
        result_json=json.dumps(checks),
    )
    db.add(job)
    db.commit()
    db.refresh(job)
    return _job_response(job)


def evaluate(db: Session, dataset_id: UUID) -> JobResponse:
    dataset = db.get(DatasetRecord, str(dataset_id))
    if dataset is None:
        raise AppError(404, "dataset_not_found", "Dataset was not found")
    samples = db.scalars(
        select(SampleRecord).where(
            SampleRecord.dataset_id == dataset.id,
            SampleRecord.split == "validation",
        )
    ).all()
    if not samples:
        samples = db.scalars(
            select(SampleRecord).where(SampleRecord.dataset_id == dataset.id).limit(20)
        ).all()
    latencies = []
    exact = 0
    structured = 0
    started = perf_counter()
    for sample in samples:
        text, _, latency = infer(f"{sample.instruction}\n{sample.input_text}")
        latencies.append(latency)
        exact += int(text.strip() == sample.output_text.strip())
        with suppress(json.JSONDecodeError):
            structured += int(isinstance(json.loads(text), dict))
    elapsed = perf_counter() - started
    total = len(samples)
    metrics = {
        "sample_count": total,
        "exact_match": round(exact / total, 4),
        "structured_json_rate": round(structured / total, 4),
        "average_latency_ms": round(sum(latencies) / total, 4),
        "throughput_samples_per_second": round(total / elapsed, 2) if elapsed else 0,
        "candidate": "demo-rule",
        "measured": True,
    }
    job = JobRecord(
        kind="evaluation",
        status="succeeded",
        dataset_id=dataset.id,
        result_json=json.dumps(metrics),
    )
    db.add(job)
    db.commit()
    db.refresh(job)
    return _job_response(job)


def get_job(db: Session, task_id: UUID) -> JobResponse:
    job = db.get(JobRecord, str(task_id))
    if job is None:
        raise AppError(404, "job_not_found", "Job was not found")
    return _job_response(job)


def _dataset_summary(dataset: DatasetRecord) -> DatasetSummary:
    return DatasetSummary(
        id=dataset.id,
        name=dataset.name,
        format=dataset.format,
        record_count=dataset.record_count,
        train_count=dataset.train_count,
        validation_count=dataset.validation_count,
        duplicate_count=dataset.duplicate_count,
        rejected_count=dataset.rejected_count,
        statistics=json.loads(dataset.statistics_json),
        created_at=dataset.created_at,
    )


def _job_response(job: JobRecord) -> JobResponse:
    return JobResponse(
        task_id=job.id,
        kind=job.kind,
        status=job.status,
        progress=100,
        result=json.loads(job.result_json),
        created_at=job.created_at,
    )
