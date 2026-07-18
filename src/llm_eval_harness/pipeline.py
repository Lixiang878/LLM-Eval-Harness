"""评测主流程：在评测集上运行模型并对每条回答打分。"""
from __future__ import annotations

import json
import os
from datetime import datetime

from .judge.llm_judge import MockJudge
from .judge.rubric import load_rubric, overall


def load_benchmark(path: str) -> list:
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    if isinstance(data, dict) and "items" in data:
        return data["items"]
    return data


def run(model_client, judge=None, benchmark_path: str | None = None,
       benchmark: list | None = None, rubric_path: str | None = None,
       out_path: str | None = None) -> dict:
    judge = judge or MockJudge()
    rubric = load_rubric(rubric_path)
    items = benchmark if benchmark is not None else load_benchmark(benchmark_path)

    records = []
    for it in items:
        rid = it.get("id", f"item_{len(records)}")
        prompt = it["prompt"]
        reference = it.get("reference", "")
        response = model_client.complete(prompt, item_id=rid, reference=reference)
        scores = judge.score(prompt, response, reference, rubric)
        rec = {
            "id": rid,
            "category": it.get("category", "uncategorized"),
            "prompt": prompt,
            "reference": reference,
            "response": response,
            "scores": scores,
            "overall": overall(scores, rubric),
        }
        records.append(rec)

    result = {
        "model": getattr(model_client, "name", "unknown"),
        "benchmark": os.path.basename(benchmark_path) if benchmark_path else "inline",
        "timestamp": datetime.now().isoformat(timespec="seconds"),
        "rubric": list(rubric.keys()),
        "records": records,
        "summary": _summarize(records, rubric),
    }
    if out_path:
        os.makedirs(os.path.dirname(out_path) or ".", exist_ok=True)
        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
    return result


def _summarize(records, rubric):
    dims = list(rubric.keys())
    agg = {d: round(sum(r["scores"].get(d, 0) for r in records) / max(1, len(records)), 2)
           for d in dims}
    agg["overall"] = round(sum(r["overall"] for r in records) / max(1, len(records)), 2)
    return {"n": len(records), "avg_per_dimension": agg}
