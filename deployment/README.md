# Deployment

## Purpose

Kubernetes manifests, Helm charts, and deployment automation for staging and production environments.

## Responsibilities

- Kubernetes manifests (Deployments, Services, Ingress)
- Helm charts for each service
- Environment configurations (values files)
- CI/CD integration
- Rollback procedures
- Blue/green deployment
- Canary releases

## What Belongs Here

- `k8s/` - Raw manifests
- `helm/` - Helm charts
- `scripts/` - Deployment scripts
- Environment values files
- ArgoCD/Flux configurations

## What Must NEVER Belong Here

- Application code
- Dockerfiles (use docker/)
- Local development configs

## Dependencies

- Kubernetes 1.28+
- Helm 3+
- Cloud provider CLI (aws, gcloud, az)

## Future Phases

- Phase 13: Deployment manifests