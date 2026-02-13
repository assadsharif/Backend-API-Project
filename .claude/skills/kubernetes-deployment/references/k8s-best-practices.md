# Kubernetes Deployment Best Practices

Reference for this skill's generation defaults and validation rules.

---

## Resource Requests / Limits

- **Always set both requests AND limits** for production workloads.
  - Requests → scheduler placement decisions.
  - Limits → hard caps enforced by kubelet.
- Omitting limits = unbounded consumption. Omitting requests = scheduler guesses.

### Recommended Starting Points

| Workload Type | CPU Request | CPU Limit | Mem Request | Mem Limit |
|---------------|-------------|-----------|-------------|-----------|
| Lightweight web | 100m | 200m | 128Mi | 256Mi |
| Mid-tier API | 250m | 500m | 256Mi | 512Mi |
| Data processing | 500m | 1000m | 512Mi | 1Gi |

- CPU: `100m` = 0.1 core. Millicores (`Nm`) preferred for values < 1 core.
- Memory: Limit should be ≥ 2× request as a starting point.

---

## Replica Strategy

- Minimum **2 replicas** for any production-facing service (HA against single-pod failure).
- Use HPA (Horizontal Pod Autoscaler) for variable load — **out of scope** for this skill.
- `replicas: 0` is invalid in this skill (use `kubectl scale` for manual scale-down).

---

## Label Conventions

Labels applied by this skill to every resource:

| Label | Value | Purpose |
|-------|-------|---------|
| `app` | `{app_name}` | Selector target — unique per Deployment |
| `app.kubernetes.io/name` | `{app_name}` | Kubernetes recommended label |
| `app.kubernetes.io/managed-by` | `k8s-deployment-skill` | Tooling provenance |

Custom labels provided via `labels` dict merge on top of these defaults.
**Do not override `app`** — it is the selector anchor.

---

## Service Type Selection

| Type | Use When |
|------|----------|
| `ClusterIP` | Service is internal-only (default, recommended baseline) |
| `NodePort` | Dev/test access from outside the cluster without cloud LB |
| `LoadBalancer` | Production external exposure (requires cloud provider support) |

---

## ConfigMap vs Secrets

| Resource | For |
|----------|-----|
| ConfigMap | Non-sensitive config: ports, feature flags, app settings |
| Secret | Sensitive data: passwords, API keys, TLS certs |

**This skill generates ConfigMaps only.** Never place secrets in `env_vars` or ConfigMap data.

---

## Port Naming

- Names must be **DNS-1123 labels**: lowercase, `[a-z0-9-]`, max 15 chars, start/end alphanumeric.
- Service port names **must match** corresponding container port names for consistent routing.
- Common conventions: `http` (80), `https` (443), `grpc` (50051).

---

## Namespace Guidelines

- `default` namespace is acceptable for development/testing only.
- Production workloads should use dedicated namespaces (e.g. `production`, `staging`).
- This skill parameterizes namespace; it defaults to `"default"` but callers should set explicitly for production.

---

## Anti-Patterns (enforced or warned)

| Anti-Pattern | Impact | Enforcement |
|--------------|--------|-------------|
| Only limits, no requests | Scheduler cannot place pods | Caller responsibility (warnings in best-practices) |
| Image tag `latest` | Unpredictable, breaks rollback | Not enforced — caller responsibility |
| Secrets in ConfigMap/env | Credential exposure | Documented; skill does not generate Secrets |
| `replicas: 0` | Pod never runs | Rejected by schema (`ge=1`) |
| Non-DNS-1123 names | Kubernetes rejects manifest | Rejected by Pydantic validators |
| Missing selector ↔ template label alignment | Pod never matches selector | Checked by `validate_manifest` |
