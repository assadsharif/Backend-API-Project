# Kubernetes Optimization Patterns Reference

Best practices and patterns for resource optimization in Kubernetes.

---

## Optimization Levels

### Conservative (Recommended for Learning)

```
Goal: Minimize risk while improving efficiency
Approach: Small changes, generous buffers

Resource Sizing:
- Requests: p95 usage + 30% buffer
- Limits: 2x requests
- Change increment: 10-20% at a time

Scaling:
- Keep min replicas at current level
- Increase max replicas only
- Use conservative HPA thresholds (80%)
```

### Moderate

```
Goal: Balance efficiency and stability
Approach: Moderate changes, reasonable buffers

Resource Sizing:
- Requests: p90 usage + 20% buffer
- Limits: 1.5x requests
- Change increment: 20-30% at a time

Scaling:
- Allow replica reduction by 1
- Moderate HPA thresholds (70%)
```

### Aggressive (Not for Production)

```
Goal: Maximum efficiency
Approach: Tight sizing, minimal buffers

Resource Sizing:
- Requests: p75 usage + 10% buffer
- Limits: 1.2x requests
- Change increment: 30-50%

Scaling:
- Minimize replicas
- Aggressive HPA thresholds (60%)

WARNING: High risk of instability
```

---

## Resource Right-Sizing

### CPU Optimization

**Analysis:**
```yaml
Current State:
  requests.cpu: 500m
  limits.cpu: 1000m

Observed Usage (7 days):
  p50: 80m
  p75: 120m
  p90: 180m
  p95: 220m
  max: 450m
```

**Conservative Recommendation:**
```yaml
Recommended:
  requests.cpu: 300m   # p95 (220m) + 30% buffer
  limits.cpu: 600m     # 2x requests

Rationale:
- p95 covers 95% of usage patterns
- 30% buffer for unexpected spikes
- Limits allow burst to 2x normal

Helm Implementation:
  helm upgrade myapp ./myapp \
    --set backend.resources.requests.cpu=300m \
    --set backend.resources.limits.cpu=600m
```

**CPU Throttling Prevention:**
```yaml
Signs of Throttling:
- High CPU throttling in metrics
- Latency spikes correlating with load
- container_cpu_cfs_throttled_periods_total increasing

Solutions:
1. Increase CPU limits (allow burst)
2. Increase CPU requests (guarantee more)
3. Optimize application code
4. Scale horizontally (more replicas)
```

### Memory Optimization

**Analysis:**
```yaml
Current State:
  requests.memory: 1Gi
  limits.memory: 2Gi

Observed Usage (7 days):
  p50: 280Mi
  p75: 350Mi
  p90: 420Mi
  p95: 480Mi
  max: 780Mi (during GC)
```

**Conservative Recommendation:**
```yaml
Recommended:
  requests.memory: 600Mi  # p95 (480Mi) + 25% buffer
  limits.memory: 1Gi      # Max observed + headroom

Rationale:
- Memory spikes during GC need headroom
- OOMKill is disruptive, be generous
- Limits should accommodate peak + GC overhead

Helm Implementation:
  helm upgrade myapp ./myapp \
    --set backend.resources.requests.memory=600Mi \
    --set backend.resources.limits.memory=1Gi
```

**OOM Prevention:**
```yaml
Signs of Memory Pressure:
- OOMKilled events
- High memory usage percentage
- container_memory_working_set_bytes near limit

Solutions:
1. Increase memory limits
2. Investigate memory leaks
3. Tune GC settings (Java, Go, etc.)
4. Add memory-based HPA
```

---

## Replica Optimization

### Single vs Multiple Replicas

**Development Environment:**
```yaml
Recommendation: Single Replica

Rationale:
- Minikube has limited resources
- No HA requirement for development
- Faster deployments
- Simpler debugging

Configuration:
  backend:
    replicaCount: 1
  frontend:
    replicaCount: 1
```

**When to Use Multiple Replicas:**
```yaml
Use Multiple Replicas When:
- Testing load balancing behavior
- Validating rolling update strategy
- Learning HPA behavior
- Simulating production-like setup

Configuration for Learning:
  backend:
    replicaCount: 2
    autoscaling:
      enabled: true
      minReplicas: 1
      maxReplicas: 3
```

### HPA Configuration

**Conservative HPA:**
```yaml
autoscaling:
  enabled: true
  minReplicas: 1
  maxReplicas: 5
  targetCPUUtilizationPercentage: 80
  behavior:
    scaleDown:
      stabilizationWindowSeconds: 300  # 5 min cooldown
      policies:
        - type: Percent
          value: 10                     # Scale down 10% at a time
          periodSeconds: 60
    scaleUp:
      stabilizationWindowSeconds: 60
      policies:
        - type: Percent
          value: 50                     # Scale up 50% at a time
          periodSeconds: 60
```

