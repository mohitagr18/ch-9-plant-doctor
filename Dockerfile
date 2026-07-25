# Dockerfile

FROM python:3.11-slim
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

WORKDIR /app

RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-cache

COPY . .

ENV PATH="/app/.venv/bin:$PATH"

EXPOSE 8080

HEALTHCHECK CMD curl --fail http://localhost:8080/_stcore/health

CMD streamlit run app.py \
    --server.port=8080 \
    --server.address=0.0.0.0 \
    --server.headless=true \
    --browser.serverAddress="0.0.0.0" \
    --browser.gatherUsageStats=false
