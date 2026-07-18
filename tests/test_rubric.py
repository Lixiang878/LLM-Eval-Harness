import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "src"))

from llm_eval_harness.judge.rubric import load_rubric, overall  # noqa: E402


def test_load_default():
    r = load_rubric()
    assert "accuracy" in r
    assert "completeness" in r


def test_overall_average():
    r = load_rubric()
    assert overall({"accuracy": 8, "completeness": 6}, r) == 7.0
    assert overall({}, r) == 0.0
