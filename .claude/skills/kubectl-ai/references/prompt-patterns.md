# kubectl-ai Prompt Patterns Reference

Comprehensive natural language prompt patterns for kubectl-ai.

---

## Prompt Structure Best Practices

### Be Specific

```
# GOOD: Specific resource and namespace
kubectl ai "show pods in myapp namespace with label app=backend"

# BAD: Vague query
kubectl ai "show me some pods"
```

### Include Context

```
# GOOD: Full context
kubectl ai "describe deployment backend in myapp namespace and show events from last hour"

# BAD: Missing namespace
kubectl ai "describe backend deployment"
```

### State Desired Format

```
# GOOD: Explicit format
kubectl ai "get backend deployment in myapp namespace as yaml"

# GOOD: Specific columns
kubectl ai "list pods in myapp showing name, status, restarts, and age"
```

---

## Resource Inspection Patterns

### Pods

```
# List all pods in namespace
kubectl ai "list all pods in myapp namespace"

# List pods with specific label
kubectl ai "show pods with label app=backend in myapp namespace"

# Get pod details
kubectl ai "describe pod backend-abc123 in myapp namespace"

# Get pod YAML
kubectl ai "get pod backend-abc123 in myapp as yaml"

# Get pod with wide output
kubectl ai "list pods in myapp with node and IP information"

# Get pods sorted by restart count
kubectl ai "list pods in myapp sorted by restart count descending"

# Get pods by creation time
kubectl ai "show newest pods in myapp namespace"

# Get pods not running
kubectl ai "show pods in myapp that are not in Running state"
```

### Deployments

```
# List deployments
kubectl ai "list all deployments in myapp namespace"

# Describe deployment
kubectl ai "describe deployment backend in myapp namespace"

# Get deployment YAML
kubectl ai "get deployment backend yaml in myapp namespace"

# Check rollout status
kubectl ai "show rollout status for backend deployment in myapp"

# Show rollout history
kubectl ai "show revision history for backend deployment in myapp"

# Get deployment replicas status
kubectl ai "show desired vs ready replicas for deployments in myapp"

# Check deployment conditions
kubectl ai "show conditions for backend deployment in myapp"
```

### Services

```
# List services
kubectl ai "list all services in myapp namespace"

# Describe service
kubectl ai "describe service backend-svc in myapp namespace"

# Get service endpoints
kubectl ai "show endpoints for backend-svc service in myapp"

# Check service selectors
kubectl ai "show selector for backend-svc and matching pods in myapp"

# Get external access info
kubectl ai "show services with NodePort or LoadBalancer in myapp"
```

### Ingress

```
# List ingress resources
kubectl ai "list all ingress in myapp namespace"

# Describe ingress
kubectl ai "describe ingress myapp-ingress in myapp namespace"

# Show ingress rules
kubectl ai "show routing rules for ingress in myapp"

# Check ingress controller
kubectl ai "show ingress controller pods and their status"

# Get ingress addresses
kubectl ai "show ingress addresses and hosts in myapp"
```

### ConfigMaps and Secrets

```
# List ConfigMaps
kubectl ai "list configmaps in myapp namespace"

# Get ConfigMap data
kubectl ai "show data in configmap myapp-config in myapp namespace"

# List Secrets (names only, no decode)
kubectl ai "list secret names in myapp namespace"

# Describe Secret metadata
kubectl ai "describe secret myapp-secrets in myapp showing only metadata"
```

### PersistentVolumeClaims

```
# List PVCs
kubectl ai "list PVCs in myapp namespace with status and storage class"

# Describe PVC
kubectl ai "describe pvc data-pvc in myapp namespace"

# Check PVC binding
kubectl ai "show which PV is bound to pvc data-pvc in myapp"

# Get PVC capacity
kubectl ai "show storage capacity for all PVCs in myapp"
```

### StatefulSets

```
# List StatefulSets
kubectl ai "list statefulsets in myapp namespace"

# Get StatefulSet status
kubectl ai "show replica status for statefulset postgres in myapp"

# Check volume claim templates
kubectl ai "show volume claim templates for statefulset postgres in myapp"

# Get StatefulSet pods in order
kubectl ai "list pods for statefulset postgres in myapp showing ordinal"
```

### Jobs and CronJobs

```
# List Jobs
kubectl ai "list jobs in myapp namespace with completion status"

# Describe Job
kubectl ai "describe job migrate-db in myapp namespace"

# List CronJobs
kubectl ai "list cronjobs in myapp with last schedule time"

# Get CronJob schedule
kubectl ai "show schedule and last run for cronjob cleanup in myapp"

# Check Job pods
kubectl ai "show pods created by job migrate-db in myapp"
```

