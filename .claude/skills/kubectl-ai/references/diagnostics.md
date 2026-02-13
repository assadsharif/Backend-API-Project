# Kubernetes Diagnostics Reference

Comprehensive troubleshooting workflows using kubectl-ai.

---

## Diagnostic Methodology

### 1. Observe → 2. Analyze → 3. Hypothesize → 4. Verify → 5. Resolve

1. **Observe**: Gather symptoms without assumptions
2. **Analyze**: Examine events, logs, resource states
3. **Hypothesize**: Form theories about root cause
4. **Verify**: Test hypothesis with targeted queries
5. **Resolve**: Address via Helm upgrade (never imperative kubectl)

---

## Pod Issues

### Pod Stuck in Pending

**Symptoms:** Pod remains in Pending state, never schedules

**Diagnostic Workflow:**

```
Step 1: Get pod events
kubectl ai "describe pod {name} in {namespace} and show events"

Step 2: Check node resources
kubectl ai "show nodes with allocatable cpu and memory"

Step 3: Check PVC status (if pod uses volumes)
kubectl ai "show PVC status for PVCs used by pod {name}"

Step 4: Check node selectors/affinity
kubectl ai "show nodeSelector and affinity for pod {name}"

Step 5: Check taints and tolerations
kubectl ai "show taints on all nodes and tolerations for pod {name}"
```

**Common Causes & Solutions:**

| Event Message | Cause | Resolution |
|---------------|-------|------------|
| "Insufficient cpu" | Node lacks CPU | Reduce resource requests or add nodes |
| "Insufficient memory" | Node lacks memory | Reduce resource requests or add nodes |
| "no persistent volumes available" | PVC not bound | Check storage class, create PV |
| "node(s) didn't match node selector" | Label mismatch | Fix nodeSelector or label nodes |
| "node(s) had taints that pod didn't tolerate" | Taint blocking | Add tolerations or remove taints |

---

### Pod Stuck in ContainerCreating

**Symptoms:** Pod stays in ContainerCreating state

**Diagnostic Workflow:**

```
Step 1: Check pod events
kubectl ai "show events for pod {name} in {namespace}"

Step 2: Check image pull status
kubectl ai "describe pod {name} showing image pull events"

Step 3: Check volume mounts
kubectl ai "show volume mount status for pod {name}"

Step 4: Check secrets/configmaps exist
kubectl ai "verify secrets and configmaps referenced by pod {name} exist"
```

**Common Causes & Solutions:**

| Event Message | Cause | Resolution |
|---------------|-------|------------|
| "ErrImagePull" | Image doesn't exist | Verify image name and tag |
| "ImagePullBackOff" | Auth or rate limit | Check imagePullSecrets, registry auth |
| "MountVolume.SetUp failed" | Volume issue | Check PVC binding, CSI driver |
| "secret not found" | Missing secret | Create secret or fix reference |
| "configmap not found" | Missing ConfigMap | Create ConfigMap or fix reference |

---

### Pod in CrashLoopBackOff

**Symptoms:** Container repeatedly crashes and restarts

**Diagnostic Workflow:**

```
Step 1: Check restart count and timing
kubectl ai "show pod {name} restart count and last restart time"

Step 2: Get container logs
kubectl ai "show logs from pod {name} in {namespace}"

Step 3: Get previous container logs
kubectl ai "show logs from previous container in pod {name}"

Step 4: Check exit codes
kubectl ai "show container exit codes for pod {name}"

Step 5: Check resource limits
kubectl ai "show resource limits vs usage for pod {name}"

Step 6: Check liveness probe
kubectl ai "show liveness probe configuration for pod {name}"
```

**Exit Code Reference:**

| Exit Code | Meaning | Investigation |
|-----------|---------|---------------|
| 0 | Normal exit | Check if CMD/entrypoint designed to exit |
| 1 | Application error | Check application logs |
| 126 | Command not executable | Check file permissions |
| 127 | Command not found | Check image has required binaries |
| 128 | Invalid exit argument | Application bug |
| 137 | SIGKILL (OOMKilled) | Increase memory limit |
| 139 | SIGSEGV (segfault) | Application bug |
| 143 | SIGTERM | Normal termination signal |

