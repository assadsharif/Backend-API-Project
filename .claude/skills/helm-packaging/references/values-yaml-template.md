# values.yaml Template Reference

Complete values.yaml template for multi-component applications.

---

## Full values.yaml Template

```yaml
# Default values for {{ .ApplicationName }}
# This is a YAML-formatted file.
# Declare variables to be passed into your templates.

# -- Global settings
global:
  # -- Image pull secrets for all containers
  imagePullSecrets: []
  # -- Storage class override
  storageClass: ""

# -- Component: Backend API
backend:
  # -- Enable/disable backend component
  enabled: true

  # -- Number of replicas
  replicaCount: 1

  # -- Image configuration
  image:
    repository: myapp/backend
    tag: ""  # Defaults to Chart.appVersion
    pullPolicy: IfNotPresent

  # -- Service configuration
  service:
    type: ClusterIP
    port: 8000
    targetPort: 8000

  # -- Resource requests and limits
  resources:
    requests:
      cpu: 100m
      memory: 128Mi
    limits:
      cpu: 500m
      memory: 512Mi

  # -- Environment variables
  env: []
  # -- Environment variables from ConfigMap/Secret
  envFrom: []

  # -- Liveness probe configuration
  livenessProbe:
    httpGet:
      path: /health
      port: http
    initialDelaySeconds: 30
    periodSeconds: 10

  # -- Readiness probe configuration
  readinessProbe:
    httpGet:
      path: /health
      port: http
    initialDelaySeconds: 5
    periodSeconds: 5

  # -- Pod annotations
  podAnnotations: {}

  # -- Pod security context
  podSecurityContext:
    fsGroup: 1000

  # -- Container security context
  securityContext:
    runAsNonRoot: true
    runAsUser: 1000

  # -- Node selector
  nodeSelector: {}

  # -- Tolerations
  tolerations: []

  # -- Affinity rules
  affinity: {}

# -- Component: Frontend
frontend:
  enabled: true
  replicaCount: 1

  image:
    repository: myapp/frontend
    tag: ""
    pullPolicy: IfNotPresent

  service:
    type: ClusterIP
    port: 3000
    targetPort: 3000

  resources:
    requests:
      cpu: 50m
      memory: 64Mi
    limits:
      cpu: 200m
      memory: 256Mi

  env: []
  envFrom: []

# -- Ingress configuration
ingress:
  # -- Enable ingress
  enabled: false
  # -- Ingress class name
  className: nginx
  # -- Ingress annotations
  annotations: {}
  # -- Ingress hosts
  hosts:
    - host: myapp.local
      paths:
        - path: /api
          pathType: Prefix
          service: backend
        - path: /
          pathType: Prefix
          service: frontend
  # -- TLS configuration
  tls: []

# -- Persistence configuration
persistence:
  # -- Enable persistence
  enabled: false
  # -- Storage class (empty uses default)
  storageClass: ""
  # -- Access mode
  accessMode: ReadWriteOnce
  # -- Size
  size: 1Gi

# -- ConfigMap data
configMap:
  # -- Enable ConfigMap creation
  enabled: false
  # -- ConfigMap data
  data: {}

# -- External secrets reference
externalSecrets:
  # -- Enable external secrets
  enabled: false
  # -- Secret store reference
  secretStoreRef: {}

# -- Service account configuration
serviceAccount:
  # -- Create service account
  create: true
  # -- Annotations
  annotations: {}
  # -- Name (auto-generated if empty)
  name: ""

# -- HorizontalPodAutoscaler configuration
autoscaling:
  # -- Enable HPA
  enabled: false
  # -- Minimum replicas
  minReplicas: 1
  # -- Maximum replicas
  maxReplicas: 10
  # -- Target CPU utilization
  targetCPUUtilizationPercentage: 80
  # -- Target memory utilization
  targetMemoryUtilizationPercentage: 80
```

---

## Values Structure Patterns

### Component-Based Organization

```yaml
# Global (applies to all)
global:
  imagePullSecrets: []
  storageClass: ""

# Per-component
backend:
  enabled: true
  # ... component-specific config

frontend:
  enabled: true
  # ... component-specific config

worker:
  enabled: false
  # ... component-specific config

# Shared resources
ingress:
  enabled: false

persistence:
  enabled: false
```

