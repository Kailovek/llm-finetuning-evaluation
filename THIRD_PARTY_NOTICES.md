# Third-party dependencies · 第三方依赖

Hzhikai 的原创范围为本仓库中的应用实现、集成设计与技术文档。下列开源框架与工具的作者、版权和许可保持不变。

| Dependency | Role | License | Upstream |
| --- | --- | --- | --- |
| FastAPI | REST API and OpenAPI | MIT | [FastAPI](https://github.com/fastapi/fastapi) |
| Uvicorn | ASGI runtime | BSD-3-Clause | [Uvicorn](https://github.com/Kludex/uvicorn) |
| Pydantic / pydantic-settings | Contracts and environment settings | MIT | [Pydantic](https://github.com/pydantic/pydantic) · [Settings](https://github.com/pydantic/pydantic-settings) |
| SQLAlchemy | Dataset and task persistence | MIT | [SQLAlchemy](https://github.com/sqlalchemy/sqlalchemy) |
| python-multipart | Multipart uploads | Apache-2.0 | [python-multipart](https://github.com/Kludex/python-multipart) |
| PyTorch | Training runtime | BSD-style | [PyTorch](https://github.com/pytorch/pytorch) |
| Transformers | Tokenizer, causal model and Trainer | Apache-2.0 | [Transformers](https://github.com/huggingface/transformers) |
| PEFT | LoRA adapter injection and saving | Apache-2.0 | [PEFT](https://github.com/huggingface/peft) |
| Datasets / Accelerate | Training data and runtime integration | Apache-2.0 | [Datasets](https://github.com/huggingface/datasets) · [Accelerate](https://github.com/huggingface/accelerate) |
| pytest / Ruff | Development tools | MIT | [pytest](https://github.com/pytest-dev/pytest) · [Ruff](https://github.com/astral-sh/ruff) |
| HTTPX | API test client | BSD-3-Clause | [HTTPX](https://github.com/encode/httpx) |
| Hatchling | Build backend | MIT | [Hatch](https://github.com/pypa/hatch) |

依赖和版本范围以 [pyproject.toml](pyproject.toml) 为准；训练组件通过 `training` 分组管理。具体许可文本以安装版本的发行包和上游 LICENSE/NOTICE 为准，PyTorch 的完整许可包含附带组件声明。

本仓库通过包管理器使用上述依赖，未复制其完整项目源码。基础模型与外部数据集使用时，应独立核对其来源和授权，应用仓库的 MIT 许可不替代这些条款。
