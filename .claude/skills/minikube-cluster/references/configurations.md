# Minikube Configuration Reference

Comprehensive configuration patterns for various drivers, platforms, and use cases.

---

## Driver-Specific Configurations

### Docker Driver (Recommended)

**Platforms:** Linux, macOS, Windows (with Docker Desktop)

```bash
# Standard configuration (documentation only)
minikube start \
    --driver=docker \
    --kubernetes-version=v1.29.0 \
    --cpus=4 \
    --memory=4096 \
    --disk-size=20g
```

**Pros:**
- Fastest startup time
- No additional virtualization layer
- Works inside containers (CI/CD)
- Rootless mode support on Linux

**Cons:**
- Requires Docker to be running
- Some networking limitations vs VM drivers

**Docker-specific flags:**
```bash
# Container runtime selection
--container-runtime=containerd  # or docker, cri-o

# Rootless mode (Linux only)
--driver=docker --rootless
```

### Podman Driver

**Platforms:** Linux, macOS (with Podman Machine)

```bash
# Podman configuration (documentation only)
minikube start \
    --driver=podman \
    --kubernetes-version=v1.29.0 \
    --cpus=4 \
    --memory=4096 \
    --container-runtime=cri-o
```

**Pros:**
- Daemonless container runtime
- Rootless by default
- Drop-in Docker replacement

**Cons:**
- Less mature than Docker driver
- Some compatibility issues with certain workloads

### Hyper-V Driver (Windows)

**Platforms:** Windows 10/11 Pro, Enterprise, Education

```bash
# Hyper-V configuration (documentation only)
minikube start \
    --driver=hyperv \
    --hyperv-virtual-switch="Default Switch" \
    --kubernetes-version=v1.29.0 \
    --cpus=4 \
    --memory=4096
```

**Prerequisites:**
- Hyper-V feature enabled
- Admin privileges
- Virtual switch configured

**Hyper-V specific flags:**
```bash
# External network access
--hyperv-virtual-switch="External Switch"

# Use external virtual switch for bridged networking
--hyperv-use-external-switch
```

### VirtualBox Driver

**Platforms:** Linux, macOS, Windows

```bash
# VirtualBox configuration (documentation only)
minikube start \
    --driver=virtualbox \
    --kubernetes-version=v1.29.0 \
    --cpus=4 \
    --memory=4096 \
    --disk-size=20g
```

**Pros:**
- Cross-platform
- Full VM isolation
- GUI available

**Cons:**
- Slower than container-based drivers
- Larger resource footprint
- Nested virtualization issues

**VirtualBox specific flags:**
```bash
# Host-only network CIDR
--host-only-cidr="192.168.99.1/24"

# No VTX check (for nested virtualization)
--no-vtx-check
```

### KVM2 Driver (Linux)

**Platforms:** Linux only

```bash
# KVM2 configuration (documentation only)
minikube start \
    --driver=kvm2 \
    --kubernetes-version=v1.29.0 \
    --cpus=4 \
    --memory=4096
```

**Prerequisites:**
```bash
# Check KVM support (documentation only)
egrep -c '(vmx|svm)' /proc/cpuinfo
# Output > 0 means KVM supported

# Install libvirt (Ubuntu/Debian)
sudo apt install qemu-kvm libvirt-daemon-system
```

**Pros:**
- Native Linux virtualization
- Better performance than VirtualBox
- GPU passthrough capable

---

## Platform-Specific Configurations

### Linux

```bash
# Recommended: Docker driver (documentation only)
minikube start \
    --driver=docker \
    --kubernetes-version=v1.29.0 \
    --cpus=4 \
    --memory=4096

# Alternative: KVM2 for full VM
minikube start \
    --driver=kvm2 \
    --kubernetes-version=v1.29.0 \
    --cpus=4 \
    --memory=4096
```

**Linux-specific considerations:**
- Docker driver is fastest
- KVM2 for production-like isolation
- Rootless Docker available
- cgroup v2 support check required

### macOS

```bash
# Intel Mac: Docker driver (documentation only)
minikube start \
    --driver=docker \
    --kubernetes-version=v1.29.0 \
    --cpus=4 \
    --memory=4096

# Apple Silicon (M1/M2/M3): Docker driver
minikube start \
    --driver=docker \
    --kubernetes-version=v1.29.0 \
    --cpus=4 \
    --memory=4096
```

**macOS-specific considerations:**
- Docker Desktop required (includes VM)
- Apple Silicon uses ARM64 images
- Hypervisor.framework available (experimental)
- Resource limits set in Docker Desktop