### Toggleable Components

```yaml
backend:
  enabled: true  # Can disable entire component

frontend:
  enabled: true

# Optional components default to disabled
worker:
  enabled: false

scheduler:
  enabled: false
```

---

## Common Value Sections

### Image Configuration

```yaml
image:
  repository: myapp/backend
  tag: ""              # Empty = use Chart.appVersion
  pullPolicy: IfNotPresent
  digest: ""           # Optional: override tag with digest
```

### Service Configuration

```yaml
service:
  type: ClusterIP      # ClusterIP, NodePort, LoadBalancer
  port: 8000           # Service port
  targetPort: 8000     # Container port
  nodePort: ""         # Only for NodePort type
  annotations: {}
```

### Resources

```yaml
resources:
  requests:
    cpu: 100m
    memory: 128Mi
  limits:
    cpu: 500m
    memory: 512Mi
```

### Probes

```yaml
livenessProbe:
  httpGet:
    path: /health
    port: http
  initialDelaySeconds: 30
  periodSeconds: 10
  timeoutSeconds: 5
  failureThreshold: 3

readinessProbe:
  httpGet:
    path: /ready
    port: http
  initialDelaySeconds: 5
  periodSeconds: 5
  timeoutSeconds: 3
  failureThreshold: 3

startupProbe:
  httpGet:
    path: /health
    port: http
  failureThreshold: 30
  periodSeconds: 10
```

### Security Context

```yaml
# Pod-level
podSecurityContext:
  runAsNonRoot: true
  runAsUser: 1000
  runAsGroup: 1000
  fsGroup: 1000

# Container-level
securityContext:
  runAsNonRoot: true
  runAsUser: 1000
  readOnlyRootFilesystem: true
  allowPrivilegeEscalation: false
  capabilities:
    drop:
      - ALL
```

### Environment Variables

```yaml
# Direct values
env:
  - name: LOG_LEVEL
    value: info
  - name: PORT
    value: "8000"

# From ConfigMap/Secret
envFrom:
  - configMapRef:
      name: myapp-config
  - secretRef:
      name: myapp-secrets
```

---

## Ingress Configuration

### Basic Ingress

```yaml
ingress:
  enabled: true
  className: nginx
  annotations: {}
  hosts:
    - host: myapp.local
      paths:
        - path: /
          pathType: Prefix
  tls: []
```

### Multi-Service Routing

```yaml
ingress:
  enabled: true
  className: nginx
  hosts:
    - host: myapp.local
      paths:
        - path: /api
          pathType: Prefix
          service: backend
        - path: /
          pathType: Prefix
          service: frontend
```

### With TLS

```yaml
ingress:
  enabled: true
  className: nginx
  annotations:
    cert-manager.io/cluster-issuer: letsencrypt-prod
  hosts:
    - host: myapp.example.com
      paths:
        - path: /
          pathType: Prefix
  tls:
    - secretName: myapp-tls
      hosts:
        - myapp.example.com
```

---

## Autoscaling Configuration

```yaml
autoscaling:
  enabled: false
  minReplicas: 1
  maxReplicas: 10
  targetCPUUtilizationPercentage: 80
  targetMemoryUtilizationPercentage: 80
  behavior:
    scaleDown:
      stabilizationWindowSeconds: 300
      policies:
        - type: Percent
          value: 10
          periodSeconds: 60
    scaleUp:
      stabilizationWindowSeconds: 0
      policies:
        - type: Percent
          value: 100
          periodSeconds: 15
```

---

## Persistence Configuration

### Single Volume

```yaml
persistence:
  enabled: true
  storageClass: ""    # Empty = default class
  accessMode: ReadWriteOnce
  size: 10Gi
  mountPath: /data
```

### Multiple Volumes

```yaml
persistence:
  volumes:
    data:
      enabled: true
      size: 10Gi
      mountPath: /app/data
    cache:
      enabled: true
      size: 5Gi
      mountPath: /app/cache
```

---

## Best Practices

1. **Document every value** with `# --` comments
2. **Use sensible defaults** that work for development
3. **Group related values** under component names
4. **Make components toggleable** with `enabled: true/false`
5. **Never hardcode secrets** - use references only
6. **Use empty strings** for optional values (not `null`)
7. **Provide resource defaults** appropriate for Minikube