---

## Log Analysis Patterns

### Basic Log Viewing

```
# Get recent logs
kubectl ai "show last 100 lines of logs from backend pod in myapp"

# Follow logs
kubectl ai "follow logs from backend deployment in myapp"

# Logs with timestamps
kubectl ai "show logs with timestamps from backend in myapp"

# Logs since time
kubectl ai "show logs from backend in myapp since 1 hour ago"
```

### Multi-Container Logs

```
# Specific container logs
kubectl ai "show logs from container api in pod backend-abc in myapp"

# All containers in pod
kubectl ai "show logs from all containers in backend-abc pod"

# Init container logs
kubectl ai "show logs from init container migrate in backend pod"
```

### Log Filtering

```
# Grep for errors
kubectl ai "show logs containing ERROR from backend in myapp"

# Grep for pattern
kubectl ai "show logs matching 'connection refused' from backend pods"

# Previous container logs
kubectl ai "show logs from previous container instance of backend pod"
```

### Aggregated Logs

```
# All pods with label
kubectl ai "show combined logs from pods with label app=backend in myapp"

# Last N lines from each pod
kubectl ai "show last 50 lines from each backend pod in myapp"
```

---

## Event Analysis Patterns

### Namespace Events

```
# Recent events
kubectl ai "show events in myapp namespace sorted by time"

# Warning events only
kubectl ai "show warning events in myapp namespace"

# Events in last hour
kubectl ai "show events from the last hour in myapp namespace"
```

### Resource-Specific Events

```
# Pod events
kubectl ai "show events for pod backend-abc in myapp"

# Deployment events
kubectl ai "show events related to deployment backend in myapp"

# Node events
kubectl ai "show events for node minikube"
```

### Event Filtering

```
# By reason
kubectl ai "show events with reason FailedScheduling in myapp"

# By type
kubectl ai "show Normal events in myapp namespace"

# Count by reason
kubectl ai "count events by reason in myapp namespace"
```

---

## Metrics Patterns

### Resource Usage

```
# Pod metrics
kubectl ai "show cpu and memory usage for pods in myapp"

# Node metrics
kubectl ai "show resource usage for all nodes"

# Container metrics
kubectl ai "show per-container resource usage in myapp namespace"
```

### Top Resources

```
# Top pods by CPU
kubectl ai "show top 10 pods by cpu usage in myapp"

# Top pods by memory
kubectl ai "show top 10 pods by memory usage cluster-wide"

# Top containers
kubectl ai "show containers using most memory in myapp"
```

### Resource Comparison

```
# Usage vs limits
kubectl ai "compare resource usage to limits for pods in myapp"

# Usage vs requests
kubectl ai "show pods exceeding their cpu requests in myapp"

# Cluster capacity
kubectl ai "show cluster capacity vs total requests"
```

---

## Network Debugging Patterns

### DNS Troubleshooting

```
# Check CoreDNS
kubectl ai "show coredns pods and their status"

# CoreDNS logs
kubectl ai "show recent logs from coredns pods"

# DNS config
kubectl ai "show dns configuration for pods in myapp"
```

### Service Discovery

```
# Test service resolution
kubectl ai "show how to test dns resolution for backend-svc.myapp.svc.cluster.local"

# Endpoint status
kubectl ai "show endpoints and their ready status for services in myapp"

# Service to pod mapping
kubectl ai "show which pods are behind service backend-svc in myapp"
```

### Network Policies

```
# List policies
kubectl ai "list network policies in myapp namespace"

# Describe policy
kubectl ai "describe network policy backend-netpol in myapp"

# Check affected pods
kubectl ai "show pods selected by network policy backend-netpol"
```

### Connectivity Testing

```
# Suggest debug pod
kubectl ai "create a temporary debug pod with curl to test connectivity"

# Port forward suggestion
kubectl ai "show how to port forward to backend service in myapp"

# Service external access
kubectl ai "show how to access backend service from outside cluster"
```

---

## RBAC Analysis Patterns

```
# Check service account
kubectl ai "show service account used by backend deployment in myapp"

# List roles
kubectl ai "list roles and rolebindings in myapp namespace"

# Check permissions
kubectl ai "show what permissions service account myapp-sa has"

# Cluster roles
kubectl ai "list cluster roles bound to service accounts in myapp"
```

---

## Node Analysis Patterns