**Educational HPA (for learning):**
```yaml
autoscaling:
  enabled: true
  minReplicas: 1
  maxReplicas: 3
  targetCPUUtilizationPercentage: 50  # Triggers easily
  behavior:
    scaleDown:
      stabilizationWindowSeconds: 60   # Quick feedback
    scaleUp:
      stabilizationWindowSeconds: 0    # Immediate scale up
```

---

## Configuration Optimization

### Probe Optimization

**Startup Probe (Slow-Starting Apps):**
```yaml
# Problem: Liveness kills pods before ready
startupProbe:
  httpGet:
    path: /health
    port: 8080
  initialDelaySeconds: 0
  periodSeconds: 10
  failureThreshold: 30  # 5 minutes to start

# Then liveness/readiness take over
livenessProbe:
  httpGet:
    path: /health
    port: 8080
  periodSeconds: 10
  failureThreshold: 3
```

**Readiness Probe Optimization:**
```yaml
# Fast failure detection
readinessProbe:
  httpGet:
    path: /ready
    port: 8080
  initialDelaySeconds: 5
  periodSeconds: 5      # Check frequently
  failureThreshold: 2   # Fail fast
  successThreshold: 1

# For gradual warmup
readinessProbe:
  httpGet:
    path: /ready
    port: 8080
  initialDelaySeconds: 30
  periodSeconds: 10
  failureThreshold: 3
  successThreshold: 2   # Require 2 successes
```

### Pod Disruption Budget

**Development (Flexible):**
```yaml
podDisruptionBudget:
  enabled: false  # Not needed for development
```

**Learning PDB:**
```yaml
podDisruptionBudget:
  enabled: true
  maxUnavailable: 1  # Allow 1 pod disruption

# Or percentage-based
podDisruptionBudget:
  enabled: true
  minAvailable: 50%
```

### Priority Classes

**Development Priorities:**
```yaml
# Low priority for test workloads
priorityClassName: low-priority

# Configuration
apiVersion: scheduling.k8s.io/v1
kind: PriorityClass
metadata:
  name: low-priority
value: 100
preemptionPolicy: PreemptLowerPriority
globalDefault: false
description: "Low priority for test workloads"
```

---

## Network Optimization

### Service Type Selection

```yaml
Development:
  # Use ClusterIP with port-forward
  service:
    type: ClusterIP

  Access:
    kubectl port-forward svc/backend 8080:8080

Testing External Access:
  # Use NodePort
  service:
    type: NodePort
    nodePort: 30080

With Ingress:
  # ClusterIP behind ingress
  service:
    type: ClusterIP
  ingress:
    enabled: true
```

### Ingress Optimization

```yaml
# Minikube ingress configuration
ingress:
  enabled: true
  className: nginx
  annotations:
    # Connection optimization
    nginx.ingress.kubernetes.io/proxy-connect-timeout: "10"
    nginx.ingress.kubernetes.io/proxy-read-timeout: "60"

    # Body size for uploads
    nginx.ingress.kubernetes.io/proxy-body-size: "10m"
```

---

## Storage Optimization

### PVC Sizing

**Conservative Approach:**
```yaml
persistence:
  enabled: true
  size: 10Gi  # Start larger than needed

Rationale:
- Growing PVCs is easier than shrinking
- Disk pressure causes evictions
- SSD storage is generally fast regardless of size
```

**Right-Sized for Development:**
```yaml
persistence:
  enabled: true
  size: 2Gi  # Minimal for development

Monitor:
  kubectl exec -it pod -- df -h
```

### Storage Class Selection

```yaml
# Minikube default (hostPath)
persistence:
  storageClass: ""  # Uses default

# Explicit standard class
persistence:
  storageClass: "standard"
```

---

## Image Optimization

### Base Image Selection

```yaml
Optimization Hierarchy:
1. Distroless (smallest, most secure)
2. Alpine (small, shell available)
3. Slim variants (debian-slim, etc.)
4. Full images (largest, most compatible)

Example Sizes:
- python:3.13        ~1GB
- python:3.13-slim   ~150MB
- python:3.13-alpine ~50MB
```

### Image Pull Optimization

```yaml
# Always pull for development
image:
  pullPolicy: Always

# Use IfNotPresent for stable tags
image:
  pullPolicy: IfNotPresent
  tag: "1.0.0"  # Specific version

# For local development with Minikube
# Build directly in Minikube's Docker
eval $(minikube docker-env)
docker build -t myapp:dev .
# Then use pullPolicy: Never
```

---

## Common Anti-Patterns

### Over-Provisioning

