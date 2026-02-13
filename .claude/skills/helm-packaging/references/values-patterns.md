# values.yaml Patterns Reference

Best practices and patterns for structuring Helm chart values.

---

## Core Principles

### 1. values.yaml Is the Only Config Surface

All customization happens through values.yaml - never hardcode in templates.

```yaml
# GOOD: Everything configurable
backend:
  replicaCount: 1
  image:
    repository: myapp/backend
    tag: "1.0.0"

# BAD: Hardcoded in template
# replicas: 3  (never do this in templates)
```

### 2. Sensible Defaults

Values should work out-of-the-box for development.

```yaml
# Good defaults for local development
backend:
  replicaCount: 1
  resources:
    requests:
      cpu: 100m
      memory: 128Mi
    limits:
      cpu: 500m
      memory: 512Mi
```

### 3. Document Everything

Use comments to explain each value.

```yaml
# -- Number of backend replicas
# @default -- 1
replicaCount: 1

# -- Image pull policy
# @default -- IfNotPresent
# Options: Always, IfNotPresent, Never
pullPolicy: IfNotPresent
```

---

## Structure Patterns

### Flat vs Nested

```yaml
# PREFER: Nested for component grouping
backend:
  image:
    repository: myapp/backend
    tag: "1.0.0"
  service:
    port: 8000

# AVOID: Flat with prefixes (harder to override)
backendImageRepository: myapp/backend
backendImageTag: "1.0.0"
backendServicePort: 8000
```

### Component-Based Structure

```yaml
# Global settings (apply to all components)
global:
  imagePullSecrets: []
  storageClass: ""

# Per-component configuration
backend:
  enabled: true
  # ... backend-specific config

frontend:
  enabled: true
  # ... frontend-specific config

# Shared resources
ingress:
  enabled: false
  # ... ingress config

persistence:
  enabled: false
  # ... persistence config
```

---

## Common Value Patterns

### Image Configuration

```yaml
image:
  # -- Container image repository
  repository: myapp/backend
  # -- Image tag (defaults to Chart.appVersion)
  tag: ""
  # -- Image pull policy
  pullPolicy: IfNotPresent
  # -- Image digest (overrides tag if set)
  digest: ""
```

**Template usage:**
```yaml
image: "{{ .Values.backend.image.repository }}:{{ .Values.backend.image.tag | default .Chart.AppVersion }}"
{{- if .Values.backend.image.digest }}
image: "{{ .Values.backend.image.repository }}@{{ .Values.backend.image.digest }}"
{{- end }}
```

### Service Configuration

```yaml
service:
  # -- Service type
  type: ClusterIP
  # -- Service port
  port: 8000
  # -- Container target port
  targetPort: 8000
  # -- NodePort (only when type is NodePort)
  nodePort: ""
  # -- Service annotations
  annotations: {}
  # -- Extra ports
  extraPorts: []
```

### Resource Limits

```yaml
resources:
  # -- Resource requests
  requests:
    cpu: 100m
    memory: 128Mi
  # -- Resource limits
  limits:
    cpu: 500m
    memory: 512Mi
```

**Size presets pattern:**
```yaml
# In values.yaml
resourcePreset: small  # small, medium, large, custom

# In _helpers.tpl
{{- define "myapp.resources" -}}
{{- if eq .Values.resourcePreset "small" }}
requests:
  cpu: 100m
  memory: 128Mi
limits:
  cpu: 500m
  memory: 512Mi
{{- else if eq .Values.resourcePreset "medium" }}
requests:
  cpu: 500m
  memory: 512Mi
limits:
  cpu: 1000m
  memory: 1Gi
{{- else if eq .Values.resourcePreset "large" }}
requests:
  cpu: 1000m
  memory: 1Gi
limits:
  cpu: 2000m
  memory: 2Gi
{{- else }}
{{- toYaml .Values.resources }}
{{- end }}
{{- end }}
```

### Environment Variables

```yaml
# Direct env vars
env:
  - name: LOG_LEVEL
    value: info
  - name: DEBUG
    value: "false"

# From ConfigMap/Secret
envFrom:
  - configMapRef:
      name: myapp-config
  - secretRef:
      name: myapp-secrets

# Structured env (converted to list in template)
envVars:
  LOG_LEVEL: info
  DEBUG: "false"
  DATABASE_HOST: postgres
```

**Structured env template:**
```yaml
env:
  {{- range $key, $value := .Values.backend.envVars }}
  - name: {{ $key }}
    value: {{ $value | quote }}
  {{- end }}
  {{- with .Values.backend.env }}
  {{- toYaml . | nindent 12 }}
  {{- end }}
```

### Probes Configuration

