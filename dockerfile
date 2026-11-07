# Version parameters

ARG NODE_VERSION=24
ARG PYTHON_VERSION=3.14

# Stage 1 - Build Vite frontend

FROM node:${NODE_VERSION}-slim AS frontend-build

WORKDIR /app

# Copy manifests
COPY package.json package-lock.json ./
COPY frontend/package.json frontend/package-lock.json ./frontend/
RUN npm --prefix frontend install --frozen-lockfile

COPY frontend/ ./frontend/
COPY config/ ./config/
RUN npm --prefix frontend run build

# Stage 2 - Build Python environment

FROM python:${PYTHON_VERSION}-slim AS python-build

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

WORKDIR /app

# Install Python dependencies
COPY pyproject.toml uv.lock ./
RUN uv sync --no-dev --frozen

# Stage 3 - Lean runtime image
ARG PYTHON_VERSION=3.14
FROM python:${PYTHON_VERSION}-slim AS runtime

ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 PORT=5050

# Non-root user
RUN useradd --create-home appuser
WORKDIR /home/appuser/app
RUN mkdir -p instance && chown -R appuser:appuser /home/appuser/app
USER appuser

# Pull only the necessary things
COPY --from=python-build --chown=appuser /app/.venv .venv
COPY --from=frontend-build --chown=appuser /app/frontend/dist frontend/dist
COPY --chown=appuser backend/ backend/
COPY --chown=appuser config/ config/
COPY --chown=appuser schema.sql ./
COPY --chown=appuser frontend/app.py frontend/app.py

EXPOSE ${PORT}

HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 CMD .venv/bin/python -c "import urllib.request; urllib.request.urlopen('http://localhost:5050/api/config')"

CMD [".venv/bin/python", "-m", "frontend.app"]