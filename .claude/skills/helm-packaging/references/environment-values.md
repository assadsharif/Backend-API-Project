# Environment-Specific Values Reference

Override files for different deployment environments.

---

## values-dev.yaml (Development/Minikube)

```yaml
# Development environment overrides
# Usage: helm install myapp ./myapp -f values-dev.yaml

global:
  environment: dev
  development: true

backend:
  replicaCount: 1
  resources:
    requests:
      cpu: 50m
      memory: 64Mi
    limits:
      cpu: 200m
      memory: 256Mi
  env:
    - name: LOG_LEVEL
      value: debug
    - name: DEBUG
      value: "true"

frontend:
  replicaCount: 1
  resources:
    requests:
      cpu: 25m
      memory: 32Mi
    limits:
      cpu: 100m
      memory: 128Mi

ingress:
  enabled: true
  hosts:
    - host: myapp.local
      paths:
        - path: /api
          pathType: Prefix
          service: backend
        - path: /
          pathType: Prefix
          service: frontend

persistence:
  enabled: true
  size: 1Gi
```

---

## values-staging.yaml (Staging)

```yaml
# Staging environment overrides
# Usage: helm install myapp ./myapp -f values-staging.yaml

global:
  environment: staging
  development: false

backend:
  replicaCount: 2
  resources:
    requests:
      cpu: 250m
      memory: 256Mi
    limits:
      cpu: 500m
      memory: 512Mi
  env:
    - name: LOG_LEVEL
      value: info

frontend:
  replicaCount: 2
  resources:
    requests:
      cpu: 100m
      memory: 128Mi
    limits:
      cpu: 250m
      memory: 256Mi

ingress:
  enabled: true
  className: nginx
  hosts:
    - host: staging.myapp.example.com
      paths:
        - path: /api
          pathType: Prefix
          service: backend
        - path: /
          pathType: Prefix
          service: frontend

autoscaling:
  enabled: true
  minReplicas: 2
  maxReplicas: 5
  targetCPUUtilizationPercentage: 75

persistence:
  enabled: true
  size: 10Gi
```

---

## values-prod.yaml (Production)

```yaml
# Production environment overrides
# Usage: helm install myapp ./myapp -f values-prod.yaml

global:
  environment: prod
  development: false

backend:
  replicaCount: 3
  resources:
    requests:
      cpu: 500m
      memory: 512Mi
    limits:
      cpu: 1000m
      memory: 1Gi
  env:
    - name: LOG_LEVEL
      value: info

frontend:
  replicaCount: 2
  resources:
    requests:
      cpu: 100m
      memory: 128Mi
    limits:
      cpu: 500m
      memory: 512Mi

ingress:
  enabled: true
  className: nginx
  annotations:
    cert-manager.io/cluster-issuer: letsencrypt-prod
  hosts:
    - host: myapp.example.com
      paths:
        - path: /api
          pathType: Prefix
          service: backend
        - path: /
          pathType: Prefix
          service: frontend
  tls:
    - secretName: myapp-tls
      hosts:
        - myapp.example.com

autoscaling:
  enabled: true
  minReplicas: 2
  maxReplicas: 10
  targetCPUUtilizationPercentage: 70

persistence:
  enabled: true
  storageClass: fast-ssd
  size: 50Gi
```

---

## Resource Sizing Guidelines

| Environment | CPU Request | CPU Limit | Memory Request | Memory Limit |
|-------------|-------------|-----------|----------------|--------------|
| Development | 50m | 200m | 64Mi | 256Mi |
| Staging | 250m | 500m | 256Mi | 512Mi |
| Production | 500m | 1000m | 512Mi | 1Gi |

---

## Environment Comparison

| Setting | Dev | Staging | Prod |
|---------|-----|---------|------|
| Replicas | 1 | 2 | 3+ |
| HPA | Disabled | Enabled (2-5) | Enabled (2-10) |
| Ingress TLS | No | Optional | Required |
| Log Level | debug | info | info/warn |
| PVC Size | 1Gi | 10Gi | 50Gi |

---

## Usage Examples

### Development on Minikube

```bash
# Start Minikube
minikube start

# Enable ingress addon
minikube addons enable ingress

# Install with dev values
helm install myapp ./myapp -f values-dev.yaml

# Add to /etc/hosts
echo "$(minikube ip) myapp.local" | sudo tee -a /etc/hosts
```

### Staging Deployment

```bash
# Install with staging values
helm install myapp ./myapp -f values-staging.yaml --namespace staging

# Or upgrade existing
helm upgrade myapp ./myapp -f values-staging.yaml --namespace staging
```

### Production Deployment

```bash
# Install with production values
helm install myapp ./myapp -f values-prod.yaml --namespace production

# With additional overrides
helm install myapp ./myapp \
  -f values-prod.yaml \
  --set backend.replicaCount=5 \
  --namespace production
```

---

## Best Practices

1. **Base values.yaml**: Contains sensible defaults for development
2. **Environment files**: Override only what differs from defaults
3. **Never commit secrets**: Use external secrets management
4. **Use namespaces**: Isolate environments in separate namespaces
5. **Version control**: Keep all values files in git
6. **Document changes**: Comment why values differ per environment