### Windows

```bash
# With Docker Desktop (documentation only)
minikube start \
    --driver=docker \
    --kubernetes-version=v1.29.0 \
    --cpus=4 \
    --memory=4096

# With Hyper-V (no Docker Desktop)
minikube start \
    --driver=hyperv \
    --kubernetes-version=v1.29.0 \
    --cpus=4 \
    --memory=4096
```

**Windows-specific considerations:**
- WSL2 backend recommended for Docker
- Hyper-V requires Pro/Enterprise
- Path length issues possible
- Admin privileges may be needed

---

## Kubernetes Version Matrix

### Supported Versions

| K8s Version | Minikube Version | Status |
|-------------|------------------|--------|
| 1.30.x | v1.33+ | Latest |
| 1.29.x | v1.32+ | Stable |
| 1.28.x | v1.31+ | Supported |
| 1.27.x | v1.30+ | Supported |
| 1.26.x | v1.29+ | Maintenance |

### Version Selection

```bash
# Latest stable (documentation only)
minikube start --kubernetes-version=stable

# Specific version
minikube start --kubernetes-version=v1.29.0

# Latest version
minikube start --kubernetes-version=latest
```

### List Available Versions

```bash
# Show available versions (documentation only)
minikube config defaults kubernetes-version
```

---

## Advanced Configurations

### Custom API Server Arguments

```bash
# API server customization (documentation only)
minikube start \
    --extra-config=apiserver.enable-admission-plugins=PodSecurityPolicy \
    --extra-config=apiserver.audit-log-path=/var/log/audit.log \
    --extra-config=apiserver.audit-log-maxage=30
```

### Custom Kubelet Arguments

```bash
# Kubelet customization (documentation only)
minikube start \
    --extra-config=kubelet.max-pods=250 \
    --extra-config=kubelet.serialize-image-pulls=false
```

### Custom Controller Manager Arguments

```bash
# Controller manager customization (documentation only)
minikube start \
    --extra-config=controller-manager.node-cidr-mask-size=24
```

### Feature Gates

```bash
# Enable feature gates (documentation only)
minikube start \
    --feature-gates="EphemeralContainers=true,ServerSideApply=true"
```

### Network Plugins

```bash
# Use Calico CNI (documentation only)
minikube start --cni=calico

# Use Cilium CNI
minikube start --cni=cilium

# Use Flannel CNI
minikube start --cni=flannel

# Default (bridge)
minikube start --cni=bridge
```

### Container Runtime Selection

```bash
# containerd (default, recommended)
minikube start --container-runtime=containerd

# Docker (legacy)
minikube start --container-runtime=docker

# CRI-O
minikube start --container-runtime=cri-o
```

---

## Multi-Node Configurations

### Basic Multi-Node

```bash
# 3-node cluster (documentation only)
minikube start \
    --driver=docker \
    --nodes=3 \
    --cpus=2 \
    --memory=2048

# Note: Resources are per-node
# Total: 6 CPUs, 6GB RAM
```

### Named Profile Multi-Node

```bash
# Create named multi-node cluster (documentation only)
minikube start \
    --profile=multinode \
    --nodes=3 \
    --cpus=2 \
    --memory=2048
```

### Add/Remove Nodes

```bash
# Add node to existing cluster (documentation only)
minikube node add

# Add named node
minikube node add --worker

# Remove node
minikube node delete <node-name>

# List nodes
minikube node list
```

### Node Labels and Taints

```bash
# Label nodes (after cluster start, documentation only)
kubectl label nodes minikube-m02 node-type=worker
kubectl label nodes minikube-m03 node-type=worker

# Taint control plane
kubectl taint nodes minikube node-role.kubernetes.io/control-plane:NoSchedule
```

---

## Profile Management

### Create Multiple Clusters

```bash
# Default profile (documentation only)
minikube start

# Named profile
minikube start --profile=dev
minikube start --profile=staging

# List profiles
minikube profile list
```

### Switch Between Profiles

```bash
# Switch active profile (documentation only)
minikube profile dev

# Run command on specific profile
minikube status --profile=staging
```

### Delete Profile

```bash
# Delete specific profile (documentation only)
minikube delete --profile=dev

# Delete all profiles
minikube delete --all
```

---

## Resource Tuning

### Memory Optimization

```bash
# Minimal memory (tight) (documentation only)
minikube start --memory=2048

# Standard development
minikube start --memory=4096

# Heavy workloads
minikube start --memory=8192

# Maximum (use with caution)
minikube start --memory=16384
```

