# Minikube Troubleshooting Reference

Comprehensive debugging guide for common Minikube issues.

---

## Diagnostic Commands Quick Reference

All commands in this document are for **documentation and learning purposes only**. This skill does not execute commands.

```bash
# Cluster status overview (documentation only)
minikube status
minikube logs
minikube ssh -- 'dmesg | tail -50'

# Kubernetes component health
kubectl cluster-info
kubectl get componentstatuses
kubectl get nodes -o wide
kubectl get pods -n kube-system

# Resource usage
kubectl top nodes
kubectl top pods -A
kubectl describe nodes
```

---

## Startup Issues

### Cluster Won't Start

#### Symptom: "minikube start" hangs or fails

**Diagnostic Steps:**
```bash
# Check status (documentation only)
minikube status

# View detailed logs
minikube logs --file=minikube-logs.txt

# Check driver status
docker ps  # for docker driver
systemctl status libvirtd  # for kvm2
```

**Common Causes & Solutions:**

| Cause | Diagnosis | Solution |
|-------|-----------|----------|
| Driver not running | `docker ps` fails | Start Docker Desktop/daemon |
| Insufficient resources | Logs show OOM or resource errors | Reduce `--memory` or `--cpus` |
| Corrupted cluster | Previous failed start | `minikube delete && minikube start` |
| Network issues | Timeout pulling images | Check proxy settings, internet |
| Permission denied | Logs show permission errors | Run as admin or fix group membership |

#### Symptom: "Exiting due to GUEST_PROVISION"

```bash
# Clean start (documentation only)
minikube delete --purge
minikube start --driver=docker
```

**Causes:**
- Corrupted VM/container state
- Driver mismatch
- Incomplete previous installation

#### Symptom: "Unable to connect to the server"

```bash
# Verify kubeconfig (documentation only)
kubectl config current-context
kubectl config view

# Reset context
minikube update-context
```

---

### Driver-Specific Issues

#### Docker Driver Issues

**Symptom:** "Cannot connect to the Docker daemon"

```bash
# Check Docker status (documentation only)
docker info
systemctl status docker  # Linux
```

**Solutions:**
- Start Docker Desktop (macOS/Windows)
- Start Docker service: `sudo systemctl start docker`
- Add user to docker group: `sudo usermod -aG docker $USER`
- Log out and back in for group changes

**Symptom:** "docker: Error response from daemon"

```bash
# Reset Docker (documentation only)
docker system prune -a
minikube delete
minikube start --driver=docker
```

#### Hyper-V Driver Issues (Windows)

**Symptom:** "Hyper-V is not available"

**Solutions:**
- Enable Hyper-V in Windows Features
- Verify Windows edition (Pro/Enterprise required)
- Disable VirtualBox if installed (conflicts)
- Run PowerShell as Administrator

**Symptom:** "Default Switch not found"

```bash
# Create virtual switch (PowerShell Admin, documentation only)
New-VMSwitch -Name "Minikube" -SwitchType Internal
minikube start --driver=hyperv --hyperv-virtual-switch="Minikube"
```

#### VirtualBox Driver Issues

**Symptom:** "VBoxManage not found"

**Solutions:**
- Install VirtualBox
- Add VirtualBox to PATH
- Verify installation: `VBoxManage --version`

**Symptom:** "VT-x is not available"

**Solutions:**
- Enable virtualization in BIOS/UEFI
- Disable Hyper-V on Windows (conflicts)
- Check: `egrep -c '(vmx|svm)' /proc/cpuinfo` (Linux)

---

## Networking Issues

### Services Not Accessible

#### Symptom: Cannot reach services from host

**Diagnostic Steps:**
```bash
# Check service status (documentation only)
kubectl get svc
kubectl get endpoints
minikube service list

# Get Minikube IP
minikube ip
```

**Solutions by Service Type:**

| Service Type | Access Method |
|--------------|---------------|
| ClusterIP | `kubectl port-forward svc/name 8080:80` |
| NodePort | `minikube service name --url` |
| LoadBalancer | `minikube tunnel` (separate terminal) |
| Ingress | Enable ingress addon, configure /etc/hosts |

#### Symptom: LoadBalancer stuck on "pending"

```bash
# Start tunnel (documentation only)
minikube tunnel

# In another terminal, check service
kubectl get svc
# EXTERNAL-IP should now have an IP
```

**Note:** `minikube tunnel` must run continuously.

