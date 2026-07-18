"""LLM-as-Judge：对模型回答自动打分。"""
from __future__ import annotations

import json
import re
from abc import ABC, abstractmethod

from .rubric import load_rubric


class BaseJudge(ABC):
    @abstractmethod
    def score(self, prompt: str, response: str, reference: str, rubric: dict) -> dict:
        ...


class MockJudge(BaseJudge):
    """启发式离线裁判（词面重叠 + 长度启发），可复现、无需网络。
    用于演示与 CI。"""

    def score(self, prompt, response, reference, rubric):
        dims = list(rubric.keys())
        if not response or not response.strip():
            return {d: 0.0 for d in dims}
        resp_tokens = set(_tokens(response))
        ref_tokens = set(_tokens(reference)) if reference else set()

        if ref_tokens:
            overlap = len(resp_tokens & ref_tokens) / max(1, len(ref_tokens))
        else:
            overlap = 0.5
        accuracy = _clip(2 + overlap * 8)
        completeness = _clip(2 + min(1.0, len(response) / 120.0) * 8)
        relevance = _clip(3 + overlap * 6 + (0.5 if reference else 0))
        fmt = _clip(4 + (4 if len(response) > 20 else 0)
                    + (2 if ("\n" in response or "：" in response) else 0))
        out = {
            "accuracy": accuracy,
            "completeness": completeness,
            "relevance": relevance,
            "format": fmt,
        }
        return {d: out.get(d, 5.0) for d in dims}


def _tokens(text):
    return [w for w in re.split(r"[\s,，。.；;、：:！!？?]+", text) if len(w) >= 2]


def _clip(x):
    return round(max(0.0, min(10.0, x)), 2)


class LLMJudge(BaseJudge):
    """使用 LLM 作为裁判，需要传入一个模型客户端。"""

    SYSTEM = ("你是一名严格的大模型评测裁判。根据评分量表的各个维度，"
              "对【回答】进行 0-10 分打分，仅输出 JSON，"
              "格式：{\"accuracy\": 8, \"completeness\": 7, ...}。")

    def __init__(self, client, rubric=None):
        self.client = client
        self.rubric = rubric or load_rubric()

    def score(self, prompt, response, reference, rubric=None):
        rubric = rubric or self.rubric
        dims = list(rubric.keys())
        rubric_text = "\n".join(
            f"- {k}（{rubric[k].get('label', k)}/{rubric[k].get('en', k)}，"
            f"0-10）：{rubric[k].get('description', '')}" for k in dims)
        user = (f"【问题】\n{prompt}\n\n"
                f"【参考答案】\n{reference or '（无）'}\n\n"
                f"【待评回答】\n{response}\n\n"
                f"【评分量表】\n{rubric_text}\n\n请仅输出 JSON 分数。")
        raw = self.client.complete(self.SYSTEM + "\n" + user)
        return self._parse(raw, dims)

    @staticmethod
    def _parse(raw, dims):
        try:
            m = re.search(r"\{.*\}", raw, re.DOTALL)
            data = json.loads(m.group(0)) if m else {}
        except Exception:
            data = {}
        out = {}
        for d in dims:
            v = data.get(d)
            try:
                out[d] = round(max(0.0, min(10.0, float(v))), 2)
            except (TypeError, ValueError):
                out[d] = 0.0
        return out
