# REST API 与数据契约

[返回首页](../README.md) · [架构设计](architecture.md) · [训练 CLI](training.md)

基础地址：`http://127.0.0.1:8103/api/v1`。Swagger：`/docs`；OpenAPI：`/openapi.json`。模型与路由见 [schemas.py](../app/schemas.py)、[main.py](../app/main.py)。

## 路由

| 方法与路径 | 模型 / 状态 | 用途 |
| --- | --- | --- |
| GET /health | 状态对象 | 服务状态 |
| POST /datasets/import | DatasetSummary / 201 | multipart 文件导入 |
| GET /datasets/{dataset_id} | DatasetSummary | 数据质量摘要 |
| POST /training-jobs | JobResponse / 202 | 数据前置校验 |
| POST /evaluation-jobs | JobResponse / 202 | 规则基线评测 |
| GET /jobs/{task_id} | JobResponse | 持久化结果查询 |
| POST /inference | InferenceResponse | 结构化规则基线推理 |

## 数据导入

multipart 字段为 `name` 和 `file`。PowerShell 7 可使用以下方式：

```powershell
$base = "http://127.0.0.1:8103/api/v1"
$file = Get-Item -LiteralPath .\examples\instruction_samples.jsonl
$dataset = Invoke-RestMethod -Method Post -Uri "$base/datasets/import" `
    -Form @{ name = "instruction-reference"; file = $file }
$dataset
```

也可在 Swagger 的上传表单选择文件。响应包含 id、name、format、record_count、train_count、validation_count、duplicate_count、rejected_count、statistics 和 created_at。统计使用字符长度，不是 token 长度。

## 数据前置校验与评测

```powershell
$checkBody = @{ dataset_id = $dataset.id; mode = "validation_only" } | ConvertTo-Json
$check = Invoke-RestMethod -Method Post -Uri "$base/training-jobs" `
    -ContentType "application/json" -Body $checkBody

$evalBody = @{ dataset_id = $dataset.id; candidate = "demo-rule" } | ConvertTo-Json
$evaluation = Invoke-RestMethod -Method Post -Uri "$base/evaluation-jobs" `
    -ContentType "application/json" -Body $evalBody
$evaluation.result
Invoke-RestMethod -Uri "$base/jobs/$($evaluation.task_id)"
```

`JobResponse` 包含 task_id、kind、status、progress、result、created_at。接口在当前请求内处理并返回结果。校验检查训练与验证划分信息，评测返回候选标识和指标。

LoRA 训练使用 [独立 CLI](training.md)，与上述数据校验请求分别调用。

## 推理

```powershell
$body = Get-Content -LiteralPath .\examples\inference_request.json -Raw -Encoding UTF8
$prediction = Invoke-RestMethod -Method Post -Uri "$base/inference" `
    -ContentType "application/json; charset=utf-8" -Body ([Text.Encoding]::UTF8.GetBytes($body))
$prediction.structured
```

推理请求包含 prompt（1—4000 字符），响应包含 text、provider、latency_ms、structured。公开规则基线输出 category、action、risk。

## 错误

业务错误与请求字段校验采用 code、message、request_id、details 结构：

- dataset_not_found / job_not_found：HTTP 404。
- dataset_parse_failed / dataset_empty：HTTP 400。
- dataset_too_large：HTTP 413。
- dataset_format_unsupported：HTTP 415。
- 请求字段约束错误：HTTP 422。

调用方按 OpenAPI 模型处理 UUID 与字段类型，通过响应中的 dataset_id / task_id 关联页面，按 candidate 字段解释指标来源。
