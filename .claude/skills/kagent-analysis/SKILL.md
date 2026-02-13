---
name: kagent-analysis
description: Analyze Kubernetes cluster health, performance, and resource efficiency using kagent. Use when assessing cluster state, identifying optimization opportunities, or learning about resource management. Triggers on requests involving cluster analysis, performance tuning, or resource efficiency assessment.
---

# Kagent Analysis Skill

Analyze Kubernetes cluster health, performance, and resource efficiency using kagent.

## Purpose

Enable AI-assisted cluster analysis through kagent that:
- Assesses overall cluster health and component status
- Analyzes resource utilization and efficiency
- Identifies optimization opportunities
- Provides educational insights on Kubernetes best practices
- Maintains advisory-only posture (no automatic changes)

---

## When to Use This Skill

**Use this skill when:**
- Assessing cluster health before/after deployments
- Identifying resource optimization opportunities
- Learning about Kubernetes resource management
- Investigating performance issues
- Validating best practice compliance

**Do NOT use this skill when:**
- Debugging specific pod issues (use kubectl-ai)
- Creating Helm charts (use helm-packaging)
- Setting up clusters (use minikube-cluster)
- Creating Dockerfiles (use docker-containerization)
- Making changes (this skill is advisory-only)

---

## Required Clarifications

Before generating output, clarify these with the user:

### Mandatory Clarifications

1. **What is the analysis scope?** (cluster-wide, namespace, specific workload)
2. **What type of analysis?** (health, performance, resources, security)
3. **What is the optimization comfort level?** (conservative, moderate, aggressive)

### Optional Clarifications (if relevant)

4. **Specific namespace to focus on?**
5. **Time range for metrics?** (1h, 24h, 7d)
6. **Any observed issues to investigate?**

---

## Version Compatibility

| Component | Supported Versions | Notes |
|-----------|-------------------|-------|
| kagent / k8sgpt | Latest | AI-powered K8s analysis |
| Kubernetes | 1.25 - 1.30 | Target cluster |
| metrics-server | 0.6+ | Required for resource metrics |

**Note:** kagent is an emerging tool. This skill documents patterns adaptable to kagent, k8sgpt, and similar AI-assisted K8s analysis tools.

---

## Inputs

### Required Inputs

| Input | Type | Description |
|-------|------|-------------|
| `analysis_scope` | `cluster` \| `namespace` \| `workload` | Scope of analysis |
| `analysis_type` | String | Type: health, performance, cost, security |

### Optional Inputs

| Input | Type | Default | Description |
|-------|------|---------|-------------|
| `namespace` | String | `"default"` | Target namespace |
| `workload` | String | `null` | Specific workload to analyze |
| `time_range` | String | `"1h"` | Time range for metrics |
| `optimization_level` | `conservative` \| `moderate` \| `aggressive` | `"conservative"` | Recommendation style |

---

## Outputs

1. **kagent Analysis Prompts** - Ready-to-use prompts for kagent/k8sgpt
2. **Health Analysis Summaries** - Component status and risk assessment
3. **Optimization Recommendations** - Resource sizing via Helm values

---

## Allowed Actions

- Generate kagent/k8sgpt analysis prompts
- Interpret AI-generated optimization suggestions
- Recommend safe adjustments to Helm values
- Explain resource efficiency concepts
- Provide educational context on K8s best practices

---

## Forbidden Actions

- Auto-applying optimizations to cluster
- Changing Helm values directly
- Scaling workloads without explicit approval
- Executing kubectl commands
- Modifying resource limits automatically

---

## Constraints

### Advisory-Only Role (MANDATORY)
- All outputs are recommendations only
- User must explicitly approve any changes
- Changes must go through Helm upgrade workflow

### Local Cluster Focus
- Optimized for Minikube/local development
- Educational rather than production focus
- Conservative defaults to prevent issues

---

## Analysis Categories

### 1. Cluster Health

```
kagent analyze cluster --health
kagent analyze components --detailed
kagent analyze nodes --include-conditions
```

| Component | Healthy | Warning | Critical |
|-----------|---------|---------|----------|
| API Server | < 100ms | 100-500ms | > 500ms |
| Nodes | Ready | Pressure | NotReady |
| Pods | Running | Pending | CrashLoop |

### 2. Resource Utilization

```
kagent analyze resources --namespace myapp
kagent analyze utilization --summary
kagent analyze waste --threshold 50
```

| Metric | Healthy | Attention | Action Needed |
|--------|---------|-----------|---------------|
| CPU Usage | 20-70% | 70-85% | < 20% or > 85% |
| Memory Usage | 30-75% | 75-90% | < 30% or > 90% |

### 3. Performance

```
kagent analyze latency --namespace myapp
kagent analyze bottlenecks --top 5
kagent analyze network --include-dns
```

### 4. Configuration

```
kagent analyze best-practices --namespace myapp
kagent analyze security --include-rbac
kagent analyze config --validate-limits
```

> **Full analysis workflows**: See [references/analysis-workflows.md](references/analysis-workflows.md)

---

