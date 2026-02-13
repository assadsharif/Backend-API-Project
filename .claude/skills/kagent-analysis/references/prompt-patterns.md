# kagent Prompt Patterns Reference

Comprehensive prompt patterns for AI-assisted Kubernetes cluster analysis.

---

## Prompt Structure

### Basic Pattern

```
kagent <action> <resource-type> [--flags] [--namespace ns]
```

### Common Actions

| Action | Purpose |
|--------|---------|
| `analyze` | Assess current state and identify issues |
| `recommend` | Generate optimization suggestions |
| `validate` | Check against best practices |
| `explain` | Provide educational context |
| `compare` | Compare configurations or states |
| `predict` | Estimate impact of changes |

---

## Cluster-Level Analysis

### Overall Health

```
# Comprehensive cluster health check
kagent analyze cluster --health

# Quick status summary
kagent analyze cluster --summary

# Detailed component analysis
kagent analyze cluster --components --detailed

# Historical health trend
kagent analyze cluster --health --period 7d
```

### Control Plane Analysis

```
# Control plane health
kagent analyze control-plane

# API server performance
kagent analyze api-server --latency --errors

# etcd health and performance
kagent analyze etcd --health --latency

# Scheduler efficiency
kagent analyze scheduler --queue-depth --latency
```

### Node Analysis

```
# All nodes overview
kagent analyze nodes --all

# Node resource pressure
kagent analyze nodes --pressure

# Node conditions
kagent analyze nodes --conditions

# Specific node deep-dive
kagent analyze node minikube --detailed

# Node capacity planning
kagent analyze nodes --capacity --forecast
```

---

## Resource Analysis

### Utilization Analysis

```
# Cluster-wide utilization
kagent analyze utilization --cluster

# Namespace utilization
kagent analyze utilization --namespace myapp

# Utilization by resource type
kagent analyze utilization --type cpu
kagent analyze utilization --type memory
kagent analyze utilization --type storage

# Utilization over time
kagent analyze utilization --namespace myapp --period 24h --interval 1h
```

### Efficiency Analysis

```
# Resource waste detection
kagent analyze waste --namespace myapp

# Over-provisioned resources
kagent analyze waste --threshold 50 --type cpu

# Under-utilized workloads
kagent analyze efficiency --below 30

# Resource right-sizing candidates
kagent analyze sizing-candidates --namespace myapp
```

### Quota and Limits

```
# Resource quota analysis
kagent analyze quotas --namespace myapp

# Limit range validation
kagent analyze limits --namespace myapp

# Quota utilization percentage
kagent analyze quota-usage --namespace myapp --warn-threshold 80
```

---

## Workload Analysis

### Deployment Analysis

```
# Deployment health
kagent analyze deployment backend --namespace myapp

# Replica efficiency
kagent analyze deployment backend --replicas --utilization

# Rollout analysis
kagent analyze deployment backend --rollout-history

# All deployments in namespace
kagent analyze deployments --namespace myapp --summary
```

### Pod Analysis

```
# Pod resource efficiency
kagent analyze pod backend-abc --resources

# Pod restart analysis
kagent analyze pods --restarts --namespace myapp

# Pod lifecycle analysis
kagent analyze pods --lifecycle --namespace myapp

# Long-running pods
kagent analyze pods --age --older-than 7d
```

### Container Analysis

```
# Container resource usage
kagent analyze containers --namespace myapp

# Container image analysis
kagent analyze images --namespace myapp --size

# Container security
kagent analyze containers --security --namespace myapp
```

---

## Performance Analysis

### Latency Analysis

```
# Service latency
kagent analyze latency --service backend --namespace myapp

# P50/P95/P99 latency breakdown
kagent analyze latency --percentiles --service backend

# Latency trends
kagent analyze latency --trend --period 24h
```

### Throughput Analysis

```
# Request throughput
kagent analyze throughput --service backend

# Throughput capacity
kagent analyze throughput --capacity --service backend

# Traffic patterns
kagent analyze traffic --patterns --namespace myapp
```

### Bottleneck Detection

```
# Identify bottlenecks
kagent analyze bottlenecks --namespace myapp

# CPU bottlenecks
kagent analyze bottlenecks --type cpu

# Memory bottlenecks
kagent analyze bottlenecks --type memory

# Network bottlenecks
kagent analyze bottlenecks --type network

# Top bottlenecks
kagent analyze bottlenecks --top 5 --detailed
```

---

## Configuration Analysis

### Best Practices

```
# Best practices audit
kagent analyze best-practices --namespace myapp

# Specific best practice categories
kagent analyze best-practices --category security
kagent analyze best-practices --category reliability
kagent analyze best-practices --category efficiency

# Strict validation mode
kagent analyze best-practices --strict --fail-on-warning
```

### Security Analysis

```
# Security posture
kagent analyze security --namespace myapp

# RBAC analysis
kagent analyze rbac --namespace myapp

# Pod security standards
kagent analyze pod-security --namespace myapp

# Network policy coverage
kagent analyze network-security --namespace myapp

# Secret management
kagent analyze secrets --namespace myapp --hygiene
```

### Configuration Drift

```
# Detect configuration drift
kagent analyze drift --namespace myapp

# Compare with Helm values
kagent analyze drift --compare-helm myapp

# Configuration consistency
kagent analyze consistency --namespace myapp
```

---

## Scaling Analysis

### Horizontal Scaling

```
# HPA effectiveness
kagent analyze hpa --namespace myapp

# Scaling events analysis
kagent analyze scaling-events --namespace myapp --period 24h

# Scaling recommendation
kagent analyze scaling --deployment backend --recommend

# Multi-metric HPA analysis
kagent analyze hpa backend --metrics-breakdown
```

