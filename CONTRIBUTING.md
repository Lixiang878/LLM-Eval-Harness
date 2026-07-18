# 贡献指南 / Contributing

感谢你有兴趣为 `llm-eval-harness` 做贡献。本项目是一个轻量大模型评测框架，
目标是保持**小、可读、可复现、易扩展**。以下约定有助于 PR 被快速合并。

## 开发环境

```bash
git clone https://github.com/Lixiang878/llm-eval-harness.git
cd llm-eval-harness
python -m pip install --upgrade pip
pip install -e .[dev]        # 安装可编辑包 + pytest + ruff
```

离线演示不需要任何第三方依赖；只有接入真实模型 API（`requests`）或生成图表
（`matplotlib`）时才需要可选依赖，可通过 `pip install -e .[api]` / `.[chart]` 安装。

## 本地校验

提交前请保证两项检查通过：

```bash
ruff check .        # 代码风格与静态检查
pytest -q           # 单元测试
```

未安装 `ruff` 时也可只跑 `pytest`。CI 会在 Python 3.9–3.12 上重复这两项检查。

## 代码结构约定

- 核心逻辑放在 `src/llm_eval_harness/` 下，按职责分子包：`models/`（模型客户端）、
  `judge/`（评分量表与裁判）、`analysis/`（报告与归因）、`pipeline.py`（编排）。
- 新增复用逻辑优先做成**可插拔组件**：模型客户端继承 `BaseModelClient`，裁判继承
  `BaseJudge`，评分量表为 JSON。
- 保持离线可运行：新增功能不应强制依赖网络或第三方包。

## 如何扩展

**新增一个评测集**：在 `configs/benchmarks/` 下新建 JSON，字段见
`configs/benchmarks/general_qa.json`（`id` / `category` / `prompt` / `reference`）。
然后 `llm-eval-harness run --benchmark path/to/your.json`。

**接入新的模型**：在 `src/llm_eval_harness/models/clients.py` 实现 `BaseModelClient`
的 `complete()`，并在 `build_client()` 工厂里登记类型。若走 OpenAI 兼容协议，
通常直接复用 `OpenAICompatibleClient` 并传入对应 `base_url` 即可。

**自定义评分维度**：编辑 `configs/default_rubric.json`，或运行时用
`--rubric your_rubric.json` 指定。维度键会被裁判与报告自动识别。

## 提交与 PR

1. 从 `main` 切出特性分支：`git checkout -b feat/xxx`。
2. 保持提交原子、信息清晰（中文英文均可，说明"为什么"而非仅"做了什么"）。
3. 更新 `CHANGELOG.md` 的 `Unreleased` 段。
4. 发起 PR，按模板填写变更说明与测试方式。

## 问题反馈

请使用仓库的 Issue 模板提交 Bug 或功能建议；涉及安全漏洞请走
[Security Advisory](https://github.com/Lixiang878/llm-eval-harness/security/advisories/new)
私密渠道，不要公开披露。