## Optimization Levels

| Level | Buffer | Use Case |
|-------|--------|----------|
| **Conservative** | p95 + 30% | Learning, stability focus |
| **Moderate** | p90 + 20% | Balance efficiency/stability |
| **Aggressive** | p75 + 10% | Maximum efficiency (risky) |

> **Optimization patterns**: See [references/optimization-patterns.md](references/optimization-patterns.md)

---

## Quick Analysis Prompts

### Cluster Health

```
kagent analyze cluster --summary
kagent analyze components --all
```

### Namespace Analysis

```
kagent analyze resources --namespace myapp
kagent analyze best-practices --namespace myapp
kagent recommend --namespace myapp --conservative
```

### Right-Sizing

```
kagent analyze sizing --namespace myapp --period 7d
kagent analyze waste --namespace myapp --threshold 40
kagent recommend sizing --namespace myapp
```

> **Full prompt patterns**: See [references/prompt-patterns.md](references/prompt-patterns.md)

---

## Recommendation Format

```
RESOURCE RIGHT-SIZING: backend deployment

Current:
  requests: cpu=500m, memory=512Mi
  limits: cpu=1000m, memory=1Gi

Observed Usage (p95):
  cpu: 150m (30% of request)
  memory: 280Mi (55% of request)

Recommendation (conservative):
  requests: cpu=200m, memory=350Mi
  limits: cpu=400m, memory=512Mi

Implementation:
  helm upgrade myapp ./myapp \
    --set backend.resources.requests.cpu=200m \
    --set backend.resources.requests.memory=350Mi

APPROVAL REQUIRED: User must confirm before applying.
```

---

## Usage Examples

### Example 1: Resource Efficiency Analysis

**Input:**
```json
{
  "analysis_scope": "namespace",
  "analysis_type": "resource-efficiency",
  "namespace": "myapp",
  "optimization_level": "conservative"
}
```

**Output:**
```
kagent Analysis Prompts:

1. kagent analyze resources --namespace myapp --period 24h
2. kagent analyze waste --namespace myapp --threshold 40
3. kagent recommend sizing --namespace myapp --conservative

Likely Findings:
- Development workloads often over-provisioned
- Typical usage 20-30% of requests
- Conservative right-sizing can free 30-50% resources
```

### Example 2: Performance Investigation

**Input:**
```json
{
  "analysis_scope": "workload",
  "analysis_type": "performance",
  "namespace": "myapp",
  "workload": "deployment/backend",
  "observed_anomalies": ["High latency", "Timeouts"]
}
```

**Output:**
```
kagent Analysis Prompts:

1. kagent analyze performance --deployment backend -n myapp
2. kagent analyze bottlenecks --deployment backend -n myapp
3. kagent analyze resources --deployment backend --pressure

Diagnostic Checklist:
[ ] CPU throttling (limits too low?)
[ ] Memory pressure (approaching limits?)
[ ] Network latency (DNS, service mesh?)
[ ] Resource contention (noisy neighbors?)
```

---

## Educational Concepts

### Requests vs Limits

```
REQUESTS: Guaranteed resources for scheduling
LIMITS: Maximum resources allowed

Best Practices:
- Set requests based on typical usage
- Set limits 1.5-2x requests for burst capacity
- Never set limits = requests (no burst room)
- Never omit limits (unbounded consumption)
```

### Optimization Wisdom

```
1. Measure before optimizing
2. Change one thing at a time
3. Monitor after every change
4. Be conservative in production
5. Document all changes
```

---

## Safety Reminders

```
=== OPTIMIZATION SAFETY CHECKLIST ===

[ ] Reviewed current state metrics
[ ] Understood the recommendation rationale
[ ] Have rollback plan ready
[ ] Changes going through Helm (not kubectl)
[ ] User has explicitly approved change

REMINDER: This skill provides RECOMMENDATIONS ONLY.
All changes require explicit user approval.
```

---

## Integration with Other Skills

| Skill | Integration Point |
|-------|-------------------|
| `minikube-cluster` | Cluster capacity context |
| `helm-packaging` | Changes via Helm values |
| `kubectl-ai` | Detailed resource inspection |

### Workflow

```
1. kagent-analysis → Identify optimization opportunity
2. kubectl-ai → Gather detailed diagnostics
3. helm-packaging → Update values.yaml
4. User approval → Required
5. helm upgrade → Apply changes
6. kagent-analysis → Verify improvement
```

---

## References

### Internal References
- [Prompt Patterns](references/prompt-patterns.md) - kagent prompt examples
- [Optimization Patterns](references/optimization-patterns.md) - Right-sizing patterns
- [Analysis Workflows](references/analysis-workflows.md) - Complete workflows

### External Documentation
- [Kubernetes Resource Management](https://kubernetes.io/docs/concepts/configuration/manage-resources-containers/)
- [k8sgpt (similar tool)](https://github.com/k8sgpt-ai/k8sgpt)
- [Vertical Pod Autoscaler](https://github.com/kubernetes/autoscaler/tree/master/vertical-pod-autoscaler)
