# 公开内容与授权说明

本仓库中的公开代码、架构设计与技术文档由 **Hzhikai** 基于本人实际项目经验独立整理并授权发布，用于 LLM 应用开发交流、开源共同学习与求职作品展示。

## 公开工程内容

| 技术方向 | 公开内容 |
| --- | --- |
| SFT 数据准备 | CSV、JSONL、Alpaca JSON 解析，字段映射、清洗与质量统计 |
| 数据一致性 | SHA-256 去重、内容指纹划分、样本与数据集关联 |
| 参数高效微调 | Transformers 本地模型加载、PEFT-LoRA 注入、Trainer 训练入口 |
| 训练组织 | 超参数、梯度累积、日志间隔、检查点策略与 Adapter 保存 |
| 推理与评测 | 结构化规则基线、文本匹配、JSON 对象率、延迟与样本吞吐 |
| 任务服务 | 训练前数据校验、评测任务持久化、UUID 结果查询 |
| 工程组织 | OpenAPI 契约、配置示例、Windows 脚本、示例输入与测试源码 |

## 阅读与使用

建议从 [README](README.md)、[业务设计导读](docs/business-design.md)和[训练指南](docs/training.md)阅读，再对照 [数据管线](app/dataset_pipeline.py)、[训练入口](scripts/train_lora.py)与[评测服务](app/service.py)。运行配置见 [.env.example](.env.example)，依赖分组见 [pyproject.toml](pyproject.toml)。

## 作者与许可证

Hzhikai 创作并发布的代码与文档采用 [MIT License](LICENSE)。第三方框架和依赖遵循各自许可证，详见 [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md)。模型和数据的使用遵守相应来源的授权条款。

欢迎阅读、引用、讨论和改进，并请保留作者与许可证信息。
