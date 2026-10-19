# 模块说明与阅读顺序

[返回首页](../README.md) · [业务导读](business-design.md) · [训练指南](training.md)

## 推荐阅读路径

`schemas.py → dataset_pipeline.py → db.py → service.py → main.py → train_lora.py`

| 模块 | 核心接口 | 职责 |
| --- | --- | --- |
| [app/dataset_pipeline.py](../app/dataset_pipeline.py) | parse_records / clean_and_split | 文件解析、字段映射、去重、划分、统计 |
| [app/service.py](../app/service.py) | import_dataset / get_dataset | 数据集与样本持久化、摘要查询 |
| [app/service.py](../app/service.py) | validate_training / evaluate / get_job | 前置校验、评测计算与任务查询 |
| [app/demo_model.py](../app/demo_model.py) | infer | 过流、过压、通信等问题的结构化规则基线 |
| [app/db.py](../app/db.py) | DatasetRecord / SampleRecord / JobRecord | 数据集、样本、任务与数据库会话 |
| [app/schemas.py](../app/schemas.py) | DatasetSummary / JobResponse / InferenceResponse | 数据与任务结果契约 |
| [app/main.py](../app/main.py) | create_app | 生命周期、路由及依赖注入 |
| [app/config.py](../app/config.py) | Settings | 环境配置 |
| [app/errors.py](../app/errors.py) | AppError / install_handlers | 业务异常和字段校验错误 |
| [scripts/train_lora.py](../scripts/train_lora.py) | main | 本地模型与 LoRA 训练入口 |
| [scripts/generate_demo_dataset.py](../scripts/generate_demo_dataset.py) | main | 按模板生成 100 / 1000 / 10000 条指令数据 |

## 数据管线契约

`parse_records(filename, content)` 返回格式标识和记录列表；`clean_and_split(rows)` 返回：

- records：包含 instruction、input_text、output_text、split。
- duplicates / rejected：重复与拒绝数量。
- statistics：输入字符长度的 min、avg、p95、max。

导入服务计算训练与验证数量，并将上述内容映射到关系模型。

## 训练入口契约

CLI 参数：`--model-path`、`--dataset-path`、`--output-dir`。JSONL 使用 instruction、input、output。默认训练配置、分词和保存方式见 [training.md](training.md)。

## 评测契约

评测任务通过 dataset_id 读取样本，将 instruction 与 input_text 拼成推理输入；预测文本与 output_text 进行文本比较。输出统计通过 JobResponse.result 保存，同时保留 candidate 标识和样本数量。

## 测试源码导航

[tests/test_toolbox.py](../tests/test_toolbox.py) 包含数据清洗、去重、校验任务语义、评测字段、结构化推理和服务接口的断言。测试源码用于定位这些契约的预期行为；本页不记录执行结果。