---

### Pod OOMKilled

**Symptoms:** Container killed due to memory limit

**Diagnostic Workflow:**

```
Step 1: Confirm OOMKill
kubectl ai "show events mentioning OOMKilled for pod {name}"

Step 2: Check memory limit
kubectl ai "show memory limit for containers in pod {name}"

Step 3: Check memory usage before kill
kubectl ai "show memory usage metrics for pod {name}"

Step 4: Check if limit matches request
kubectl ai "compare memory request vs limit for pod {name}"
```

**Resolution via Helm:**
```yaml
# Increase memory limit in values.yaml
backend:
  resources:
    limits:
      memory: "1Gi"  # Increase from 512Mi
```

---

### Pod Evicted

**Symptoms:** Pod terminated with "Evicted" status

**Diagnostic Workflow:**

```
Step 1: Check eviction reason
kubectl ai "describe evicted pods in {namespace} and show reason"

Step 2: Check node conditions
kubectl ai "show node conditions for node that evicted pod"

Step 3: Check node disk pressure
kubectl ai "show disk usage and pressure on nodes"

Step 4: Check resource usage cluster-wide
kubectl ai "show resource usage summary for all nodes"
```

**Common Eviction Causes:**

| Reason | Cause | Resolution |
|--------|-------|------------|
| DiskPressure | Node disk full | Clean up images, increase disk |
| MemoryPressure | Node memory exhausted | Add memory, reduce workloads |
| PIDPressure | Too many processes | Investigate runaway processes |

---

## Service Issues

### Service Has No Endpoints

**Symptoms:** Service exists but has no endpoints

**Diagnostic Workflow:**

```
Step 1: Check endpoints
kubectl ai "show endpoints for service {name} in {namespace}"

Step 2: Get service selector
kubectl ai "show selector for service {name} in {namespace}"

Step 3: Find matching pods
kubectl ai "list pods matching selector {selector} in {namespace}"

Step 4: Verify pod labels
kubectl ai "show labels on pods in {namespace} that should match service"

Step 5: Check pod readiness
kubectl ai "show ready status for pods selected by service {name}"
```

**Common Causes:**

| Issue | Diagnostic | Resolution |
|-------|------------|------------|
| Selector mismatch | Pods don't have matching labels | Fix labels in Helm values |
| No ready pods | All pods failing readiness | Fix readiness probe or app |
| Wrong namespace | Service in different namespace | Check service namespace |
| No pods running | Deployment has 0 replicas | Scale up or check deployment |

---

### Service Not Accessible

**Symptoms:** Cannot reach service from inside or outside cluster

**Diagnostic Workflow:**

```
Step 1: Verify service exists
kubectl ai "describe service {name} in {namespace}"

Step 2: Check service type
kubectl ai "show type and ports for service {name}"

Step 3: Verify endpoints exist
kubectl ai "show endpoints for service {name}"

Step 4: Check network policies
kubectl ai "list network policies affecting namespace {namespace}"

Step 5: Test from within cluster
kubectl ai "show how to create debug pod to test service connectivity"

Step 6: Check ingress (if external)
kubectl ai "describe ingress routing to service {name}"
```

**Access Methods by Service Type:**

| Type | Internal Access | External Access |
|------|-----------------|-----------------|
| ClusterIP | `svc-name.namespace:port` | kubectl port-forward |
| NodePort | `node-ip:nodePort` | `node-ip:nodePort` |
| LoadBalancer | `svc-name.namespace:port` | `external-ip:port` |

---

## Ingress Issues

### Ingress Not Routing

**Symptoms:** Requests to ingress return 404 or timeout

**Diagnostic Workflow:**

