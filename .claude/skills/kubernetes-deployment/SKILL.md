---
name: kubernetes-deployment
description: |
  Generates Kubernetes Deployment, Service, and ConfigMap manifests from typed
  Pydantic v2 schemas. Use when creating, composing, or validating Kubernetes
  deployment artifacts. Triggers on: "Kubernetes manifest", "Deployment YAML",
  "k8s service", "generate configmap", "deploy to kubernetes".
  Supports replicas, ports, env vars, resources, labels, full-stack generation.
  Output is deterministic YAML.
---

# Kubernetes Deployment

Builder skill. Generates validated Kubernetes manifests from Pydantic v2 input schemas. Deterministic — same input always produces same YAML.

## Scope

**Does**: Generate Deployment, Service, ConfigMap manifests. Validate manifest structure. Compose full stacks with auto-derivation.

**Does NOT**: Apply manifests (`kubectl apply`). Handle Helm charts, Ingress, RBAC, PVCs, Secrets, HPA, or CronJobs.

---

## Tool Map

| Function | Input | Output | Description |
|----------|-------|--------|-------------|
| `generate_deployment` | `DeploymentInput` | `ManifestOutput` | apps/v1 Deployment YAML |
| `generate_service` | `ServiceInput` | `ManifestOutput` | v1 Service YAML |
| `generate_configmap` | `ConfigMapInput` | `ManifestOutput` | v1 ConfigMap YAML |
| `generate_stack` | `StackInput` | `List[ManifestOutput]` | Deployment + Service + ConfigMap |
| `validate_manifest` | YAML string | `ValidationResult` | Structural validation |

---

## Clarification Triggers

Before generating, infer from context where possible:
- **app_name**: Derive from project or repo name if available
- **namespace**: Default `"default"` unless production context is detected
- **service_type**: Default `ClusterIP` unless external access is needed

### Required
1. **Image** — container image with tag (e.g. `nginx:1.25`). Never omit.
2. **Manifest type** — single resource or full stack?

### Optional
3. **Resources** — CPU/memory requests and limits? Recommend for any non-dev workload.
4. **Service type** — `ClusterIP` | `NodePort` | `LoadBalancer`?
5. **Env vars / ConfigMap** — environment variables to inject?

---

## Key Behaviors

- `generate_stack` auto-derives Service from `ports` and ConfigMap from `env_vars` when sub-inputs are omitted.
- All `app_name` fields validated as DNS-1123 labels (lowercase, alphanumeric + hyphens, max 63 chars).
- Port names: DNS-1123 labels (max 15 chars) — required for Service port matching.
- Labels `app`, `app.kubernetes.io/name`, `app.kubernetes.io/managed-by` always applied. Custom labels merge on top; `app` label is the selector anchor and must not be overridden.
- CPU: `Nm` (millicores) or decimal. Memory: `N[Ki|Mi|Gi|Ti]`.
- Naming: Service → `{app_name}-svc`, ConfigMap → `{app_name}-config`.

---

## Must Follow

- [ ] All inputs validated via Pydantic v2 before generation runs
- [ ] `app_name` DNS-1123 compliant (lowercase, alphanumeric, hyphens, ≤63 chars)
- [ ] Port names DNS-1123 labels (≤15 chars)
- [ ] `replicas` ≥ 1
- [ ] `selector.matchLabels` ⊆ `template.metadata.labels`
- [ ] Service spec: at least one port
- [ ] ConfigMap data: at least one key-value pair

## Must Avoid

- Hardcoding namespace (always parameterized; default = `"default"`)
- Secrets in env_vars or ConfigMap data (use Kubernetes Secrets — out of scope)
- Non-deterministic output (no timestamps, UUIDs, random values)
- Image tag `latest` in production (see `references/k8s-best-practices.md`)

---

## Error Handling

- **Invalid DNS-1123 name** → Pydantic `ValidationError` with field name and constraint details
- **Bad CPU/memory format** → Error with expected pattern (e.g. `100m`, `256Mi`)
- **replicas < 1** → Rejected by schema constraint (`ge=1`)
- **Missing required fields** → Caught at Pydantic boundary; generation never runs on invalid input
- **validate_manifest** → Returns `errors` and `warnings` arrays; never throws for parseable YAML input

---

## Dependencies

- PyYAML ≥ 6.0
- Pydantic ≥ 2.0
- MCP server: `k8s_deployment_mcp` (`src/mcp_servers/k8s_deployment_mcp.py`)

---

## References

| Resource | URL / Path | When to Read |
|----------|------------|--------------|
| K8s API Reference | https://kubernetes.io/docs/reference/kubernetes-api/ | Field-level spec definitions |
| Deployments | https://kubernetes.io/docs/concepts/workloads/controllers/deployment/ | Deployment patterns |
| Services | https://kubernetes.io/docs/concepts/services-networking/service/ | Service type selection |
| Resource mgmt | https://kubernetes.io/docs/concepts/configuration/manage-resources-containers/ | CPU/memory sizing |
| Best practices | `references/k8s-best-practices.md` | Production sizing, anti-patterns, label conventions |
| Schemas | `models.py` | All Pydantic v2 input/output models |
| Logic | `skill.py` | Generation and validation functions |

For patterns not covered here, fetch from the K8s API reference link above.

---

## Keeping Current

- Check https://kubernetes.io/docs/reference/kubernetes-api/ for new API fields
- Monitor https://kubernetes.io/docs/concepts/overview/versions/ for API version deprecations
- Last verified: 2025-01
