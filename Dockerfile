# syntax=docker/dockerfile:1

# TWIB backend multi-stage image.
#
# Two build chains share the Python 3.12 slim base:
#
#   - `runtime`    : minimal production image. Installs only the locked
#                    runtime dependencies with uv, copies the compiled
#                    virtual environment and the application source, runs
#                    uvicorn (no hot reload) as a non-root user, and
#                    registers a health check against /api/v1/health. The
#                    production Compose stack builds with `target: runtime`.
#   - `development`: default stage (last stage). Reproduces the development
#                    image: all dependency groups, hot reload via
#                    `uv run uvicorn --reload`, and a non-root user.

# Stage 1 -- builder: install the locked runtime dependencies with uv.
FROM python:3.12-slim AS builder

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy

# Install the uv package manager.
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

WORKDIR /app

# Install only the runtime dependencies from the lockfile. Copying the
# manifest first keeps this layer cached until the dependencies change.
COPY backend/pyproject.toml backend/uv.lock backend/README.md ./
RUN uv sync --frozen --no-dev

# Stage 2 -- runtime: minimal production image.
FROM python:3.12-slim AS runtime

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PATH="/app/.venv/bin:$PATH"

WORKDIR /app

# Run as a non-root user.
RUN groupadd --gid 1000 twib \
    && useradd --uid 1000 --gid twib --create-home twib

# Copy only the compiled virtual environment and the application source.
COPY --from=builder --chown=twib:twib /app/.venv /app/.venv
COPY --from=builder --chown=twib:twib /app/app ./app

USER twib

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=5s --start-period=20s --retries=3 \
    CMD ["python", "-c", "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/api/v1/health')"]

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]

# Stage 3 -- development (default stage).
FROM python:3.12-slim AS development

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy

# Install the uv package manager.
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

WORKDIR /app

# Install runtime and development dependencies.
COPY backend/pyproject.toml backend/uv.lock backend/README.md ./
RUN uv sync --all-groups

# Copy the application source into the image. At runtime this directory is
# bind-mounted from the host so uvicorn's reloader picks up changes.
COPY backend/app ./app

# Run as a non-root user. uid 1000 matches the typical host developer user,
# which keeps bind-mounted source files readable inside the container.
RUN useradd --uid 1000 --create-home twib \
    && chown -R twib:twib /app

USER twib

EXPOSE 8000

CMD ["uv", "run", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
