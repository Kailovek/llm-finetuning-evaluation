from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, FastAPI, File, Form, Request, UploadFile, status
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.config import Settings, get_settings
from app.db import Base, create_session_factory, get_db
from app.demo_model import infer
from app.errors import install_handlers
from app.schemas import (
    DatasetSummary,
    EvaluationRequest,
    InferenceRequest,
    InferenceResponse,
    JobResponse,
    TrainingRequest,
)
from app.service import evaluate, get_dataset, get_job, import_dataset, validate_training


def create_app(settings: Settings | None = None) -> FastAPI:
    resolved = settings or get_settings()

    @asynccontextmanager
    async def lifespan(app: FastAPI) -> AsyncIterator[None]:
        resolved.data_dir.mkdir(parents=True, exist_ok=True)
        resolved.output_dir.mkdir(parents=True, exist_ok=True)
        engine, factory = create_session_factory(resolved.database_url)
        app.state.engine = engine
        app.state.session_factory = factory
        Base.metadata.create_all(engine)
        yield
        engine.dispose()

    app = FastAPI(
        title="LLM Fine-tuning and Evaluation Toolbox",
        version="0.1.0",
        description="Demo-first dataset and measured evaluation service with opt-in LoRA",
        lifespan=lifespan,
    )
    install_handlers(app)
    api = APIRouter(prefix="/api/v1")
    Database = Annotated[Session, Depends(get_db)]
    DatasetFile = Annotated[UploadFile, File()]
    DatasetName = Annotated[str, Form(min_length=1, max_length=128)]

    @api.get("/health", tags=["health"])
    def health(request: Request) -> dict:
        with request.app.state.engine.connect() as connection:
            connection.execute(text("SELECT 1"))
        return {
            "service": "llm-finetuning-evaluation",
            "status": "healthy",
            "mode": resolved.app_env,
            "dependencies": {
                "database": "ready",
                "demo_inference": "ready",
                "training_runtime": "disabled" if resolved.app_env == "demo" else "unavailable",
                "model_weights": "disabled",
            },
        }

    @api.post(
        "/datasets/import",
        response_model=DatasetSummary,
        status_code=status.HTTP_201_CREATED,
        tags=["datasets"],
    )
    async def upload_dataset(db: Database, name: DatasetName, file: DatasetFile) -> DatasetSummary:
        return import_dataset(db, name, file.filename or "dataset", await file.read())

    @api.get("/datasets/{dataset_id}", response_model=DatasetSummary, tags=["datasets"])
    def read_dataset(dataset_id: UUID, db: Database) -> DatasetSummary:
        return get_dataset(db, dataset_id)

    @api.post(
        "/training-jobs",
        response_model=JobResponse,
        status_code=status.HTTP_202_ACCEPTED,
        tags=["training"],
    )
    def create_training_job(payload: TrainingRequest, db: Database) -> JobResponse:
        return validate_training(db, payload.dataset_id, payload.mode, resolved.app_env)

    @api.post(
        "/evaluation-jobs",
        response_model=JobResponse,
        status_code=status.HTTP_202_ACCEPTED,
        tags=["evaluation"],
    )
    def create_evaluation_job(payload: EvaluationRequest, db: Database) -> JobResponse:
        return evaluate(db, payload.dataset_id)

    @api.get("/jobs/{task_id}", response_model=JobResponse, tags=["jobs"])
    def read_job(task_id: UUID, db: Database) -> JobResponse:
        return get_job(db, task_id)

    @api.post("/inference", response_model=InferenceResponse, tags=["inference"])
    def run_inference(payload: InferenceRequest) -> InferenceResponse:
        text_value, structured, latency = infer(payload.prompt)
        return InferenceResponse(
            text=text_value,
            provider="demo-rule",
            latency_ms=latency,
            structured=structured,
        )

    app.include_router(api)
    return app


app = create_app()
