# Analysis Workflows Reference

Detailed workflows for different types of cluster analysis.

---

## Comprehensive Cluster Assessment

**Purpose:** Full cluster health and efficiency review

### Workflow Steps

```
Step 1: Cluster Overview
kagent analyze cluster --summary

Step 2: Component Health
kagent analyze components --all

Step 3: Resource Utilization
kagent analyze resources --cluster-wide

Step 4: Best Practices
kagent analyze best-practices --all-namespaces

Step 5: Optimization Opportunities
kagent recommend --type all --conservative
```

### Output Template

```
=== Cluster Assessment Report ===

CLUSTER HEALTH: [Healthy/Warning/Critical]
- API Server: [Status]
- Nodes: [Ready/Total]
- Control Plane: [Status]

RESOURCE UTILIZATION:
- CPU: [Usage]% of allocatable
- Memory: [Usage]% of allocatable
- Pods: [Running]/[Capacity]

TOP ISSUES:
1. [Issue description]
2. [Issue description]

OPTIMIZATION OPPORTUNITIES:
1. [Recommendation]
2. [Recommendation]

RECOMMENDED ACTIONS:
1. [Action with Helm command]
2. [Action with Helm command]
```

---

## Namespace Health Check

**Purpose:** Focused analysis of specific namespace

### Workflow Steps

```
Step 1: Workload Status
kagent analyze workloads --namespace myapp

Step 2: Resource Efficiency
kagent analyze resources --namespace myapp --detailed

Step 3: Configuration Audit
kagent analyze config --namespace myapp

Step 4: Network Analysis
kagent analyze network --namespace myapp

Step 5: Recommendations
kagent recommend --namespace myapp
```

### Output Template

```
=== Namespace Health: myapp ===

WORKLOAD STATUS:
- Deployments: [Available/Total]
- Pods: [Running/Total]
- Services: [Count]

RESOURCE EFFICIENCY:
- CPU Utilization: [%]
- Memory Utilization: [%]
- Over-provisioned: [List]

CONFIGURATION ISSUES:
1. [Issue]
2. [Issue]

RECOMMENDATIONS:
1. [Action]
2. [Action]
```

---

## Pre-Deployment Validation

**Purpose:** Validate configuration before deployment

### Workflow Steps

```
Step 1: Resource Availability
kagent analyze capacity --for-deployment ./values.yaml

Step 2: Configuration Check
kagent validate chart ./myapp --values values.yaml

Step 3: Best Practices
kagent lint deployment --strict

Step 4: Risk Assessment
kagent assess risk --deployment myapp
```

### Validation Checklist

```
[ ] Sufficient cluster resources
[ ] Storage class available
[ ] Resource limits defined
[ ] Probes configured
[ ] Security context set
[ ] Image tags specific (not :latest)
```

---

## Performance Investigation

**Purpose:** Diagnose performance issues

### Workflow Steps

```
Step 1: Current Performance Metrics
kagent analyze performance --namespace myapp

Step 2: Bottleneck Detection
kagent analyze bottlenecks --namespace myapp --top 5

Step 3: Resource Pressure
kagent analyze pressure --namespace myapp

Step 4: Historical Comparison
kagent analyze trends --namespace myapp --period 24h
```

### Performance Indicators

| Area | Good | Needs Attention |
|------|------|-----------------|
| Pod Startup | < 30s | > 60s |
| Container Restart | 0 in 24h | > 3 in 24h |
| Image Pull | < 30s | > 60s |
| Service Latency | p95 < 100ms | p95 > 500ms |
| DNS Resolution | < 5ms | > 50ms |

---

## Resource Right-Sizing

**Purpose:** Optimize resource allocation

### Workflow Steps

```
Step 1: Current Usage Analysis
kagent analyze sizing --namespace myapp --period 7d

Step 2: Identify Over-Provisioned
kagent analyze waste --namespace myapp --threshold 40

Step 3: Generate Recommendations
kagent recommend sizing --namespace myapp --conservative

Step 4: Implementation Plan
# Output Helm commands for each recommendation
```

### Right-Sizing Template

```
RESOURCE RIGHT-SIZING: [deployment name]

Current Configuration:
  requests:
    cpu: [current]
    memory: [current]
  limits:
    cpu: [current]
    memory: [current]

Observed Usage (p95 over 7 days):
  cpu: [usage] ([%] of request)
  memory: [usage] ([%] of request)

Recommendation (conservative):
  requests:
    cpu: [new]      # [change description]
    memory: [new]   # [change description]
  limits:
    cpu: [new]
    memory: [new]

Implementation via Helm:
  helm upgrade myapp ./myapp \
    --set backend.resources.requests.cpu=[new] \
    --set backend.resources.requests.memory=[new]

APPROVAL REQUIRED: This change requires user confirmation.
```

---

## Security Audit

**Purpose:** Review security configuration

### Workflow Steps

```
Step 1: Security Posture
kagent analyze security --namespace myapp

Step 2: RBAC Analysis
kagent analyze rbac --namespace myapp

Step 3: Pod Security Standards
kagent analyze pod-security --namespace myapp

Step 4: Network Policy Coverage
kagent analyze network-security --namespace myapp
```

### Security Checklist

```
[ ] Non-root containers
[ ] Read-only root filesystem
[ ] Capabilities dropped
[ ] Resource limits set
[ ] Network policies defined
[ ] Service accounts restricted
[ ] Secrets properly managed
```

---

## Cost Analysis (Educational)

**Purpose:** Understand resource costs for learning

### Workflow Steps

```
Step 1: Resource Cost Estimation
kagent analyze cost --namespace myapp --educational

Step 2: Cost Optimization Opportunities
kagent analyze cost-optimization --namespace myapp

Step 3: Efficiency Score
kagent analyze efficiency-score --namespace myapp
```

### Cost Awareness Template

```
=== Resource Cost Awareness ===

NOTE: This is for educational purposes only.
Actual cloud costs vary by provider and region.

RESOURCE ALLOCATION:
- CPU: [cores] (~$X/month equivalent)
- Memory: [GB] (~$X/month equivalent)
- Storage: [GB] (~$X/month equivalent)

EFFICIENCY OPPORTUNITIES:
1. [Opportunity] - Potential [%] savings
2. [Opportunity] - Potential [%] savings

LEARNING POINTS:
- Over-provisioning wastes resources
- Right-sizing improves efficiency
- Monitoring enables optimization
```

---

## Anomaly Investigation

**Purpose:** Investigate detected anomalies

### Common Anomalies

| Anomaly | Detection | Potential Causes |
|---------|-----------|------------------|
| High restart count | > 3 restarts/hour | OOM, crash, liveness fail |
| Pending pods | Duration > 5min | Resources, scheduling |
| Evictions | Any eviction | Node pressure |
| Failed probes | Continuous failures | App issue, misconfigured |
| Image pull failures | ImagePullBackOff | Registry, image name |
| PVC pending | Duration > 1min | Storage class, quota |

### Investigation Workflow

```
Step 1: Identify Anomaly Type
kagent analyze anomalies --namespace myapp

Step 2: Gather Details
kagent analyze anomaly --id [anomaly-id] --detailed

Step 3: Root Cause Analysis
kagent explain anomaly --id [anomaly-id]

Step 4: Remediation Options
kagent recommend --for-anomaly [anomaly-id]
```
