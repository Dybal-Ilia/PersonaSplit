# syntax=docker/dockerfile:1
FROM python:3.12-slim AS base

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_ROOT_USER_ACTION=ignore \
    PIP_BREAK_SYSTEM_PACKAGES=1

RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY pyproject.toml README.md /app/
COPY src /app/src

RUN pip install --upgrade pip && \
    pip install \
      aiogram>=3.22.0 \
      asyncio>=4.0.0 \
      groq>=0.33.0 \
      langchain>=1.0.2 \
      langchain-community>=0.4 \
      langchain-groq>=1.0.0 \
      langchain-ollama>=1.0.0 \
      langgraph>=1.0.1 \
      neo4j>=5.23.0 \
      ollama>=0.6.0 \
      pydantic>=2.11.10 \
      python-dotenv>=1.1.1 \
      pyyaml>=6.0.3 \
      sentence-transformers>=5.1.2

ENV PROMPTS_PATH=/app/src/core/prompts/prompts.yaml

CMD ["python", "-m", "src.app.main"]
