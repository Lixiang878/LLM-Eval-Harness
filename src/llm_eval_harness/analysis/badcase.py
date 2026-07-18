"""Bad Case 归因：从单次评测结果中筛出低分样本并分类。"""
from __future__ import annotations

import os

DIM_LABEL = {
    "accuracy": "事实性错误/幻觉",
    "completeness": "覆盖不全",
    "relevance": "答非所问/跑题",
    "format": "表达与格式差",
}

THRESHOLD = 6.0


def analyze(result: dict, threshold: float = THRESHOLD) -> list:
    rubric = result.get("rubric", [])
    bad = []
    for rec in result["records"]:
        weak = [d for d in rubric if rec["scores"].get(d, 10) < threshold]
        if not weak:
            continue
        worst = min(weak, key=lambda d: rec["scores"].get(d, 0))
        bad.append({
            "id": rec["id"],
            "category": rec.get("category", ""),
            "overall": rec["overall"],
            "weak_dims": weak,
            "reason": DIM_LABEL.get(worst, worst),
            "prompt": rec["prompt"],
            "response": rec["response"],
        })
    return bad


def render_markdown(bad: list) -> str:
    if not bad:
        return "# Bad Case 归因\n\n未发现低于阈值的样本，模型表现稳定。"
    lines = ["# Bad Case 归因", f"共 {len(bad)} 条低分样本（阈值 {THRESHOLD}）\n"]
    for b in bad:
        lines.append(f"## {b['id']}（{b['category']}）— 总分 {b['overall']}")
        lines.append(f"- 归因：**{b['reason']}**")
        lines.append(f"- 弱维度：{', '.join(b['weak_dims'])}")
        lines.append(f"- 问题：{b['prompt']}")
        lines.append(f"- 回答：{b['response']}")
        lines.append("")
    return "\n".join(lines)


def write(result: dict, out_md: str, threshold: float = THRESHOLD) -> str:
    bad = analyze(result, threshold)
    md = render_markdown(bad)
    os.makedirs(os.path.dirname(out_md) or ".", exist_ok=True)
    with open(out_md, "w", encoding="utf-8") as f:
        f.write(md)
    return md
