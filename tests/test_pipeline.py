import json
import os
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "src"))

from llm_eval_harness.judge.llm_judge import MockJudge  # noqa: E402
from llm_eval_harness.models.clients import MockClient  # noqa: E402
from llm_eval_harness.pipeline import load_benchmark, run  # noqa: E402

BENCH = os.path.join(ROOT, "configs", "benchmarks", "general_qa.json")


def test_offline_run_strong_beats_weak():
    items = load_benchmark(BENCH)
    strong = run(model_client=MockClient(name="strong", profile="strong"),
                 judge=MockJudge(), benchmark=items)
    weak = run(model_client=MockClient(name="weak", profile="weak"),
               judge=MockJudge(), benchmark=items)
    assert strong["summary"]["n"] == len(items)
    s_strong = strong["summary"]["avg_per_dimension"]["overall"]
    s_weak = weak["summary"]["avg_per_dimension"]["overall"]
    assert s_strong > s_weak


def test_run_writes_valid_output():
    items = load_benchmark(BENCH)
    with tempfile.TemporaryDirectory() as d:
        out = os.path.join(d, "r.json")
        run(model_client=MockClient(name="strong", profile="strong"),
            judge=MockJudge(), benchmark=items, out_path=out)
        assert os.path.exists(out)
        with open(out, "r", encoding="utf-8") as f:
            data = json.load(f)
        assert data["summary"]["n"] == len(items)
        assert "records" in data
