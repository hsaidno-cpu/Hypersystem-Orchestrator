FROM python:3.13-slim AS runtime

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    HSO_CATALOG_DIR=/app/catalog

WORKDIR /app
COPY services/hso-platform/pyproject.toml ./pyproject.toml
COPY services/hso-platform/src ./src
COPY services/hso-platform/migrations ./migrations
COPY services/hso-platform/alembic.ini ./alembic.ini
COPY catalog ./catalog

RUN pip install --upgrade pip && pip install .
RUN useradd --create-home --uid 10001 hso

USER 10001:10001
EXPOSE 8000
CMD ["uvicorn", "hso_platform.app:app", "--host", "0.0.0.0", "--port", "8000", "--proxy-headers"]
