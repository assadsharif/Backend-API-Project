# Safety Classification Reference

Risk levels and confirmation requirements for kubectl-ai operations.

---

## Safety Categories

### Safe Operations (Green)

Read-only operations that don't modify cluster state.

| Operation | Risk Level | Confirmation | Example |
|-----------|------------|--------------|---------|
| Get resources | None | Not required | `get pods` |
| Describe resources | None | Not required | `describe deployment` |
| List resources | None | Not required | `get all -n myapp` |
| View logs | None | Not required | `logs pod/backend` |
| View events | None | Not required | `get events` |
| Explain resources | None | Not required | `explain deployment` |
| Top (metrics) | None | Not required | `top pods` |

**kubectl-ai Prompts (Safe):**
```
kubectl ai "show me all pods in the myapp namespace"
kubectl ai "describe the backend deployment"
kubectl ai "get logs from backend pod"
kubectl ai "show events in myapp namespace"
kubectl ai "show cpu and memory usage for pods"
```

### Caution Operations (Yellow)

Operations that may affect workloads but are recoverable.

| Operation | Risk Level | Confirmation | Impact |
|-----------|------------|--------------|--------|
| Scale deployment | Medium | Required | Changes replica count |
| Restart rollout | Medium | Required | Restarts all pods |
| Port forward | Low | Recommended | Opens network tunnel |
| Exec into pod | Medium | Required | Shell access to container |
| Copy files | Medium | Required | Transfers data |
| Cordon node | High | Required | Prevents scheduling |

**kubectl-ai Prompts (Caution):**
```
kubectl ai "scale backend deployment to 3 replicas in myapp"
kubectl ai "restart backend deployment in myapp"
kubectl ai "exec into backend pod in myapp"
kubectl ai "copy /tmp/file from backend pod"
```

**Warning Template:**
```
WARNING: This operation modifies cluster state.
Operation: [Scale/Restart/Exec]
Affected: [Resource name]
Impact: [Description of what will change]
Reversible: Yes
Recommended: Proceed with caution
```

### Dangerous Operations (Red)

Destructive operations that may cause data loss or outages.

| Operation | Risk Level | Confirmation | Impact |
|-----------|------------|--------------|--------|
| Delete resources | Critical | MANDATORY | Permanent removal |
| Drain node | Critical | MANDATORY | Evicts all pods |
| Delete namespace | Critical | MANDATORY | Deletes all resources |
| Force delete pod | High | MANDATORY | Immediate termination |
| Patch resources | High | MANDATORY | Modifies spec |
| Edit resources | High | MANDATORY | Inline modification |

**kubectl-ai Prompts (Dangerous - Use Extreme Caution):**
```
kubectl ai "delete pod backend-xxx in myapp namespace"
kubectl ai "drain node minikube"
kubectl ai "delete namespace test"
kubectl ai "force delete stuck pod"
```

**Mandatory Warning Template:**
```
DANGER: This operation is destructive.
Operation: [Delete/Drain/Patch]
Affected: [Resource name]
Impact: [Permanent data loss / Service disruption]
Reversible: NO / Partially
MANDATORY: User confirmation required before execution

Type 'yes' to confirm or 'no' to cancel.
```

---

## Helm Resource Safety

### Special Considerations for Helm-Managed Resources

All resources with these labels should be modified via Helm, not kubectl:

```yaml
Labels:
  app.kubernetes.io/managed-by: Helm
  helm.sh/chart: myapp-1.0.0
  app.kubernetes.io/instance: myapp
```

**Before Any Modification:**
```
kubectl ai "check if backend deployment has helm managed-by label"
```

**If Helm-Managed:**
```
WARNING: This resource is managed by Helm.
Direct modification will cause drift from Helm state.

RECOMMENDED: Use helm upgrade instead:
  helm upgrade myapp ./myapp --set backend.replicaCount=3

Proceed with kubectl anyway? (not recommended)
```

---

## Confirmation Workflow

### Standard Confirmation Flow

```
1. User requests operation
2. kubectl-ai generates command
3. Safety classification displayed
4. User confirms (y/n)
5. Command executed (if confirmed)
6. Result displayed
```

### Enhanced Confirmation for Dangerous Operations

```
1. User requests operation
2. kubectl-ai generates command
3. DANGER warning displayed
4. Impact analysis shown
5. User types 'yes' (not just 'y')
6. 5-second delay
7. Command executed
8. Result verified
```

---

## Best Practices

### Always Verify First

Before any modification:
```
kubectl ai "show current state of backend deployment"
kubectl ai "show events for backend in last hour"
```

### Use Dry-Run When Available

For testing commands:
```
kubectl ai "dry-run scale backend to 3 replicas"
kubectl ai "dry-run delete pod backend-xxx"
```

### Document Changes

After modifications:
```
kubectl ai "show rollout history for backend"
kubectl ai "compare current state with previous"
```
