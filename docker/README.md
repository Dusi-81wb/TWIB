# Docker

## Purpose

Docker configurations for containerizing all services. Multi-stage builds for production optimization.

## Responsibilities

- Backend Dockerfile
- Frontend Dockerfile
- Development Docker Compose
- Production Docker Compose
- Base image definitions
- Build arguments
- Health checks

## What Belongs Here

- `Dockerfile.backend`
- `Dockerfile.frontend`
- `docker-compose.yml` (dev)
- `docker-compose.prod.yml`
- `.dockerignore`
- Build scripts

## What Must NEVER Belong Here

- Application code
- Kubernetes manifests (use deployment/)
- CI/CD pipelines (use .github/)

## Dependencies

- Docker 24+
- Docker Compose 2+

## Future Phases

- Phase 13: Docker configuration