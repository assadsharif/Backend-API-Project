---
name: minikube-cluster
description: Model and manage local Kubernetes cluster lifecycle for spec-driven learning and validation. Use when configuring Minikube clusters, validating Helm readiness, or debugging local K8s environments. Triggers on requests involving local Kubernetes setup, cluster configuration, or development environment preparation.
---

# Minikube Cluster Skill

Model and manage local Kubernetes cluster lifecycle for spec-driven learning and validation.

## Purpose

Enable configuration and validation of local Kubernetes environments using Minikube:
- Generate startup configurations for various resource profiles
- Validate cluster readiness for Helm deployments
- Explain cluster states and component health
- Provide debugging guidance for common issues

---

## When to Use This Skill

**Use this skill when:**
- Setting up a local Kubernetes cluster for development
- Configuring Minikube for Helm chart testing
- Troubleshooting cluster startup or networking issues
- Learning Kubernetes concepts locally
- Preparing environment for application deployment

**Do NOT use this skill when:**
- Working with cloud Kubernetes (EKS, GKE, AKS)
- Managing production clusters
- Deploying applications (use helm-packaging)
- Debugging application issues (use kubectl-ai)
- Analyzing cluster performance (use kagent-analysis)

---

## Required Clarifications

Before generating output, clarify these with the user:

### Mandatory Clarifications

1. **What is the primary use case?** (learning, Helm testing, multi-service app)
2. **Which driver is available?** (Docker, Podman, Hypervisor)
3. **How much RAM can be allocated?** (minimum 2GB, recommended 4GB+)

### Optional Clarifications (if relevant)

4. **Specific Kubernetes version needed?**
5. **Ingress required for external access?**
6. **Persistent storage needed?**

---

## Version Compatibility

| Component | Supported Versions | Notes |
|-----------|-------------------|-------|
| Minikube | 1.30+ | Recommended: latest |
| Kubernetes | 1.25 - 1.30 | Match target production |
| Docker Driver | Docker 20.10+ | Most compatible |
| Helm | 3.10+ | Tiller-less |

### Driver Compatibility

| Driver | OS | Recommended For |
|--------|-----|-----------------|
| docker | All | Default choice, most reliable |
| podman | Linux | Rootless containers |
| hyperv | Windows | Native virtualization |
| virtualbox | All | Legacy support |
| kvm2 | Linux | Better performance |

---

## Inputs

### Required Inputs

| Input | Type | Description |
|-------|------|-------------|
| `cluster_profile` | `minimal` \| `standard` \| `heavy` | Resource allocation profile |
| `kubernetes_version` | String | Target K8s version (e.g., "1.29.0") |
| `driver` | `docker` \| `podman` \| `hyperv` \| `virtualbox` | Virtualization driver |

### Optional Inputs

| Input | Type | Default | Description |
|-------|------|---------|-------------|
| `cpus` | Number | Profile-based | CPU cores to allocate |
| `memory` | String | Profile-based | Memory allocation (e.g., "4096mb") |
| `disk_size` | String | "20g" | Disk space allocation |
| `addons` | Array | `[]` | Minikube addons to enable |
| `nodes` | Number | 1 | Number of cluster nodes |

---

## Outputs

### Primary Outputs

1. **Minikube Startup Configuration** - Complete `minikube start` command
2. **Validation Checklist** - Pre/post-start health checks
3. **Debugging Prompts** - Issue diagnosis and recovery

---

## Allowed Actions

- Suggest `minikube start` configurations (as documentation)
- Explain cluster states and component health
- Validate Helm deployment readiness
- Recommend addon configurations
- Provide resource tuning recommendations
- Document ingress and storage setup

---

## Forbidden Actions

- Executing `minikube` or `kubectl` commands
- Creating Kubernetes workloads directly
- Modifying host system settings
- Installing software or drivers
- Accessing cloud resources

---

## Constraints

### Local-Only Usage (MANDATORY)
- All configurations target local development only
- No cloud provider assumptions
- Single-machine deployment focus

### Helm Support Required
- Configurations must support Helm 3.x
- Storage provisioner for PVC support
- RBAC enabled (default)

---

## Resource Profiles

| Profile | CPUs | Memory | Disk | Use Case |
|---------|------|--------|------|----------|
| **minimal** | 2 | 2GB | 10GB | Learning basics, simple pods |
| **standard** | 4 | 4GB | 20GB | Helm charts, multi-service apps |
| **heavy** | 6 | 8GB | 40GB | Multi-node, complex workloads |

---

## Configuration Templates

### Standard Helm-Ready Configuration

