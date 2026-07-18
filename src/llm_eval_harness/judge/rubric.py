"""LLM-as-Judge 评分量表（rubric）。"""
from __future__ import annotations

import json
import os

DEFAULT_RUBRIC = {
    "accuracy": {
        "label": "准确性",
        "en": "Accuracy",
        "scale": [0, 10],
        "description": "答案事实正确性，与参考答案一致程度。",
    },
    "completeness": {
        "label": "完整性",
        "en": "Completeness",
        "scale": [0, 10],
        "description": "是否覆盖问题的主要要点。",
    },
    "relevance": {
        "label": "相关性",
        "en": "Relevance",
        "scale": [0, 10],
        "description": "回答是否切题，未跑题或答非所问。",
    },
    "format": {
        "label": "可读性",
        "en": "Readability",
        "scale": [0, 10],
        "description": "表达清晰、结构合理、格式规范。",
    },
}

_RUBRIC_PATH = os.path.join(os.path.dirname(__file__), "default_rubric.json")


def load_rubric(path: str | None = None) -> dict:
    if path and os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    if os.path.exists(_RUBRIC_PATH):
        with open(_RUBRIC_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    return DEFAULT_RUBRIC


def overall(scores: dict, rubric: dict) -> float:
    vals = [v for k, v in scores.items() if k in rubric]
    return round(sum(vals) / len(vals), 2) if vals else 0.0