```yaml
# Liveness probe
livenessProbe:
  enabled: true
  httpGet:
    path: /health
    port: http
  initialDelaySeconds: 30
  periodSeconds: 10
  timeoutSeconds: 5
  failureThreshold: 3
  successThreshold: 1

# Readiness probe
readinessProbe:
  enabled: true
  httpGet:
    path: /ready
    port: http
  initialDelaySeconds: 5
  periodSeconds: 5
  timeoutSeconds: 3
  failureThreshold: 3
  successThreshold: 1

# Startup probe (for slow-starting apps)
startupProbe:
  enabled: false
  httpGet:
    path: /health
    port: http
  initialDelaySeconds: 0
  periodSeconds: 10
  timeoutSeconds: 5
  failureThreshold: 30
```

**Template usage:**
```yaml
{{- if .Values.backend.livenessProbe.enabled }}
livenessProbe:
  {{- if .Values.backend.livenessProbe.httpGet }}
  httpGet:
    path: {{ .Values.backend.livenessProbe.httpGet.path }}
    port: {{ .Values.backend.livenessProbe.httpGet.port }}
  {{- else if .Values.backend.livenessProbe.tcpSocket }}
  tcpSocket:
    port: {{ .Values.backend.livenessProbe.tcpSocket.port }}
  {{- else if .Values.backend.livenessProbe.exec }}
  exec:
    command:
      {{- toYaml .Values.backend.livenessProbe.exec.command | nindent 14 }}
  {{- end }}
  initialDelaySeconds: {{ .Values.backend.livenessProbe.initialDelaySeconds }}
  periodSeconds: {{ .Values.backend.livenessProbe.periodSeconds }}
  timeoutSeconds: {{ .Values.backend.livenessProbe.timeoutSeconds }}
  failureThreshold: {{ .Values.backend.livenessProbe.failureThreshold }}
  successThreshold: {{ .Values.backend.livenessProbe.successThreshold }}
{{- end }}
```

---

## Security Context Patterns

### Pod Security Context

```yaml
podSecurityContext:
  # -- Run as non-root
  runAsNonRoot: true
  # -- Run as user ID
  runAsUser: 1000
  # -- Run as group ID
  runAsGroup: 1000
  # -- Filesystem group
  fsGroup: 1000
  # -- Filesystem group change policy
  fsGroupChangePolicy: OnRootMismatch
  # -- Supplemental groups
  supplementalGroups: []
  # -- Seccomp profile
  seccompProfile:
    type: RuntimeDefault
```

### Container Security Context

```yaml
securityContext:
  # -- Run as non-root
  runAsNonRoot: true
  # -- Run as user ID
  runAsUser: 1000
  # -- Read-only root filesystem
  readOnlyRootFilesystem: true
  # -- Disallow privilege escalation
  allowPrivilegeEscalation: false
  # -- Drop all capabilities
  capabilities:
    drop:
      - ALL
    add: []
```

---

## Ingress Patterns

### Basic Ingress

```yaml
ingress:
  enabled: false
  className: nginx
  annotations: {}
  hosts:
    - host: myapp.local
      paths:
        - path: /
          pathType: Prefix
  tls: []
```

### Multi-Service Ingress

```yaml
ingress:
  enabled: false
  className: nginx
  annotations:
    nginx.ingress.kubernetes.io/proxy-body-size: "50m"
  hosts:
    - host: myapp.local
      paths:
        - path: /api
          pathType: Prefix
          backend:
            service: backend
            port: 8000
        - path: /
          pathType: Prefix
          backend:
            service: frontend
            port: 3000
  tls:
    - secretName: myapp-tls
      hosts:
        - myapp.local
```

### Environment-Specific Annotations

```yaml
# values-dev.yaml
ingress:
  enabled: true
  annotations: {}

# values-prod.yaml
ingress:
  enabled: true
  annotations:
    cert-manager.io/cluster-issuer: letsencrypt-prod
    nginx.ingress.kubernetes.io/ssl-redirect: "true"
    nginx.ingress.kubernetes.io/proxy-body-size: "100m"
```

---

## Persistence Patterns

### Single Volume

```yaml
persistence:
  enabled: false
  storageClass: ""
  accessMode: ReadWriteOnce
  size: 10Gi
  annotations: {}
  # Existing claim (skip creating PVC)
  existingClaim: ""
  # Mount path in container
  mountPath: /data
  # Sub-path within volume
  subPath: ""
```

### Multiple Volumes

```yaml
persistence:
  data:
    enabled: true
    storageClass: ""
    accessMode: ReadWriteOnce
    size: 10Gi
    mountPath: /app/data
  cache:
    enabled: true
    storageClass: ""
    accessMode: ReadWriteOnce
    size: 5Gi
    mountPath: /app/cache
  logs:
    enabled: false
    storageClass: ""
    accessMode: ReadWriteOnce
    size: 2Gi
    mountPath: /app/logs
```

### StatefulSet Volumes

```yaml
# For StatefulSet volumeClaimTemplates
volumeClaimTemplates:
  - name: data
    accessMode: ReadWriteOnce
    size: 10Gi
    storageClass: ""
```

---

## Global Configuration

```yaml
global:
  # -- Image pull secrets for all containers
  imagePullSecrets: []
  #  - name: regcred

  # -- Default storage class
  storageClass: ""

  # -- Environment (dev, staging, prod)
  environment: dev

  # -- Development mode (affects defaults)
  development: true

  # -- Image registry override
  imageRegistry: ""

  # -- Common labels to add to all resources
  commonLabels: {}

  # -- Common annotations to add to all resources
  commonAnnotations: {}
```

