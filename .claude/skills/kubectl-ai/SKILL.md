---
name: kubectl-ai
description: Use kubectl-ai as an AI-assisted interface for Kubernetes operations and diagnostics. Use when generating kubectl-ai prompts, interpreting cluster state, or debugging workloads. Triggers on requests involving Kubernetes diagnostics, resource inspection, or AI-assisted cluster operations.
---

# Kubectl-AI Skill

Use kubectl-ai as an AI-assisted interface for Kubernetes operations and diagnostics.

## Purpose

Enable AI-assisted Kubernetes operations through kubectl-ai that:
- Generate natural language prompts for cluster interactions
- Provide observability into workload state and health
- Support debugging and diagnostics workflows
- Maintain safety through confirmation requirements
- Respect Helm-managed resource boundaries

---

## When to Use This Skill

**Use this skill when:**
- Diagnosing pod/service issues in Kubernetes
- Generating kubectl commands from natural language
- Analyzing logs, events, and metrics
- Troubleshooting deployment problems
- Learning kubectl syntax through AI assistance

**Do NOT use this skill when:**
- Setting up Kubernetes cluster (use minikube-cluster)
- Creating Helm charts (use helm-packaging)
- Creating Dockerfiles (use docker-containerization)
- Analyzing cluster efficiency (use kagent-analysis)
- Making configuration changes (use Helm upgrade)

---

## Required Clarifications

Before generating output, clarify these with the user:

### Mandatory Clarifications

1. **What is the issue or goal?** (diagnose pod crash, check service connectivity, etc.)
2. **Which namespace?** (target namespace for operations)
3. **Is this Helm-managed?** (affects how changes should be made)

### Optional Clarifications (if relevant)

4. **Specific pod/deployment name?** (for targeted diagnostics)
5. **Time range for events/logs?** (last hour, since deployment, etc.)
6. **Read-only or modification needed?** (affects safety level)

---

## Version Compatibility

| Component | Supported Versions | Notes |
|-----------|-------------------|-------|
| kubectl-ai | Latest | Via krew, go install, or brew |
| kubectl | 1.25+ | Must match cluster version ±1 |
| Kubernetes | 1.25 - 1.30 | Target cluster version |

### Installation Methods

```bash
# Via krew (documentation only)
kubectl krew install ai

# Via go install
go install github.com/sozercan/kubectl-ai@latest

# Via Homebrew
brew install sozercan/tap/kubectl-ai
```

---

## Inputs

### Required Inputs

| Input | Type | Description |
|-------|------|-------------|
| `action_intent` | String | What you want to accomplish (natural language) |
| `target_workload` | String | Resource type and name (e.g., "deployment/myapp") |
| `namespace` | String | Target namespace |

### Optional Inputs

| Input | Type | Default | Description |
|-------|------|---------|-------------|
| `observed_symptoms` | String | `null` | Symptoms or errors observed |
| `helm_release` | String | `null` | Associated Helm release name |
| `output_format` | String | `"yaml"` | Preferred output format |

---

## Outputs

1. **kubectl-ai Natural Language Prompts** - Ready-to-use prompts
2. **Expected Kubernetes Effects** - What commands will do
3. **Safety Warnings** - Destructive operation alerts

---

## Allowed Actions

- Generate kubectl-ai prompts (natural language queries)
- Interpret kubectl-ai output and feedback
- Suggest diagnostic queries
- Explain resource states and relationships
- Document troubleshooting workflows
- Generate read-only inspection commands

---

## Forbidden Actions

- Executing kubectl or kubectl-ai commands directly
- Making irreversible changes without confirmation
- Modifying Helm-managed resources imperatively
- Deleting resources without explicit approval
- Creating resources outside Helm lifecycle

---

## Constraints

### Helm-Managed Resources Only (MANDATORY)
- Verify `app.kubernetes.io/managed-by: Helm` label
- No imperative changes to Helm resources
- Changes must go through Helm upgrade

### Observability Focus
- Primary use: inspection and diagnostics
- Read operations preferred over write operations

---

## Safety Classification Summary

| Level | Operations | Confirmation |
|-------|-----------|--------------|
| **Green** (Safe) | get, describe, logs, events, top | Not required |
| **Yellow** (Caution) | scale, restart, exec, port-forward | Required |
| **Red** (Dangerous) | delete, drain, patch, edit | MANDATORY |

> **Full safety guide**: See [references/safety-classification.md](references/safety-classification.md)

---

## Common kubectl-ai Prompts

### Resource Inspection

```
kubectl ai "show me all pods in the myapp namespace"
kubectl ai "describe the backend deployment in myapp"
kubectl ai "get backend deployment yaml in myapp"
kubectl ai "list resources with label app.kubernetes.io/instance=myapp"
```

