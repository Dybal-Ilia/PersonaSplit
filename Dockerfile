FROM python:3.12-slim

WORKDIR /app


RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*


COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/


COPY pyproject.toml uv.lock ./


RUN uv sync --frozen --no-install-project


COPY . .


RUN uv sync --frozen

CMD ["uv", "run", "python", "-m", "src.app.main"]