```yaml
# ANTI-PATTERN: Huge resources "just in case"
resources:
  requests:
    cpu: 2000m
    memory: 4Gi
  limits:
    cpu: 4000m
    memory: 8Gi

# PROBLEM:
# - Wastes cluster capacity
# - Fewer pods can be scheduled
# - Higher cost (in cloud)

# SOLUTION: Right-size based on actual usage
resources:
  requests:
    cpu: 200m
    memory: 256Mi
  limits:
    cpu: 500m
    memory: 512Mi
```

### Request = Limit

```yaml
# ANTI-PATTERN: Setting request equal to limit
resources:
  requests:
    cpu: 500m
    memory: 512Mi
  limits:
    cpu: 500m      # Same as request!
    memory: 512Mi  # Same as request!

# PROBLEM:
# - No burst capacity
# - Any spike causes throttling
# - QoS class becomes "Guaranteed" (good for some cases)

# SOLUTION: Allow burst headroom
resources:
  requests:
    cpu: 500m
    memory: 512Mi
  limits:
    cpu: 1000m     # 2x request
    memory: 768Mi  # 1.5x request
```

### No Limits

```yaml
# ANTI-PATTERN: Missing limits
resources:
  requests:
    cpu: 100m
    memory: 128Mi
  # No limits!

# PROBLEM:
# - Pod can consume unlimited resources
# - Can starve other pods
# - Can cause node instability

# SOLUTION: Always set limits
resources:
  requests:
    cpu: 100m
    memory: 128Mi
  limits:
    cpu: 500m
    memory: 512Mi
```

### Latest Tag

```yaml
# ANTI-PATTERN: Using :latest tag
image:
  repository: myapp/backend
  tag: latest

# PROBLEM:
# - Non-deterministic deployments
# - Difficult to rollback
# - Cache invalidation issues

# SOLUTION: Use specific versions
image:
  repository: myapp/backend
  tag: "1.2.3"  # Or use Chart.appVersion
```

---

## Optimization Checklist

### Before Optimizing

- [ ] Collected at least 24h of metrics
- [ ] Identified current resource usage patterns
- [ ] Documented current configuration
- [ ] Have rollback plan ready
- [ ] Changes going through Helm

### Resource Optimization

- [ ] CPU requests based on p90-p95 usage
- [ ] CPU limits allow for burst (1.5-2x requests)
- [ ] Memory requests include GC headroom
- [ ] Memory limits prevent OOMKill
- [ ] No resources set to request = limit

### Configuration Optimization

- [ ] All containers have resource limits
- [ ] Probes configured appropriately
- [ ] Image tags are specific versions
- [ ] No unnecessary privileges

### After Optimizing

- [ ] Monitor for 24h minimum
- [ ] Check for throttling
- [ ] Check for OOMKills
- [ ] Verify latency unchanged
- [ ] Document changes made

---

## Optimization Decision Tree

```
START: Is resource over-provisioned?
│
├─ YES: Usage < 50% of request?
│   │
│   ├─ YES: Reduce request by 20-30%
│   │       Monitor for 24h
│   │       Check for throttling/OOM
│   │
│   └─ NO: Usage 50-80%?
│          └─ Leave as-is (good efficiency)
│
└─ NO: Usage > 80% of request?
    │
    ├─ YES: Check for throttling/OOM
    │   │
    │   ├─ Throttling: Increase CPU limit
    │   └─ OOM: Increase memory limit
    │
    └─ NO: Leave as-is
```

---

## Helm Values Templates

### Development Profile

```yaml
# values-dev.yaml
backend:
  replicaCount: 1
  resources:
    requests:
      cpu: 100m
      memory: 128Mi
    limits:
      cpu: 500m
      memory: 512Mi
  autoscaling:
    enabled: false

frontend:
  replicaCount: 1
  resources:
    requests:
      cpu: 50m
      memory: 64Mi
    limits:
      cpu: 200m
      memory: 256Mi
```

### Optimized Development Profile

```yaml
# values-dev-optimized.yaml
backend:
  replicaCount: 1
  resources:
    requests:
      cpu: 50m      # Reduced based on usage
      memory: 64Mi  # Reduced based on usage
    limits:
      cpu: 200m
      memory: 256Mi

frontend:
  replicaCount: 1
  resources:
    requests:
      cpu: 25m
      memory: 32Mi
    limits:
      cpu: 100m
      memory: 128Mi
```

### Learning/Experimentation Profile

```yaml
# values-learning.yaml
backend:
  replicaCount: 2  # For testing scaling
  resources:
    requests:
      cpu: 100m
      memory: 128Mi
    limits:
      cpu: 300m
      memory: 384Mi
  autoscaling:
    enabled: true
    minReplicas: 1
    maxReplicas: 3
    targetCPUUtilizationPercentage: 50  # Easy to trigger
```
