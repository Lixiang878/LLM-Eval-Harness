"""llm-eval-harness 命令行入口。"""
from __future__ import annotations

import argparse
import glob
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
# cli.py 位于 <repo>/src/llm_eval_harness/cli.py，向上两级即仓库根目录
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, "src"))

from llm_eval_harness import __version__  # noqa: E402
from llm_eval_harness.analysis import badcase as badcase_mod  # noqa: E402
from llm_eval_harness.analysis import report as report_mod  # noqa: E402
from llm_eval_harness.models.clients import build_client  # noqa: E402
from llm_eval_harness.pipeline import run  # noqa: E402


def cmd_run(args):
    spec = {"type": "mock", "name": args.model, "profile": args.profile}
    client = build_client(spec)
    result = run(model_client=client, benchmark_path=args.benchmark,
                 rubric_path=args.rubric, out_path=args.out)
    s = result["summary"]["avg_per_dimension"]
    print(f"[ok] model={result['model']} items={result['summary']['n']} "
          f"overall={s['overall']}")
    print(f"[ok] 结果已写入: {args.out}")
    return 0


def cmd_report(args):
    paths = []
    for p in args.results:
        paths += sorted(glob.glob(p))
    results = report_mod.load_results(paths)
    report_mod.write_report(results, args.out, args.chart)
    print(f"[ok] 对比报告已写入: {args.out}")
    if args.chart:
        print(f"[ok] 对比图表: {args.chart}")
    return 0


def cmd_badcase(args):
    with open(args.result, "r", encoding="utf-8") as f:
        result = json.load(f)
    badcase_mod.write(result, args.out, args.threshold)
    print(f"[ok] Bad Case 归因已写入: {args.out}")
    return 0


def build_parser():
    p = argparse.ArgumentParser(
        prog="llm-eval-harness",
        description="轻量大模型评测框架：多模型对比 / LLM-as-Judge / Bad Case 归因")
    p.add_argument("--version", action="version",
                   version=f"llm-eval-harness {__version__}")
    sub = p.add_subparsers(dest="cmd", required=True)

    r = sub.add_parser("run", help="运行一次评测")
    r.add_argument("--model", default="mock", help="模型名称（仅用于结果标识）")
    r.add_argument("--profile", default="strong",
                   choices=["strong", "weak", "random"],
                   help="mock 客户端质量档位")
    r.add_argument("--benchmark",
                   default=os.path.join(ROOT, "configs", "benchmarks", "general_qa.json"))
    r.add_argument("--rubric", default=None, help="自定义评分量表 JSON 路径")
    r.add_argument("--out", default=os.path.join(ROOT, "results", "run_mock.json"))
    r.set_defaults(func=cmd_run)

    rep = sub.add_parser("report", help="生成多模型对比报告")
    rep.add_argument("results", nargs="+", help="一个或多个 result JSON 路径（支持通配符）")
    rep.add_argument("--out", default=os.path.join(ROOT, "results", "report.md"))
    rep.add_argument("--chart", default=None, help="可选：输出对比柱状图 PNG 路径")
    rep.set_defaults(func=cmd_report)

    bc = sub.add_parser("badcase", help="Bad Case 归因")
    bc.add_argument("result", help="单次评测结果 JSON 路径")
    bc.add_argument("--out", default=os.path.join(ROOT, "results", "badcase.md"))
    bc.add_argument("--threshold", type=float, default=6.0, help="低分判定阈值（0-10）")
    bc.set_defaults(func=cmd_badcase)
    return p


def main(argv=None):
    args = build_parser().parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