### Vertical Scaling

```
# VPA recommendations
kagent analyze vpa-candidates --namespace myapp

# Resource sizing analysis
kagent analyze sizing --deployment backend --period 7d

# Memory/CPU ratio analysis
kagent analyze resource-ratio --namespace myapp
```

---

## Network Analysis

### Service Analysis

```
# Service connectivity
kagent analyze services --namespace myapp --connectivity

# Service mesh analysis
kagent analyze service-mesh --namespace myapp

# Load balancing efficiency
kagent analyze load-balancing --service backend
```

### DNS Analysis

```
# DNS performance
kagent analyze dns --namespace myapp

# DNS resolution patterns
kagent analyze dns --resolution-patterns

# DNS errors
kagent analyze dns --errors --period 1h
```

### Network Policy Analysis

```
# Policy coverage
kagent analyze network-policies --namespace myapp

# Traffic flow analysis
kagent analyze traffic-flows --namespace myapp

# Policy conflicts
kagent analyze network-policies --conflicts
```

---

## Storage Analysis

### PVC Analysis

```
# PVC utilization
kagent analyze pvc --namespace myapp --utilization

# PVC growth trends
kagent analyze pvc --growth --period 30d

# Unused PVCs
kagent analyze pvc --unused --namespace myapp
```

### Storage Class Analysis

```
# Storage class performance
kagent analyze storage-class standard --performance

# Provisioner health
kagent analyze storage-provisioner
```

---

## Cost Analysis (Educational)

### Resource Cost Estimation

```
# Estimated resource costs
kagent analyze cost --namespace myapp --educational

# Cost optimization opportunities
kagent analyze cost-optimization --namespace myapp

# Cost by workload
kagent analyze cost --breakdown workload --namespace myapp
```

### Efficiency Scoring

```
# Resource efficiency score
kagent analyze efficiency-score --namespace myapp

# Efficiency trends
kagent analyze efficiency --trend --period 30d
```

---

## Comparison Patterns

### Configuration Comparison

```
# Compare namespaces
kagent compare namespaces myapp-dev myapp-staging

# Compare deployments
kagent compare deployments backend frontend --namespace myapp

# Compare time periods
kagent compare --period "last-week" "this-week" --namespace myapp
```

### Benchmark Comparison

```
# Compare against benchmarks
kagent compare --benchmark production-baseline --namespace myapp

# Compare against best practices
kagent compare --best-practices --namespace myapp
```

---

## Recommendation Patterns

### Resource Recommendations

```
# Right-sizing recommendations
kagent recommend sizing --namespace myapp

# Conservative recommendations
kagent recommend sizing --namespace myapp --conservative

# Aggressive optimization
kagent recommend sizing --namespace myapp --aggressive

# Specific workload
kagent recommend sizing --deployment backend --namespace myapp
```

### Scaling Recommendations

```
# Scaling recommendations
kagent recommend scaling --namespace myapp

# HPA configuration
kagent recommend hpa --deployment backend --namespace myapp

# Replica count
kagent recommend replicas --deployment backend
```

### Configuration Recommendations

```
# Best practice recommendations
kagent recommend config --namespace myapp

# Security improvements
kagent recommend security --namespace myapp

# Reliability improvements
kagent recommend reliability --namespace myapp
```

---

## Validation Patterns

### Pre-Deployment Validation

```
# Validate Helm values
kagent validate values ./values.yaml

# Validate against cluster capacity
kagent validate capacity --values ./values.yaml

# Validate best practices
kagent validate best-practices --chart ./myapp
```

### Post-Deployment Validation

```
# Validate deployment health
kagent validate deployment backend --namespace myapp

# Validate against spec
kagent validate --against-spec ./spec.md --namespace myapp
```

---

## Explanation Patterns

### Concept Explanations

```
# Explain resource concept
kagent explain resources --concept requests-vs-limits

# Explain scaling
kagent explain scaling --concept hpa-vs-vpa

# Explain recommendation
kagent explain recommendation --id rec-123
```

### Analysis Explanations

```
# Explain analysis result
kagent explain analysis --last

# Explain metric
kagent explain metric cpu-throttling

# Explain anomaly
kagent explain anomaly --id anom-456
```

---

## Output Formats

### Format Options

```
# JSON output
kagent analyze cluster --output json

# YAML output
kagent analyze cluster --output yaml

# Table format
kagent analyze cluster --output table

# Markdown report
kagent analyze cluster --output markdown --report
```

### Verbosity Levels

```
# Summary only
kagent analyze cluster --summary

# Normal detail
kagent analyze cluster

# Detailed output
kagent analyze cluster --detailed

# Debug level
kagent analyze cluster --verbose
```

---

## Time-Based Patterns

### Time Range Specification

```
# Last hour
kagent analyze --period 1h

# Last 24 hours
kagent analyze --period 24h

# Last 7 days
kagent analyze --period 7d

# Custom range
kagent analyze --from "2024-01-01" --to "2024-01-07"
```

### Trend Analysis

```
# Show trend
kagent analyze utilization --trend --period 7d

# Compare periods
kagent analyze --compare-period "last-week"

# Forecast
kagent analyze --forecast --period 7d
```

---

## Quick Reference

| Analysis Type | kagent Command |
|---------------|----------------|
| Cluster health | `kagent analyze cluster --health` |
| Resource usage | `kagent analyze utilization --namespace X` |
| Waste detection | `kagent analyze waste --namespace X` |
| Best practices | `kagent analyze best-practices --namespace X` |
| Performance | `kagent analyze performance --namespace X` |
| Right-sizing | `kagent recommend sizing --namespace X` |
| Security | `kagent analyze security --namespace X` |
| Scaling | `kagent recommend scaling --deployment X` |