```
# List nodes
kubectl ai "list all nodes with status and roles"

# Node details
kubectl ai "describe node minikube showing conditions and capacity"

# Node resources
kubectl ai "show allocatable vs capacity for node minikube"

# Node conditions
kubectl ai "show nodes with any non-Ready conditions"

# Pods on node
kubectl ai "list pods running on node minikube"

# Taints and tolerations
kubectl ai "show taints on all nodes"
```

---

## Helm-Aware Patterns

### Verify Helm Management

```
# Check release status
kubectl ai "list resources with label app.kubernetes.io/managed-by=Helm in myapp"

# Get release info
kubectl ai "show annotations with helm release info for deployment backend"

# Verify ownership
kubectl ai "check if backend deployment is managed by helm release myapp"
```

### Release Inspection

```
# List Helm releases (via labels)
kubectl ai "list unique helm release names from resource labels in myapp"

# Release resources
kubectl ai "show all resources belonging to helm release myapp"

# Release secrets
kubectl ai "list secrets with type helm.sh/release.v1 in myapp"
```

---

## Namespace Patterns

```
# List namespaces
kubectl ai "list all namespaces with status"

# Namespace resources
kubectl ai "show resource counts by type in myapp namespace"

# Resource quotas
kubectl ai "show resource quotas in myapp namespace"

# Limit ranges
kubectl ai "show limit ranges in myapp namespace"

# Namespace events
kubectl ai "show recent events across myapp namespace"
```

---

## Comparison Patterns

```
# Compare deployments
kubectl ai "compare backend and frontend deployments in myapp"

# Compare pods
kubectl ai "compare resource usage across backend pods in myapp"

# Compare releases
kubectl ai "compare resources between namespace myapp-dev and myapp-prod"

# Compare revisions
kubectl ai "compare deployment backend revision 2 with revision 3"
```

---

## Output Format Patterns

### Format Specification

```
# YAML output
kubectl ai "get deployment backend in myapp as yaml"

# JSON output
kubectl ai "get service backend-svc in myapp as json"

# Wide output
kubectl ai "list pods in myapp with wide output showing node and IP"

# Custom columns
kubectl ai "list pods in myapp showing only name, status, and restarts"

# JSONPath
kubectl ai "get image names for all containers in backend deployment"
```

### Sorted Output

```
# Sort by age
kubectl ai "list pods in myapp sorted by creation time"

# Sort by restarts
kubectl ai "list pods in myapp sorted by restart count"

# Sort by resource usage
kubectl ai "list pods in myapp sorted by memory usage"
```

---

## Safety-Aware Patterns

### Read-Only Queries

```
# These are always safe
kubectl ai "show pods in myapp"              # Safe: GET
kubectl ai "describe deployment backend"      # Safe: GET
kubectl ai "show logs from backend"          # Safe: GET
kubectl ai "list events in myapp"            # Safe: GET
kubectl ai "show resource usage"             # Safe: GET
```

### Queries That Suggest Mutations

```
# These require confirmation
kubectl ai "scale backend to 3 replicas"     # WARN: Mutation
kubectl ai "restart backend deployment"       # WARN: Mutation
kubectl ai "delete pod backend-abc"          # DANGER: Deletion

# Always add safety note when generating these
# SAFETY: This command will modify cluster state.
# Confirm before executing. Consider using helm upgrade instead.
```

---

## Interactive Debugging Patterns

```
# Exec into pod (requires confirmation)
kubectl ai "exec into backend pod in myapp and run bash"

# Run command in pod
kubectl ai "run 'env' command in backend pod in myapp"

# Debug with temporary pod
kubectl ai "create debug pod with network tools in myapp namespace"

# Copy file from pod
kubectl ai "copy /app/logs/error.log from backend pod to local machine"
```

---

## Quick Reference Table

| Intent | kubectl-ai Prompt Pattern |
|--------|---------------------------|
| List pods | `"list pods in {namespace}"` |
| Get pod details | `"describe pod {name} in {namespace}"` |
| View logs | `"show logs from {resource} in {namespace}"` |
| Check events | `"show events in {namespace} sorted by time"` |
| Resource usage | `"show resource usage for pods in {namespace}"` |
| Rollout status | `"show rollout status for deployment {name}"` |
| Service endpoints | `"show endpoints for service {name} in {namespace}"` |
| PVC status | `"show PVC status in {namespace}"` |
| Debug connectivity | `"show how to test connectivity to {service}"` |
| Helm verification | `"check if {resource} is managed by helm"` |
