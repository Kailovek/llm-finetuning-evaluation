def test_health_is_honest_about_training_runtime(client):
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    assert response.json()["dependencies"]["training_runtime"] == "disabled"
    assert response.json()["dependencies"]["model_weights"] == "disabled"


def test_jsonl_import_cleans_deduplicates_and_splits(client):
    row = '{"instruction":"检查告警","input":"过流","output":"安全停机"}'
    content = f'{row}\n{row}\n{{"instruction":"","output":"bad"}}'.encode()
    response = client.post(
        "/api/v1/datasets/import",
        data={"name": "quality-demo"},
        files={"file": ("data.jsonl", content, "application/jsonl")},
    )
    assert response.status_code == 201
    body = response.json()
    assert body["record_count"] == 1
    assert body["duplicate_count"] == 1
    assert body["rejected_count"] == 1
    assert body["statistics"]["input_length_max"] > 0


def test_validation_only_job_does_not_claim_training(client, dataset_id):
    response = client.post(
        "/api/v1/training-jobs",
        json={"dataset_id": dataset_id, "mode": "validation_only"},
    )
    assert response.status_code == 202
    result = response.json()["result"]
    assert result["schema_valid"] is True
    assert result["training_started"] is False
    assert result["model_downloaded"] is False


def test_lora_is_blocked_in_demo(client, dataset_id):
    response = client.post("/api/v1/training-jobs", json={"dataset_id": dataset_id, "mode": "lora"})
    assert response.status_code == 409
    assert response.json()["code"] == "training_resource_required"


def test_evaluation_records_measured_metrics(client, dataset_id):
    response = client.post(
        "/api/v1/evaluation-jobs",
        json={"dataset_id": dataset_id, "candidate": "demo-rule"},
    )
    assert response.status_code == 202
    result = response.json()["result"]
    assert result["measured"] is True
    assert result["sample_count"] >= 1
    assert result["structured_json_rate"] == 1.0
    assert result["average_latency_ms"] >= 0


def test_inference_returns_structured_output(client):
    response = client.post("/api/v1/inference", json={"prompt": "减速时出现过压告警"})
    assert response.status_code == 200
    assert response.json()["structured"]["category"] == "overvoltage"
    assert response.json()["provider"] == "demo-rule"