### Ingress Issues

#### Symptom: Ingress not working

**Diagnostic Steps:**
```bash
# Verify addon enabled (documentation only)
minikube addons list | grep ingress

# Check ingress controller
kubectl get pods -n ingress-nginx
kubectl get ingress

# Get ingress address
kubectl get ingress -o wide
```

**Common Issues:**

| Issue | Solution |
|-------|----------|
| Addon not enabled | `minikube addons enable ingress` |
| Controller not ready | Wait, check logs: `kubectl logs -n ingress-nginx -l app.kubernetes.io/name=ingress-nginx` |
| Wrong host header | Add entry to /etc/hosts with `minikube ip` |
| Ingress class missing | Add `ingressClassName: nginx` to Ingress spec |

#### Symptom: DNS resolution fails in cluster

```bash
# Test DNS (documentation only)
kubectl run -it --rm debug --image=busybox --restart=Never -- nslookup kubernetes.default

# Check CoreDNS
kubectl get pods -n kube-system -l k8s-app=kube-dns
kubectl logs -n kube-system -l k8s-app=kube-dns
```

---

## Pod Issues

### Pods Stuck in Pending

**Diagnostic Steps:**
```bash
# Describe pod for events (documentation only)
kubectl describe pod <pod-name>
kubectl get events --sort-by=.metadata.creationTimestamp

# Check node resources
kubectl describe nodes
kubectl top nodes
```

**Common Causes:**

| Cause | Events/Symptoms | Solution |
|-------|-----------------|----------|
| Insufficient CPU | "Insufficient cpu" | Increase minikube `--cpus` |
| Insufficient memory | "Insufficient memory" | Increase minikube `--memory` |
| No PV available | "no persistent volumes available" | Enable storage-provisioner addon |
| Node not ready | "0/1 nodes are available" | Check node status, restart minikube |
| Taint/toleration | "node(s) had taints" | Add tolerations or remove taints |

### Pods Stuck in ImagePullBackOff

**Diagnostic Steps:**
```bash
# Check pod events (documentation only)
kubectl describe pod <pod-name>

# Check image availability
kubectl get events | grep -i pull
```

**Common Causes:**

| Cause | Solution |
|-------|----------|
| Image not found | Verify image name and tag |
| Private registry | Add imagePullSecrets |
| Network issues | Check minikube network, proxy settings |
| Rate limiting | Use authenticated pull, local registry |

**Using Local Images:**
```bash
# Point shell to minikube's Docker (documentation only)
eval $(minikube docker-env)

# Build image inside minikube
docker build -t myapp:local .

# Use imagePullPolicy: Never in pod spec
```

### Pods Stuck in CrashLoopBackOff

**Diagnostic Steps:**
```bash
# Check logs (documentation only)
kubectl logs <pod-name>
kubectl logs <pod-name> --previous

# Check container command
kubectl describe pod <pod-name>
```

**Common Causes:**

| Cause | Symptoms | Solution |
|-------|----------|----------|
| Application error | Error in logs | Fix application code |
| Missing config | "file not found", "env not set" | Check ConfigMaps, Secrets, env vars |
| Resource limits | OOMKilled | Increase memory limits |
| Readiness probe | Probe fails | Fix probe configuration |
| Entrypoint issues | Exits immediately | Check CMD/ENTRYPOINT |

---

## Storage Issues

### PVC Stuck in Pending

**Diagnostic Steps:**
```bash
# Check PVC status (documentation only)
kubectl get pvc
kubectl describe pvc <pvc-name>

# Check storage class
kubectl get sc
kubectl describe sc standard
```

**Solutions:**

```bash
# Enable storage provisioner (documentation only)
minikube addons enable storage-provisioner
minikube addons enable default-storageclass

# Verify
kubectl get sc
# Should show 'standard' with PROVISIONER 'k8s.io/minikube-hostpath'
```

### PV Access Issues

**Symptom:** Permission denied writing to mounted volume

**Solutions:**
- Check `securityContext` in pod spec
- Use `fsGroup` to set group ownership
- For hostPath: check host directory permissions

```yaml
# Example securityContext (documentation)
spec:
  securityContext:
    fsGroup: 1000
  containers:
  - name: app
    securityContext:
      runAsUser: 1000
```

---

## Performance Issues

### Slow Cluster Performance

