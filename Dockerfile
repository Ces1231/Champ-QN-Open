# CHAMP-QN Crypto Readiness Scanner — reference container image.
FROM python:3.14-slim AS base

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

# Minimal OS deps: curl only, used by the container HEALTHCHECK.
RUN apt-get update \
    && apt-get install -y --no-install-recommends curl \
    && rm -rf /var/lib/apt/lists/*

COPY pyproject.toml ./
COPY app ./app
COPY examples ./examples

RUN pip install --no-cache-dir .

RUN useradd --create-home --shell /usr/sbin/nologin --uid 10001 champqn \
    && chown -R champqn:champqn /app
USER champqn

EXPOSE 8000

HEALTHCHECK --interval=15s --timeout=5s --start-period=10s --retries=3 \
    CMD curl -fsS "http://127.0.0.1:${CHAMPQN_PORT:-8000}/health" || exit 1

CMD ["sh", "-c", "uvicorn app.main:app --host ${CHAMPQN_HOST:-0.0.0.0} --port ${CHAMPQN_PORT:-8000}"]
