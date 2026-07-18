# 更新日志 / Changelog

本项目遵循 [Keep a Changelog](https://keepachangelog.com/zh-CN/1.1.0/) 规范，
版本号遵循 [Semantic Versioning](https://semver.org/lang/zh-CN/)。

## [Unreleased]

## [0.1.0] - 2026-07-18

### Added
- 评测主流程 `pipeline.run`：在评测集上运行模型并对每条回答打分。
- 模型客户端：`MockClient`（离线演示）与 `OpenAICompatibleClient`
  （兼容 OpenAI / 文心 / 通义 / 本地 vLLM）。
- LLM-as-Judge：基于评分量表（rubric）的自动打分，含离线 `MockJudge`
  与真实 LLM 裁判。
- 多模型对比报告（`analysis/report.py`），可选柱状图输出。
- Bad Case 归因（`analysis/badcase.py`），按最弱维度自动分类。
- 命令行入口 `llm-eval-harness`，含 `run` / `report` / `badcase` 子命令。
- 内置样例评测集与默认评分量表。
- 单元测试（pytest）与 CI（Python 3.9–3.12 + ruff）。

### Notes
- 离线场景零第三方依赖即可运行完整流程。
- 仓库为 src-layout 可安装包，支持 `pip install -e .` 与控制台脚本。
