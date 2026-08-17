# ---------- Builder ----------
FROM python:3.13.14-slim AS builder

ARG POETRY_VERSION=2.4.1
ARG POETRY_EXPORT_PLUGIN_VERSION=1.10.0

ENV PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_NO_CACHE_DIR=1 \
    POETRY_NO_INTERACTION=1

WORKDIR /build

RUN apt-get update \
    && apt-get install -y --no-install-recommends gcc libpq-dev \
    && rm -rf /var/lib/apt/lists/*

RUN pip install \
    "poetry==${POETRY_VERSION}" \
    "poetry-plugin-export==${POETRY_EXPORT_PLUGIN_VERSION}"

COPY pyproject.toml poetry.lock ./

RUN poetry export \
    --format requirements.txt \
    --output requirements.txt \
    --without-hashes \
    && pip wheel \
        --wheel-dir /wheels \
        --requirement requirements.txt \
        --no-deps


# ---------- Runtime ----------
FROM python:3.13.14-slim AS runtime

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /src

RUN apt-get update \
    && apt-get install -y --no-install-recommends libpq5 \
    && rm -rf /var/lib/apt/lists/* \
    && useradd --create-home --uid 10001 appuser \
    && mkdir -p /src/logs \
    && chown -R appuser:appuser /src

COPY --from=builder /wheels /wheels

RUN pip install --no-index --no-deps /wheels/* \
    && rm -rf /wheels

COPY --chown=appuser:appuser ./src ./
COPY --chown=appuser:appuser alembic.ini /alembic.ini

USER appuser

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