### CPU Optimization

```bash
# Minimal (documentation only)
minikube start --cpus=2

# Standard
minikube start --cpus=4

# Heavy computation
minikube start --cpus=8

# Use all available
minikube start --cpus=max
```

### Disk Optimization

```bash
# Minimal (documentation only)
minikube start --disk-size=10g

# Standard
minikube start --disk-size=20g

# Large images/data
minikube start --disk-size=50g
```

---

## Networking Configurations

### Port Exposure

```bash
# Expose specific ports to host (documentation only)
minikube start --ports=80:80,443:443,8080:8080

# With NodePort range extension
minikube start --extra-config=apiserver.service-node-port-range=1-65535
```

### Service CIDR

```bash
# Custom service CIDR (documentation only)
minikube start --service-cluster-ip-range=10.96.0.0/12
```

### DNS Configuration

```bash
# Custom DNS domain (documentation only)
minikube start --dns-domain=cluster.local
```

### Insecure Registry

```bash
# Allow insecure registries (documentation only)
minikube start --insecure-registry="192.168.0.0/16"

# Multiple registries
minikube start --insecure-registry="10.0.0.0/8,192.168.0.0/16"
```

---

## Environment Variables

### Proxy Configuration

```bash
# Set proxy (documentation only)
export HTTP_PROXY=http://proxy.example.com:8080
export HTTPS_PROXY=http://proxy.example.com:8080
export NO_PROXY=localhost,127.0.0.1,10.96.0.0/12,192.168.99.0/24

minikube start
```

### Docker Environment

```bash
# Configure shell to use Minikube's Docker (documentation only)
eval $(minikube docker-env)

# Reset Docker environment
eval $(minikube docker-env --unset)
```

---

## CI/CD Configurations

### GitHub Actions

```yaml
# .github/workflows/test.yml (example configuration)
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Start Minikube
        uses: medyagh/setup-minikube@latest
        with:
          kubernetes-version: v1.29.0
          driver: docker
          cpus: 2
          memory: 4096

      - name: Deploy and Test
        run: |
          kubectl apply -f k8s/
          kubectl wait --for=condition=ready pod -l app=myapp --timeout=120s
```

### GitLab CI

```yaml
# .gitlab-ci.yml (example configuration)
test:
  image: docker:latest
  services:
    - docker:dind
  before_script:
    - curl -LO https://storage.googleapis.com/minikube/releases/latest/minikube-linux-amd64
    - install minikube-linux-amd64 /usr/local/bin/minikube
    - minikube start --driver=docker --cpus=2 --memory=2048
  script:
    - kubectl apply -f k8s/
    - kubectl get pods
```

### Jenkins Pipeline

```groovy
// Jenkinsfile (example configuration)
pipeline {
    agent any
    stages {
        stage('Setup Minikube') {
            steps {
                sh '''
                    minikube start --driver=docker --cpus=2 --memory=2048
                    kubectl cluster-info
                '''
            }
        }
        stage('Deploy') {
            steps {
                sh 'kubectl apply -f k8s/'
            }
        }
    }
    post {
        always {
            sh 'minikube delete'
        }
    }
}
```

---

## Configuration Presets

### Learning Environment

```bash
# Minimal setup for K8s learning (documentation only)
minikube start \
    --driver=docker \
    --kubernetes-version=v1.29.0 \
    --cpus=2 \
    --memory=2048 \
    --addons=dashboard,metrics-server
```

### Development Environment

```bash
# Full-featured dev setup (documentation only)
minikube start \
    --driver=docker \
    --kubernetes-version=v1.29.0 \
    --cpus=4 \
    --memory=4096 \
    --disk-size=20g \
    --addons=ingress,dashboard,metrics-server,storage-provisioner
```

### Helm Chart Development

```bash
# Helm-ready setup (documentation only)
minikube start \
    --driver=docker \
    --kubernetes-version=v1.29.0 \
    --cpus=4 \
    --memory=4096 \
    --disk-size=30g \
    --addons=ingress,storage-provisioner,default-storageclass,metrics-server
```

### Production-Like Testing

```bash
# Multi-node with realistic settings (documentation only)
minikube start \
    --driver=docker \
    --kubernetes-version=v1.29.0 \
    --cpus=2 \
    --memory=4096 \
    --nodes=3 \
    --addons=ingress,metrics-server \
    --extra-config=kubelet.serialize-image-pulls=false
```
