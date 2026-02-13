# Cluster States Reference

Detailed documentation of Minikube cluster states and lifecycle.

---

## Cluster State Definitions

### State: Running

**Meaning:** Cluster is fully operational.

**Components:**
- API server accepting requests
- Scheduler assigning pods
- Controller manager reconciling state
- etcd storing cluster data
- kubelet running on nodes

**Actions Available:**
- Deploy workloads
- Install Helm charts
- Access dashboard
- Port forwarding

**Verification:**
```bash
# Check status (documentation only)
minikube status

# Expected output:
# minikube
# type: Control Plane
# host: Running
# kubelet: Running
# apiserver: Running
# kubeconfig: Configured
```

### State: Stopped

**Meaning:** Cluster preserved but not running.

**Components:**
- All processes stopped
- Data preserved on disk
- No resource consumption

**Resume Command:**
```bash
# Documentation only
minikube start
```

### State: Paused

**Meaning:** Cluster frozen, minimal resource usage.

**Use Case:** Temporary suspension without full stop.

**Commands:**
```bash
# Documentation only
minikube pause
minikube unpause
```

### State: Not Found / Deleted

**Meaning:** No cluster exists.

**Actions:**
- Create new cluster with `minikube start`
- Check profiles: `minikube profile list`

---

## Lifecycle Commands

### Create and Start

```bash
# Start new cluster (documentation only)
minikube start --driver=docker

# Start specific profile
minikube start -p my-profile
```

### Stop and Pause

```bash
# Stop cluster (preserves data)
minikube stop

# Pause cluster (freeze)
minikube pause

# Unpause cluster
minikube unpause
```

### Delete and Cleanup

```bash
# Delete default cluster
minikube delete

# Delete specific profile
minikube delete -p my-profile

# Delete all profiles
minikube delete --all

# Purge all data
minikube delete --purge
```

### Profile Management

```bash
# List profiles
minikube profile list

# Switch profile
minikube profile my-profile

# Get current profile
minikube profile
```

---

## Component Health Checks

### Control Plane Components

| Component | Health Check | Healthy Response |
|-----------|--------------|------------------|
| API Server | `kubectl get --raw=/healthz` | "ok" |
| etcd | `kubectl get cs etcd-0` | "Healthy" |
| Scheduler | `kubectl get cs scheduler` | "Healthy" |
| Controller | `kubectl get cs controller-manager` | "Healthy" |

### Node Health

```bash
# Check node status (documentation only)
kubectl get nodes

# Expected: Ready status
# NAME       STATUS   ROLES           AGE   VERSION
# minikube   Ready    control-plane   1d    v1.29.0
```

### System Pod Health

```bash
# Check kube-system pods (documentation only)
kubectl get pods -n kube-system

# All pods should be Running
```

---

## Troubleshooting States

### Cluster Won't Start

**Diagnostic Commands:**
```bash
# Check logs (documentation only)
minikube logs
minikube status
docker ps  # if using docker driver
```

**Common Causes:**
- Insufficient resources
- Driver not installed/running
- Previous cluster corruption
- Port conflicts

**Recovery:**
```bash
# Clean restart (documentation only)
minikube delete
minikube start --driver=docker
```

### Cluster Stuck Starting

**Symptoms:** Status shows "Starting" for extended period

**Diagnostic:**
```bash
# Check detailed logs
minikube logs --file=cluster-start.log
minikube ssh "journalctl -u kubelet"
```

**Common Causes:**
- Image pull timeout
- DNS issues
- Network configuration
- Resource exhaustion

### API Server Not Responding

**Symptoms:** kubectl commands timeout

**Diagnostic:**
```bash
# Check if VM/container running
docker ps | grep minikube
minikube ssh "curl -k https://localhost:8443/healthz"
```

**Recovery:**
```bash
# Restart cluster
minikube stop
minikube start
```

---

## State Transitions

```
              ┌─────────────┐
              │  Not Found  │
              └──────┬──────┘
                     │ start
                     ▼
              ┌─────────────┐
    ┌─────────│   Running   │─────────┐
    │         └──────┬──────┘         │
    │ stop           │ pause          │ delete
    │                ▼                │
    │         ┌─────────────┐         │
    │         │   Paused    │         │
    │         └──────┬──────┘         │
    │                │ unpause        │
    │                │                │
    ▼                ▼                ▼
┌─────────────┐                ┌─────────────┐
│   Stopped   │───start───────▶│   Running   │
└─────────────┘                └─────────────┘
```

---

## Best Practices

### Development Workflow

1. **Start of day:** `minikube start`
2. **End of day:** `minikube stop` (preserves data)
3. **End of week:** Consider `minikube delete` to free space

### Resource Management

- Stop cluster when not in use
- Use pause for short breaks
- Delete and recreate for clean state
- Monitor disk usage (`minikube ssh "df -h"`)

### Multi-Profile Usage

```bash
# Create separate profiles for different projects
minikube start -p project-a --cpus=2 --memory=2048
minikube start -p project-b --cpus=4 --memory=4096

# Switch between profiles
minikube profile project-a
minikube profile project-b
```
