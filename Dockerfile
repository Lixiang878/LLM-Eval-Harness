# syntax=docker/dockerfile:1
FROM python:3.11-slim

LABEL org.opencontainers.image.source="https://github.com/Lixiang878/llm-eval-harness"
LABEL org.opencontainers.image.description="Multi-model LLM evaluation harness with LLM-as-Judge and bad-case attribution"

WORKDIR /app

COPY . /app

# Offline core install: pure stdlib. Model providers / judge models are
# OPTIONAL and lazy-imported; a deterministic mock provider runs with no network.
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -e . \
    && pip install --no-cache-dir pytest

CMD ["pytest", "-q"]

# Run an offline evaluation (defaults to the built-in mock model, no API key):
#   docker build -t llm-eval-harness .
#   docker run --rm llm-eval-harness python -m llm_eval_harness.cli run
