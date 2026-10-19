import json
from collections.abc import Generator
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from app.config import Settings
from app.main import create_app


@pytest.fixture()
def client(tmp_path: Path) -> Generator[TestClient, None, None]:
    settings = Settings(
        database_url=f"sqlite:///{tmp_path / 'toolbox.db'}", output_dir=tmp_path / "outputs"
    )
    with TestClient(create_app(settings)) as value:
        yield value


@pytest.fixture()
def dataset_id(client: TestClient) -> str:
    scenarios = [
        ("分析过流告警 A", "启动过流", "overcurrent", "check_load_and_wiring", "high"),
        (
            "分析过压告警 B",
            "减速过压",
            "overvoltage",
            "check_deceleration_and_braking",
            "high",
        ),
        (
            "分析通信超时 C",
            "通信丢失",
            "communication",
            "check_power_connection_and_timeout",
            "medium",
        ),
    ]
    rows = []
    for instruction, input_text, category, action, risk in scenarios:
        output = json.dumps({"category": category, "action": action, "risk": risk})
        rows.append(json.dumps({"instruction": instruction, "input": input_text, "output": output}))
    content = "\n".join(rows).encode()
    response = client.post(
        "/api/v1/datasets/import",
        data={"name": "demo-sft"},
        files={"file": ("demo.jsonl", content, "application/jsonl")},
    )
    assert response.status_code == 201
    return response.json()["id"]