**Diagnostic Steps:**
```bash
# Check resource usage (documentation only)
kubectl top nodes
kubectl top pods -A
minikube ssh -- 'free -h && df -h'
```

**Optimization Strategies:**

| Issue | Solution |
|-------|----------|
| Low memory | Increase `--memory`, reduce workloads |
| CPU bottleneck | Increase `--cpus` |
| Disk I/O | Use SSD, increase `--disk-size` |
| Too many pods | Scale down replicas |
| Large images | Use slim/alpine images |

### Slow Image Pulls

**Solutions:**
```bash
# Use local registry (documentation only)
minikube addons enable registry

# Pre-load images
minikube image load myapp:latest

# Use image caching
minikube cache add nginx:latest
```

---

## Addon Issues

### Addon Won't Enable

**Diagnostic Steps:**
```bash
# Check addon status (documentation only)
minikube addons list
minikube addons enable <addon> -v=7  # verbose
```

**Common Issues:**

| Addon | Issue | Solution |
|-------|-------|----------|
| ingress | Pods not starting | Check resources, wait longer |
| dashboard | Can't access | Use `minikube dashboard` command |
| metrics-server | No metrics | Wait for startup, check logs |
| registry | Connection refused | Check port, use `minikube service` |

### Dashboard Won't Load

```bash
# Access dashboard (documentation only)
minikube dashboard

# Or get URL
minikube dashboard --url

# Check dashboard pod
kubectl get pods -n kubernetes-dashboard
```

---

## Cleanup and Recovery

### Full Reset

```bash
# Delete cluster and cache (documentation only)
minikube delete --purge

# Remove all profiles
minikube delete --all --purge

# Clear kubectl context
kubectl config delete-context minikube
kubectl config delete-cluster minikube
```

### Partial Recovery

```bash
# Restart cluster without deleting (documentation only)
minikube stop
minikube start

# Restart specific component
minikube ssh -- 'sudo systemctl restart kubelet'
```

### Cache Issues

```bash
# Clear image cache (documentation only)
minikube cache delete --all

# Clear download cache
rm -rf ~/.minikube/cache
```

---

## Logs and Debugging

### Collecting Logs

```bash
# Minikube logs (documentation only)
minikube logs > minikube.log
minikube logs --problems  # show only problems

# System pods logs
kubectl logs -n kube-system -l component=kube-apiserver
kubectl logs -n kube-system -l component=kube-scheduler
kubectl logs -n kube-system -l component=kube-controller-manager
kubectl logs -n kube-system -l k8s-app=kube-dns
```

### SSH into Node

```bash
# SSH access (documentation only)
minikube ssh

# Run command directly
minikube ssh -- 'ls -la /var/log'
minikube ssh -- 'sudo journalctl -u kubelet'
```

### Debug Container

```bash
# Run debug container (documentation only)
kubectl run debug --rm -it --image=busybox --restart=Never -- sh

# Debug with networking tools
kubectl run debug --rm -it --image=nicolaka/netshoot --restart=Never -- bash
```

---

## Error Message Reference

### Quick Lookup Table

| Error | Likely Cause | Quick Fix |
|-------|--------------|-----------|
| "machine does not exist" | Deleted or corrupted | `minikube delete && minikube start` |
| "kubeconfig not found" | Context not set | `minikube update-context` |
| "connection refused" | API server down | `minikube stop && minikube start` |
| "unable to upgrade connection" | kubectl version mismatch | Update kubectl |
| "no space left on device" | Disk full | Increase `--disk-size`, prune images |
| "unable to resolve host" | DNS issues | Check network, proxy settings |
| "ImagePullBackOff" | Can't pull image | Check image name, registry access |
| "CrashLoopBackOff" | Container crashing | Check `kubectl logs` |
| "Pending" | Resources/config issue | `kubectl describe` for details |
| "OOMKilled" | Out of memory | Increase limits or minikube memory |

---

## Getting Help

### Useful Resources

- **Minikube GitHub Issues:** https://github.com/kubernetes/minikube/issues
- **Minikube Documentation:** https://minikube.sigs.k8s.io/docs/
- **Kubernetes Slack:** #minikube channel
- **Stack Overflow:** Tag: minikube

### Reporting Issues

When reporting issues, include:
```bash
# Collect diagnostic info (documentation only)
minikube version
minikube status
minikube logs --file=minikube-diag.log
kubectl version
uname -a  # or systeminfo on Windows
```
