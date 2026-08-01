# syntax=docker/dockerfile:1

# TWIB backend development image.
#
# Python 3.12 with uv. Runs the FastAPI application through uvicorn with
# hot reload (--reload) as a non-root user and exposes port 8000. This
# image is intentionally not optimized; the production image is a separate
# phase.

FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy

# Install the uv package manager.
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

WORKDIR /app

# Install runtime and development dependencies. The lockfile is copied so
# resolution stays close to the project; `uv sync` refreshes it in place
# when the manifest changed since the last lock.
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