```bash
# Suggested command (DO NOT EXECUTE - for documentation only)
minikube start \
    --driver=docker \
    --kubernetes-version=v1.29.0 \
    --cpus=4 \
    --memory=4096 \
    --disk-size=20g \
    --addons=ingress,metrics-server,storage-provisioner,default-storageclass
```

### Minimal Learning Configuration

```bash
# Suggested command (DO NOT EXECUTE)
minikube start \
    --driver=docker \
    --kubernetes-version=v1.29.0 \
    --cpus=2 \
    --memory=2048 \
    --addons=dashboard
```

> **More templates**: See [references/configurations.md](references/configurations.md)

---

## Essential Addons

| Addon | Purpose | When to Enable |
|-------|---------|----------------|
| `ingress` | HTTP routing | External access needed |
| `metrics-server` | Resource metrics | HPA, `kubectl top` |
| `dashboard` | Web UI | Visual management |
| `storage-provisioner` | Dynamic PVs | StatefulSets, PVCs |
| `default-storageclass` | Default SC | Helm charts with PVCs |

---

## Validation Checklist

### Pre-Start
- [ ] Virtualization enabled (BIOS/UEFI)
- [ ] Driver installed (Docker/Podman/Hypervisor)
- [ ] Sufficient resources available
- [ ] No conflicting clusters

### Post-Start Health Checks

```bash
# Cluster status (documentation only)
minikube status

# Expected: host=Running, kubelet=Running, apiserver=Running
```

### Helm Readiness

- [ ] `kubectl cluster-info` succeeds
- [ ] `helm version` shows 3.x
- [ ] `kubectl get sc` shows default storage class

> **Full validation details**: See [references/cluster-states.md](references/cluster-states.md)

---

## Service Access Methods

| Method | Command | Use Case |
|--------|---------|----------|
| minikube service | `minikube service <name>` | Quick access |
| Port forward | `kubectl port-forward` | Direct pod access |
| NodePort | Service type: NodePort | Persistent mapping |
| Ingress | Ingress resource | Domain-based routing |
| Tunnel | `minikube tunnel` | LoadBalancer services |

---

## Quick Debugging

| Issue | Diagnostic | Solution |
|-------|------------|----------|
| Won't start | `minikube logs` | Delete and recreate |
| Pods pending | `kubectl describe pod` | Check resources, PVCs |
| Service unreachable | `minikube service list` | Check ingress, tunnel |
| Image pull fails | `kubectl get events` | Check registry access |

> **Full troubleshooting**: See [references/troubleshooting.md](references/troubleshooting.md)

---

## Usage Examples

### Example 1: Development Environment

**Input:**
```json
{
  "cluster_profile": "standard",
  "kubernetes_version": "1.29.0",
  "driver": "docker",
  "addons": ["ingress", "metrics-server", "dashboard"]
}
```

**Output:**
```bash
# Suggested startup (DO NOT EXECUTE)
minikube start \
    --driver=docker \
    --kubernetes-version=v1.29.0 \
    --cpus=4 \
    --memory=4096 \
    --disk-size=20g \
    --addons=ingress,metrics-server,dashboard
```

### Example 2: Helm Chart Testing

**Input:**
```json
{
  "cluster_profile": "standard",
  "kubernetes_version": "1.28.0",
  "driver": "docker",
  "addons": ["storage-provisioner", "default-storageclass", "ingress"]
}
```

**Output:**
```bash
# Suggested startup (DO NOT EXECUTE)
minikube start \
    --driver=docker \
    --kubernetes-version=v1.28.0 \
    --cpus=4 \
    --memory=4096 \
    --addons=storage-provisioner,default-storageclass,ingress

# Post-start verification:
# kubectl get sc (verify default storage class)
# helm version (verify Helm 3.x)
```

---

## Integration with SDD Workflow

1. **Specification Phase**: Define cluster requirements
2. **Planning Phase**: Document K8s version, addon choices
3. **Implementation**: Generate configurations (this skill)
4. **Validation**: Verify cluster readiness

### ADR Trigger

> Architectural decision detected: Kubernetes version and addon selection
> Document reasoning? Run `/sp.adr minikube-cluster-config`

---

## References

### Internal References
- [Cluster Configurations](references/configurations.md) - Driver-specific configs
- [Cluster States](references/cluster-states.md) - States and lifecycle
- [Troubleshooting](references/troubleshooting.md) - Debugging guides

### External Documentation
- [Minikube Documentation](https://minikube.sigs.k8s.io/docs/)
- [Minikube Drivers](https://minikube.sigs.k8s.io/docs/drivers/)
- [Minikube Addons](https://minikube.sigs.k8s.io/docs/handbook/addons/)
