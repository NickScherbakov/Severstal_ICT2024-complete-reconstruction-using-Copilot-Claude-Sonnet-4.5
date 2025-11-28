# TITAN Analytics Platform - Kubernetes Deployment

This directory contains Kubernetes manifests for deploying TITAN Analytics Platform in a production environment.

## Prerequisites

- Kubernetes 1.24+
- kubectl configured
- Helm 3.0+ (for Helm deployment)
- Ingress Controller (nginx-ingress recommended)
- PostgreSQL operator or external database

## Quick Start

### Using kubectl

```bash
# Create namespace
kubectl create namespace titan

# Apply secrets (edit first!)
kubectl apply -f secrets.yaml -n titan

# Deploy all components
kubectl apply -f . -n titan
```

### Using Helm

```bash
cd helm/titan-analytics
helm install titan . -n titan --create-namespace
```

## Components

| Component | Description | Replicas |
|-----------|-------------|----------|
| backend | Django API server | 2+ |
| frontend | React SPA (Nginx) | 2+ |
| celery-worker | Async task processor | 2+ |
| celery-beat | Scheduled tasks | 1 |
| rabbitmq | Message broker | 1 |
| postgresql | Database | 1 (external recommended) |

## Configuration

Edit `configmap.yaml` and `secrets.yaml` before deployment:

```yaml
# configmap.yaml
DJANGO_DEBUG: "false"
ALLOWED_HOSTS: "your-domain.com"

# secrets.yaml (base64 encoded)
DATABASE_URL: <base64>
YANDEX_API_KEY: <base64>
SECRET_KEY: <base64>
```

## Scaling

```bash
# Scale backend
kubectl scale deployment titan-backend --replicas=4 -n titan

# Scale workers
kubectl scale deployment titan-celery-worker --replicas=6 -n titan
```

## Monitoring

Health endpoints:
- `/health/` - Backend health check
- `/ready/` - Backend readiness check

## Troubleshooting

```bash
# Check pod status
kubectl get pods -n titan

# View logs
kubectl logs -f deployment/titan-backend -n titan

# Describe service
kubectl describe svc titan-backend -n titan
```