```
Step 1: Check ingress status
kubectl ai "describe ingress {name} in {namespace}"

Step 2: Verify ingress controller running
kubectl ai "show pods in ingress-nginx namespace with status"

Step 3: Check ingress class
kubectl ai "show ingressClassName for ingress {name}"

Step 4: Verify backend services exist
kubectl ai "check services referenced by ingress {name} exist"

Step 5: Check ingress controller logs
kubectl ai "show logs from ingress controller for errors"

Step 6: Verify host header
kubectl ai "show hosts configured in ingress {name}"
```

**Common Issues:**

| Symptom | Cause | Resolution |
|---------|-------|------------|
| 404 Not Found | Path mismatch | Check path and pathType |
| 503 Service Unavailable | Backend has no endpoints | Fix service/deployment |
| Connection refused | Ingress controller not running | Check ingress-nginx pods |
| Timeout | Network policy blocking | Check network policies |

---

## Deployment Issues

### Rollout Stuck

**Symptoms:** Deployment rollout doesn't complete

**Diagnostic Workflow:**

```
Step 1: Check rollout status
kubectl ai "show rollout status for deployment {name} in {namespace}"

Step 2: Check replica sets
kubectl ai "show replica sets for deployment {name} with ready count"

Step 3: Check new pods
kubectl ai "show pods from new replica set for deployment {name}"

Step 4: Check pod events
kubectl ai "show events for pods in new replica set of {name}"

Step 5: Check PDB
kubectl ai "show pod disruption budgets affecting deployment {name}"

Step 6: Check resource quotas
kubectl ai "show resource quota usage in {namespace}"
```

**Rollout Strategies:**

| Strategy | Behavior | Stuck Reason |
|----------|----------|--------------|
| RollingUpdate | Gradual replacement | New pods failing, PDB blocking |
| Recreate | Delete all, create new | New pods not starting |

---

### ReplicaSet Not Scaling

**Symptoms:** Deployment shows desired replicas but not available

**Diagnostic Workflow:**

```
Step 1: Check deployment status
kubectl ai "show replicas status for deployment {name}"

Step 2: Check ReplicaSet status
kubectl ai "describe newest replica set for deployment {name}"

Step 3: Check pod creation
kubectl ai "show pods being created by replica set"

Step 4: Check node capacity
kubectl ai "show available resources on nodes vs pod requests"

Step 5: Check scheduler events
kubectl ai "show scheduling events for deployment {name} pods"
```

---

## Storage Issues

### PVC Stuck in Pending

**Symptoms:** PVC remains in Pending state

**Diagnostic Workflow:**

```
Step 1: Check PVC status
kubectl ai "describe pvc {name} in {namespace}"

Step 2: Check storage class
kubectl ai "describe storage class {storageClass}"

Step 3: Check provisioner
kubectl ai "show pods for storage provisioner"

Step 4: Check available PVs (static provisioning)
kubectl ai "list persistent volumes with Available status"

Step 5: Check storage quota
kubectl ai "show storage resource quota in {namespace}"
```

**Common Causes:**

| Cause | Diagnostic | Resolution |
|-------|------------|------------|
| No storage class | StorageClass not specified | Set storageClassName |
| Provisioner not running | CSI pods not ready | Check storage system |
| No matching PV | Static provisioning mismatch | Create matching PV |
| Quota exceeded | Storage quota limit | Increase quota or delete PVCs |

---

### Volume Mount Failures

**Symptoms:** Pod fails to mount volume

**Diagnostic Workflow:**

```
Step 1: Check pod events
kubectl ai "show volume mount events for pod {name}"

Step 2: Verify PVC is bound
kubectl ai "show binding status for PVC used by pod {name}"

Step 3: Check CSI driver
kubectl ai "show CSI driver pods and status"

Step 4: Check node has volume plugin
kubectl ai "describe node showing volume plugins"
```

---

## Network Policy Issues

### Pods Cannot Communicate

**Symptoms:** Pods cannot reach other pods or services

**Diagnostic Workflow:**

