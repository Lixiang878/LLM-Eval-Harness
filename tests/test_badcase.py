"""Tests for Bad Case attribution, the `python -m` contract, and run() guard."""

import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "src"))

import pytest  # noqa: E402

from llm_eval_harness import __main__ as main_mod  # noqa: E402
from llm_eval_harness.analysis import badcase as badcase_mod  # noqa: E402
from llm_eval_harness.judge.llm_judge import MockJudge  # noqa: E402
from llm_eval_harness.models.clients import MockClient  # noqa: E402
from llm_eval_harness.pipeline import run  # noqa: E402


def _result(scores):
    return {
        "rubric": ["accuracy", "completeness", "relevance", "format"],
        "records": [{
            "id": "qa_001", "category": "科学", "overall": 5.0,
            "scores": scores,
            "prompt": "什么是傅里叶变换？",
            "response": "这个我不太确定。",
        }],
    }


def test_badcase_reports_custom_threshold():
    res = _result({"accuracy": 5, "completeness": 9, "relevance": 9, "format": 9})
    bad = badcase_mod.analyze(res, threshold=8.0)
    assert bad  # accuracy(5) < 8 -> flagged
    md = badcase_mod.render_markdown(bad, threshold=8.0)
    assert "8.0" in md


def test_badcase_default_threshold_in_header():
    res = _result({"accuracy": 5, "completeness": 9, "relevance": 9, "format": 9})
    bad = badcase_mod.analyze(res, threshold=6.0)
    md = badcase_mod.render_markdown(bad, threshold=6.0)
    assert "6.0" in md


def test_badcase_missing_dimension_is_neutral():
    # A record missing the 'accuracy' key must not be flagged as weak by it.
    res = _result({"completeness": 9, "relevance": 9, "format": 9})
    bad = badcase_mod.analyze(res, threshold=6.0)
    assert bad == []


def test_main_module_exposes_main():
    assert callable(getattr(main_mod, "main", None))


def test_run_requires_benchmark_or_path():
    with pytest.raises(ValueError):
        run(model_client=MockClient(), judge=MockJudge())