**Template usage:**
```yaml
{{- with .Values.global.imagePullSecrets }}
imagePullSecrets:
  {{- toYaml . | nindent 8 }}
{{- end }}

metadata:
  labels:
    {{- include "myapp.labels" . | nindent 4 }}
    {{- with .Values.global.commonLabels }}
    {{- toYaml . | nindent 4 }}
    {{- end }}
```

---

## Environment Override Files

### values-dev.yaml

```yaml
# Development environment
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
        - path: /
          pathType: Prefix
```

### values-staging.yaml

```yaml
# Staging environment
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

ingress:
  enabled: true
  className: nginx
  hosts:
    - host: staging.myapp.example.com
      paths:
        - path: /
          pathType: Prefix
```

### values-prod.yaml

```yaml
# Production environment
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
      value: warn

frontend:
  replicaCount: 3

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
    - secretName: myapp-prod-tls
      hosts:
        - myapp.example.com

autoscaling:
  enabled: true
  minReplicas: 3
  maxReplicas: 10
  targetCPUUtilizationPercentage: 70

podDisruptionBudget:
  enabled: true
  minAvailable: 2
```

---

## Secret Management Patterns

### External Secrets Operator

```yaml
externalSecrets:
  enabled: true
  refreshInterval: "1h"
  secretStoreRef:
    name: aws-secrets-manager
    kind: ClusterSecretStore
  data:
    - secretKey: DATABASE_URL
      remoteRef:
        key: myapp/prod/database
        property: url
    - secretKey: API_KEY
      remoteRef:
        key: myapp/prod/api
        property: key
```

### Sealed Secrets

```yaml
sealedSecrets:
  enabled: true
  # Pre-encrypted values (encrypt with kubeseal)
  encryptedData:
    DATABASE_URL: "AgBy3i4OJSWK+PiTySYZZA..."
    API_KEY: "AgCtr1OJSWK+PiTy..."
```

### Vault Integration

```yaml
vault:
  enabled: true
  injector:
    enabled: true
  agent:
    annotations:
      vault.hashicorp.com/agent-inject: "true"
      vault.hashicorp.com/role: "myapp"
      vault.hashicorp.com/agent-inject-secret-config: "secret/data/myapp/config"
```

### Secret References (Never Store Values)

```yaml
# Reference existing secrets
existingSecrets:
  database:
    name: myapp-database-credentials
    key: DATABASE_URL
  api:
    name: myapp-api-credentials
    key: API_KEY
```

---

## Validation Patterns

### JSON Schema (values.schema.json)

```json
{
  "$schema": "https://json-schema.org/draft-07/schema#",
  "type": "object",
  "properties": {
    "backend": {
      "type": "object",
      "properties": {
        "enabled": { "type": "boolean" },
        "replicaCount": {
          "type": "integer",
          "minimum": 1,
          "maximum": 100
        },
        "image": {
          "type": "object",
          "required": ["repository"],
          "properties": {
            "repository": { "type": "string" },
            "tag": { "type": "string" },
            "pullPolicy": {
              "type": "string",
              "enum": ["Always", "IfNotPresent", "Never"]
            }
          }
        },
        "resources": {
          "type": "object",
          "properties": {
            "requests": { "$ref": "#/definitions/resourceQuantities" },
            "limits": { "$ref": "#/definitions/resourceQuantities" }
          }
        }
      }
    }
  },
  "definitions": {
    "resourceQuantities": {
      "type": "object",
      "properties": {
        "cpu": { "type": "string", "pattern": "^[0-9]+m?$" },
        "memory": { "type": "string", "pattern": "^[0-9]+(Mi|Gi)$" }
      }
    }
  }
}
```

### Required Value Template Check

```yaml
# In template, fail if required value missing
image: {{ required "backend.image.repository is required" .Values.backend.image.repository }}

# With helpful error message
{{- if not .Values.backend.image.repository }}
{{- fail "backend.image.repository is required. Set it in values.yaml or via --set" }}
{{- end }}
```

---

## Documentation Patterns

### Using helm-docs Format

```yaml
# -- @section Backend Configuration

# -- Enable backend component
# @default -- true
enabled: true

# -- Number of replicas
# @default -- 1
replicaCount: 1

# -- @section Image Configuration

# -- [Backend image configuration](https://example.com/docs/images)
image:
  # -- Container image repository
  repository: myapp/backend
  # -- Image tag (defaults to Chart.appVersion)
  tag: ""
  # -- Image pull policy
  # @default -- IfNotPresent
  pullPolicy: IfNotPresent
```

### README Generation

Run `helm-docs` to auto-generate README.md from values.yaml comments.

```bash
# Install helm-docs
go install github.com/norwoodj/helm-docs/cmd/helm-docs@latest

# Generate README
helm-docs --chart-search-root=./charts
```
