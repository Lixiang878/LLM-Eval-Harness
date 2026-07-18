"""从评测结果 JSON 生成多模型对比报告。"""
from __future__ import annotations

import json
import os


def load_results(paths: list) -> list:
    out = []
    for p in paths:
        with open(p, "r", encoding="utf-8") as f:
            out.append(json.load(f))
    return out


def render_markdown(results: list) -> str:
    if not results:
        return "# 评测报告\n\n（无数据）"
    dims = results[0].get("rubric", [])
    lines = ["# 大模型评测对比报告", "",
             f"模型数：{len(results)}，评测集：{results[0].get('benchmark', '')}", ""]
    header = ["模型", "样本数", "总分(avg)"] + [d for d in dims]
    lines.append("| " + " | ".join(header) + " |")
    lines.append("|" + "|".join(["---"] * len(header)) + "|")
    for r in results:
        s = r["summary"]["avg_per_dimension"]
        row = [r["model"], str(r["summary"]["n"]), f"{s.get('overall', 0):.2f}"]
        row += [f"{s.get(d, 0):.2f}" for d in dims]
        lines.append("| " + " | ".join(row) + " |")
    lines.append("")
    return "\n".join(lines)


def render_chart(results: list, out_png: str | None = None) -> str:
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
        import numpy as np
    except Exception:
        return ""
    dims = results[0].get("rubric", [])
    models = [r["model"] for r in results]
    x = np.arange(len(dims))
    width = 0.8 / max(1, len(models))
    fig, ax = plt.subplots(figsize=(8, 4.5))
    for i, r in enumerate(results):
        s = r["summary"]["avg_per_dimension"]
        vals = [s.get(d, 0) for d in dims]
        ax.bar(x + i * width, vals, width, label=r["model"])
    ax.set_xticks(x + width * (len(models) - 1) / 2)
    ax.set_xticklabels(dims)
    ax.set_ylabel("Score (0-10)")
    ax.set_title("LLM Eval Comparison")
    ax.legend()
    ax.set_ylim(0, 10)
    if out_png:
        os.makedirs(os.path.dirname(out_png) or ".", exist_ok=True)
        fig.tight_layout()
        fig.savefig(out_png, dpi=120)
        return out_png
    return ""


def write_report(results: list, out_md: str, out_png: str | None = None) -> str:
    md = render_markdown(results)
    os.makedirs(os.path.dirname(out_md) or ".", exist_ok=True)
    with open(out_md, "w", encoding="utf-8") as f:
        f.write(md)
    if out_png:
        render_chart(results, out_png)
    return md
