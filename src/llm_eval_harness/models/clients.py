"""模型 API 客户端。

离线演示（MockClient）仅依赖标准库，无需联网、无需第三方包。
真实 API 客户端（OpenAICompatibleClient）按需惰性导入 `requests`，
因此离线演示永远不会触发该依赖。
"""
from __future__ import annotations

import os
import re
from abc import ABC, abstractmethod


class BaseModelClient(ABC):
    name: str = "base"

    @abstractmethod
    def complete(self, prompt: str, **kwargs) -> str:
        ...

    def chat(self, messages, **kwargs) -> str:
        return self.complete("\n".join(m.get("content", "") for m in messages), **kwargs)


class MockClient(BaseModelClient):
    """确定性离线客户端，供演示与 CI 使用，无需网络。

    profile:
      - "strong": 返回覆盖要点的连贯回答（演示用，会引用参考答案关键词）。
      - "weak":   返回简短、含糊、部分跑题的回答。
      - "random": 按文本稳定哈希在 strong/weak 间切换（可复现）。
    """

    def __init__(self, name: str = "mock", profile: str = "strong",
                 reference_lookup: dict | None = None):
        self.name = name
        self.profile = profile
        self._ref = reference_lookup or {}

    def complete(self, prompt: str, item_id: str | None = None,
                 reference: str | None = None, **kwargs) -> str:
        ref = reference or self._ref.get(item_id or "", "")
        if self.profile == "strong" or (self.profile == "random" and _hash_bit(prompt)):
            return _strong_answer(prompt, ref)
        return _weak_answer(prompt, ref)


def _hash_bit(text: str) -> bool:
    return (sum(ord(c) for c in text) % 2) == 0


def _strong_answer(prompt: str, ref: str) -> str:
    if ref:
        keywords = [w for w in re.split(r"[\s,，。.；;、：:]+", ref) if len(w) >= 2][:6]
        body = "；".join(keywords)
        return f"针对您的问题，我的回答如下：{body}。综上，该问题可从上述要点理解。"
    return f"这是一个高质量的回答示例：{prompt[:30]}……（此处给出覆盖要点的完整解答）。"


def _weak_answer(prompt: str, ref: str) -> str:
    return "这个我不太确定，可能大概也许是这样吧，感觉应该没什么问题。"


class OpenAICompatibleClient(BaseModelClient):
    """最小化的 OpenAI 兼容对话客户端（OpenAI / 文心 / 通义 / 本地 vLLM 等）。"""

    def __init__(self, name: str, api_key: str, base_url: str, model: str,
                 temperature: float = 0.0, timeout: int = 60):
        self.name = name
        self.api_key = api_key
        self.base_url = base_url.rstrip("/")
        self.model = model
        self.temperature = temperature
        self.timeout = timeout

    def chat(self, messages, **kwargs) -> str:
        import requests  # 惰性导入：离线演示不会触达此处
        resp = requests.post(
            f"{self.base_url}/chat/completions",
            headers={"Authorization": f"Bearer {self.api_key}",
                     "Content-Type": "application/json"},
            json={"model": self.model, "messages": messages,
                  "temperature": self.temperature},
            timeout=self.timeout,
        )
        resp.raise_for_status()
        return resp.json()["choices"][0]["message"]["content"]

    def complete(self, prompt: str, **kwargs) -> str:
        return self.chat([{"role": "user", "content": prompt}], **kwargs)


def build_client(spec: dict) -> BaseModelClient:
    """工厂函数。spec 字段：type, name, profile, api_key, base_url, model, temperature。"""
    t = spec.get("type", "mock")
    if t == "mock":
        return MockClient(name=spec.get("name", "mock"),
                          profile=spec.get("profile", "strong"))
    if t in ("openai", "openai-compatible"):
        return OpenAICompatibleClient(
            name=spec.get("name", spec.get("model", "openai")),
            api_key=spec.get("api_key") or os.environ.get("OPENAI_API_KEY", ""),
            base_url=spec.get("base_url", "https://api.openai.com/v1"),
            model=spec.get("model", "gpt-4o-mini"),
            temperature=spec.get("temperature", 0.0),
        )
    raise ValueError(f"未知客户端类型 unknown client type: {t}")