### Log Analysis

```
kubectl ai "show last 100 lines of logs from backend pod in myapp"
kubectl ai "follow logs from pods with label app=backend in myapp"
kubectl ai "show timestamped logs from backend deployment"
```

### Event Analysis

```
kubectl ai "show recent events in myapp namespace sorted by time"
kubectl ai "show warning events in myapp namespace"
kubectl ai "show events related to backend deployment"
```

### Troubleshooting

```
kubectl ai "why is the backend pod pending in myapp"
kubectl ai "show pods with container restarts in myapp"
kubectl ai "show resource quotas and limits in myapp"
```

> **More prompts**: See [references/prompt-patterns.md](references/prompt-patterns.md)

---

## Quick Diagnostic Workflows

### Pod Not Starting

```
1. kubectl ai "describe pod backend-xxx in myapp and show events"
2. kubectl ai "show node resource availability"
3. kubectl ai "show PVC status in myapp"
```

**Common Causes:** Insufficient resources, PVC not bound, image pull error

### Service Not Accessible

```
1. kubectl ai "show service and endpoints for backend in myapp"
2. kubectl ai "compare service selector with pod labels"
3. kubectl ai "describe ingress in myapp"
```

**Common Causes:** Selector mismatch, no endpoints, ingress misconfigured

### High Resource Usage

```
1. kubectl ai "show resource usage vs limits for pods in myapp"
2. kubectl ai "show pods that were OOMKilled in myapp"
3. kubectl ai "show HPA status for myapp"
```

**Common Causes:** Limits too low, memory leak, HPA not scaling

> **Full workflows**: See [references/diagnostics.md](references/diagnostics.md)

---

## Helm Integration

### Verify Helm Management

```
kubectl ai "show helm release status for myapp"
kubectl ai "check if backend deployment has helm managed-by label"
kubectl ai "list resources with annotation meta.helm.sh/release-name=myapp"
```

### Safe Changes (Always Use Helm)

```
# Instead of: kubectl scale deployment backend --replicas=3
# Suggest: helm upgrade myapp ./myapp --set backend.replicaCount=3

# Instead of: kubectl set image deployment/backend backend=myapp:v2
# Suggest: helm upgrade myapp ./myapp --set backend.image.tag=v2
```

---

## Usage Examples

### Example 1: Debug Pending Pod

**Input:**
```json
{
  "action_intent": "Find out why my pod is stuck in Pending",
  "target_workload": "pod/backend-abc123",
  "namespace": "myapp",
  "observed_symptoms": "Pod has been Pending for 5 minutes"
}
```

**Output:**
```
kubectl-ai Prompts:

1. "describe pod backend-abc123 in myapp and show events"
   Safety: Read-only, safe

2. "show node resources and allocatable capacity"
   Safety: Read-only, safe

3. "show PVC status in myapp"
   Safety: Read-only, safe

Common Causes:
- Insufficient resources → Adjust via Helm values
- PVC not bound → Check storage class
- Node affinity → Verify node labels
```

### Example 2: Investigate OOMKilled Pods

**Input:**
```json
{
  "action_intent": "Find why backend pods are being OOMKilled",
  "target_workload": "deployment/backend",
  "namespace": "myapp",
  "helm_release": "myapp"
}
```

**Output:**
```
kubectl-ai Prompts:

1. "show memory usage for backend pods in myapp"
2. "show events mentioning OOMKilled in myapp"
3. "describe deployment backend and show resource limits"
4. "show helm values for myapp release"

Resolution:
  helm upgrade myapp ./myapp --set backend.resources.limits.memory=1Gi
```

---

## Integration with Other Skills

| Skill | Integration Point |
|-------|-------------------|
| `docker-containerization` | Debug container/image issues |
| `minikube-cluster` | Local cluster context |
| `helm-packaging` | Changes via Helm upgrade |
| `kagent-analysis` | Optimization recommendations |

### Workflow

```
1. minikube-cluster → Cluster running
2. helm-packaging → Chart deployed
3. kubectl-ai → Monitor, debug (this skill)
4. helm-packaging → Changes via helm upgrade
```

---

## References

### Internal References
- [Prompt Patterns](references/prompt-patterns.md) - Comprehensive prompt examples
- [Diagnostics](references/diagnostics.md) - Troubleshooting workflows
- [Safety Classification](references/safety-classification.md) - Risk levels and confirmation

### External Documentation
- [kubectl-ai GitHub](https://github.com/sozercan/kubectl-ai)
- [kubectl Cheat Sheet](https://kubernetes.io/docs/reference/kubectl/cheatsheet/)
- [Kubernetes Debugging](https://kubernetes.io/docs/tasks/debug/)