```
Step 1: List network policies
kubectl ai "list network policies in {namespace}"

Step 2: Check policies affecting pod
kubectl ai "show network policies selecting pod {name}"

Step 3: Analyze ingress rules
kubectl ai "show ingress rules for network policies in {namespace}"

Step 4: Analyze egress rules
kubectl ai "show egress rules for network policies in {namespace}"

Step 5: Test connectivity
kubectl ai "create debug pod to test connectivity to {target}"
```

**Network Policy Debug:**

| Cannot Reach | Check | Resolution |
|--------------|-------|------------|
| Other pods in namespace | Ingress rules on target | Add allow rule |
| Pods in other namespace | Namespace selectors | Add namespaceSelector |
| External services | Egress rules | Add egress allow rule |
| DNS | Egress to kube-dns | Allow UDP 53 to kube-system |

---

## HPA Issues

### HPA Not Scaling

**Symptoms:** HPA shows targets but doesn't scale

**Diagnostic Workflow:**

```
Step 1: Check HPA status
kubectl ai "describe hpa {name} in {namespace}"

Step 2: Check metrics availability
kubectl ai "show if metrics are available for HPA {name}"

Step 3: Check metrics-server
kubectl ai "show metrics-server pods and status"

Step 4: Check current metrics
kubectl ai "show current vs target metrics for HPA {name}"

Step 5: Check scale limits
kubectl ai "show min and max replicas for HPA {name}"
```

**HPA Troubleshooting:**

| Issue | Cause | Resolution |
|-------|-------|------------|
| "unknown" metrics | metrics-server not running | Deploy metrics-server |
| Doesn't scale up | Already at maxReplicas | Increase maxReplicas |
| Doesn't scale down | stabilizationWindow active | Wait or adjust window |
| Metrics too low | Threshold not met | Adjust targetUtilization |

---

## DNS Issues

### DNS Resolution Failing

**Symptoms:** Pods cannot resolve service names

**Diagnostic Workflow:**

```
Step 1: Check CoreDNS pods
kubectl ai "show coredns pods in kube-system with status"

Step 2: Check CoreDNS logs
kubectl ai "show recent logs from coredns pods"

Step 3: Check DNS service
kubectl ai "show kube-dns service and endpoints"

Step 4: Check pod DNS config
kubectl ai "show dns config for pod {name}"

Step 5: Test resolution
kubectl ai "show how to test dns resolution for {service}.{namespace}.svc.cluster.local"
```

**DNS Debug:**

```
# Create debug pod
kubectl ai "run temporary busybox pod to test nslookup"

# Expected inside pod:
# nslookup kubernetes.default
# nslookup backend-svc.myapp.svc.cluster.local
```

---

## Quick Diagnostic Commands

### Health Check Sequence

```
# 1. Namespace overview
kubectl ai "summarize resource health in {namespace}"

# 2. Failing pods
kubectl ai "show pods not in Running/Completed state in {namespace}"

# 3. Recent warnings
kubectl ai "show warning events in last 30 minutes in {namespace}"

# 4. Resource pressure
kubectl ai "show pods near resource limits in {namespace}"

# 5. Pending resources
kubectl ai "show pending pods and PVCs in {namespace}"
```

### Emergency Triage

```
# Cluster health
kubectl ai "show any nodes with issues"
kubectl ai "show control plane component status"

# Namespace health
kubectl ai "count pods by status in {namespace}"
kubectl ai "show deployments with unavailable replicas in {namespace}"

# Recent problems
kubectl ai "show warning events cluster-wide in last 10 minutes"
```

---

## Diagnostic Cheat Sheet

| Symptom | First Command | Next Steps |
|---------|---------------|------------|
| Pod Pending | `describe pod` | Check events, node resources |
| Pod CrashLoop | `logs --previous` | Check exit code, memory |
| Service 503 | `get endpoints` | Check pod readiness |
| Ingress 404 | `describe ingress` | Check paths, backend |
| PVC Pending | `describe pvc` | Check storage class |
| HPA not scaling | `describe hpa` | Check metrics-server |
| DNS failing | `logs coredns` | Check kube-dns service |
| Network blocked | `get networkpolicy` | Check ingress/egress rules |
