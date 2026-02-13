---
name: helm-packaging
description: Package applications into Helm charts for repeatable, parameterized Kubernetes deployments. Use when creating Helm charts, parameterizing deployments, or explaining chart structures. Triggers on requests involving Helm chart creation, values.yaml configuration, or Kubernetes deployment packaging.
---

# Helm Packaging Skill

Package applications into Helm charts for repeatable, parameterized Kubernetes deployments.

## Purpose

Enable generation of production-ready Helm charts that:
- Provide consistent, repeatable deployments
- Parameterize all environment-specific values
- Follow Helm best practices and conventions
- Deploy cleanly on Minikube and production clusters

---

## When to Use This Skill

**Use this skill when:**
- Creating Helm charts for new applications
- Packaging existing Kubernetes deployments as charts
- Parameterizing deployments for multiple environments
- Learning Helm chart structure and best practices
- Preparing applications for Minikube or production deployment

**Do NOT use this skill when:**
- Creating Dockerfiles (use docker-containerization)
- Setting up Kubernetes cluster (use minikube-cluster)
- Debugging deployed applications (use kubectl-ai)
- Analyzing cluster performance (use kagent-analysis)
- Deploying charts (charts are generated, not installed)

---

## Required Clarifications

Before generating output, clarify these with the user:

### Mandatory Clarifications

1. **What components does your application have?** (backend, frontend, worker, etc.)
2. **What container images are available?** (registry/image:tag format)
3. **What ports need to be exposed?** (internal and external)

### Optional Clarifications (if relevant)

4. **Ingress required?** (external HTTP access needed?)
5. **Persistent storage needed?** (databases, file storage)
6. **Environment-specific configurations?** (dev vs prod differences)
7. **Autoscaling requirements?** (HPA configuration)

---

## Version Compatibility

| Component | Supported Versions | Notes |
|-----------|-------------------|-------|
| Helm | 3.10+ | Tiller-less, API v2 |
| Kubernetes | 1.25 - 1.30 | Chart kubeVersion field |
| Chart API | v2 | apiVersion: v2 |

### Chart.yaml apiVersion

| apiVersion | Helm Version | Features |
|------------|--------------|----------|
| v2 | Helm 3.x | Dependencies in Chart.yaml, library charts |
| v1 | Helm 2.x (deprecated) | requirements.yaml for deps |

---

## Inputs

### Required Inputs

| Input | Type | Description |
|-------|------|-------------|
| `application_name` | String | Name of the application (lowercase, hyphenated) |
| `components` | Array | Application components (backend, frontend, worker, etc.) |
| `container_images` | Object | Image references for each component |

### Optional Inputs

| Input | Type | Default | Description |
|-------|------|---------|-------------|
| `service_exposure` | Object | `{}` | Service types and ports per component |
| `resource_constraints` | Object | `{}` | CPU/memory limits and requests |
| `environment_config` | Object | `{}` | Environment variables and secrets |
| `persistence` | Object | `{}` | PVC requirements |
| `ingress` | Object | `null` | Ingress configuration |
| `replicas` | Object | `{default: 1}` | Replica counts per component |
| `health_checks` | Object | `{}` | Liveness/readiness probes |

---

## Outputs

### Primary Outputs

1. **Helm Chart Structure** - Complete directory layout with all required files
2. **values.yaml Schema** - Fully parameterized configuration with documented defaults
3. **Template Responsibility Mapping** - Which template handles which concern

---

## Allowed Actions

- Generate Helm chart YAML files (as documentation)
- Parameterize deployment values via values.yaml
- Explain chart behavior and template rendering
- Document chart structure and conventions
- Generate template files (deployment, service, ingress, etc.)
- Suggest values.yaml overrides for different environments
- Explain Helm lifecycle hooks
- Document upgrade and rollback strategies
- Generate chart dependencies configuration

---

## Forbidden Actions

- Executing `helm install/upgrade/delete` commands
- Writing ad-hoc Kubernetes YAML outside chart structure
- Hardcoding environment-specific values in templates
- Bypassing Helm lifecycle (direct kubectl apply)
- Creating multiple charts for single application
- Placing configuration outside values.yaml
- Generating charts that won't work on Minikube

---

## Constraints

### One Chart Per Application (MANDATORY)
- All components packaged in single chart
- Use subcharts only for external dependencies
- Maintain cohesive deployment unit

### values.yaml Is the Only Config Surface
- All customizable values in values.yaml
- No hardcoded values in templates
- Environment-specific via values files (values-dev.yaml, values-prod.yaml)
- Secrets referenced, never embedded

### Minikube Compatibility Required
- Must deploy on standard Minikube cluster
- Respect local resource constraints
- Support NodePort/Ingress exposure
- Work with hostPath storage class

---

## Chart Structure

### Standard Directory Layout

```
myapp/
├── Chart.yaml              # Chart metadata
├── Chart.lock              # Dependency lock file (if deps exist)
├── values.yaml             # Default configuration values
├── values.schema.json      # JSON schema for values (optional)
├── .helmignore             # Files to ignore when packaging
├── templates/
│   ├── NOTES.txt           # Post-install instructions
│   ├── _helpers.tpl        # Template helpers and partials
│   ├── deployment.yaml     # Deployment resource(s)
│   ├── service.yaml        # Service resource(s)
│   ├── ingress.yaml        # Ingress resource (if enabled)
│   ├── configmap.yaml      # ConfigMap resource(s)
│   ├── secret.yaml         # Secret resource(s)
│   ├── pvc.yaml            # PersistentVolumeClaim(s)
│   ├── hpa.yaml            # HorizontalPodAutoscaler (if enabled)
│   └── serviceaccount.yaml # ServiceAccount (if enabled)
└── charts/                 # Subcharts directory (if deps exist)
```

> **Full templates**: See [references/template-examples.md](references/template-examples.md)

---

## Template Responsibility Mapping

| Template | Responsibility | Key Values |
|----------|----------------|------------|
| `_helpers.tpl` | Naming conventions, labels, selectors | `nameOverride`, `fullnameOverride` |
| `deployment.yaml` | Pod specification, containers, probes | `*.image`, `*.resources`, `*.env` |
| `service.yaml` | Service exposure, port mapping | `*.service.type`, `*.service.port` |
| `ingress.yaml` | HTTP routing, TLS termination | `ingress.*` |
| `configmap.yaml` | Non-sensitive configuration | `configMap.data` |
| `secret.yaml` | Sensitive data references | `externalSecrets.*` |
| `pvc.yaml` | Persistent storage claims | `persistence.*` |
| `hpa.yaml` | Auto-scaling rules | `autoscaling.*` |
| `serviceaccount.yaml` | RBAC identity | `serviceAccount.*` |
| `NOTES.txt` | Post-install user guidance | All (read-only) |

---

## Parameterization Principles

### DO: Parameterize These

- Image repository, tag, pull policy
- Resource requests and limits
- Replica counts
- Environment variables
- Service type and ports
- Ingress hosts and paths

### DON'T: Hardcode These

- Image tags (use `.Values.*.image.tag`)
- Replica counts (use `.Values.*.replicaCount`)
- Resource values (use `.Values.*.resources.*`)
- Database URLs or secrets (use secrets references)

> **Full templates**: See [references/values-yaml-template.md](references/values-yaml-template.md)

---

## Environment-Specific Values

Use separate values files for each environment:

| File | Purpose | Resources |
|------|---------|-----------|
| `values.yaml` | Base defaults (dev-friendly) | Minimal |
| `values-dev.yaml` | Development/Minikube | Single replica, small resources |
| `values-staging.yaml` | Staging | 2 replicas, moderate resources |
| `values-prod.yaml` | Production | 3+ replicas, HPA, TLS |

> **Full examples**: See [references/environment-values.md](references/environment-values.md)

---

## Validation Checklist

### Chart Structure
- [ ] Chart.yaml has valid apiVersion: v2
- [ ] Chart.yaml has name, version, appVersion
- [ ] values.yaml has all configurable values
- [ ] _helpers.tpl defines all name templates
- [ ] NOTES.txt provides useful post-install info

### Templates
- [ ] All hardcoded values moved to values.yaml
- [ ] Labels use helper templates consistently
- [ ] Resources use `.Values.*.resources`
- [ ] Images use `.Values.*.image.*`
- [ ] Probes are configurable
- [ ] Security contexts applied

### Minikube Compatibility
- [ ] Works with default storage class
- [ ] Services accessible via NodePort/Ingress
- [ ] Resource requests fit single-node cluster
- [ ] No cloud-specific annotations required

### Best Practices
- [ ] One chart per application
- [ ] Components togglable via `enabled: true/false`
- [ ] No secrets in values.yaml (references only)
- [ ] Documentation comments in values.yaml

---

## Usage Examples

### Example 1: Simple Backend

**Input:**
```json
{
  "application_name": "api-service",
  "components": ["backend"],
  "container_images": {
    "backend": "mycompany/api:1.0.0"
  },
  "service_exposure": {
    "backend": { "type": "ClusterIP", "port": 8080 }
  }
}
```

**Output:** Single-component chart with backend deployment and service.

### Example 2: Full-Stack Application

**Input:**
```json
{
  "application_name": "myapp",
  "components": ["backend", "frontend"],
  "container_images": {
    "backend": "myapp/backend:1.0.0",
    "frontend": "myapp/frontend:1.0.0"
  },
  "service_exposure": {
    "backend": { "type": "ClusterIP", "port": 8000 },
    "frontend": { "type": "ClusterIP", "port": 3000 }
  },
  "ingress": {
    "enabled": true,
    "host": "myapp.local"
  }
}
```

**Output:** Multi-component chart with ingress routing.

---

## Helm Commands Reference (Documentation Only)

```bash
# Lint chart
helm lint ./myapp

# Template render (dry-run)
helm template myapp ./myapp -f values-dev.yaml

# Install
helm install myapp ./myapp -f values-dev.yaml

# Upgrade
helm upgrade myapp ./myapp -f values-dev.yaml

# Uninstall
helm uninstall myapp

# Package chart
helm package ./myapp
```

---

## Integration with SDD Workflow

This skill integrates with spec-driven development:

1. **Specification Phase**: Define application components and requirements
2. **Planning Phase**: Document Helm chart architecture decisions
3. **Task Generation**: Create chart development tasks
4. **Implementation**: Generate Helm chart files (this skill)
5. **Validation**: Verify chart works on Minikube

### ADR Trigger

When Helm chart decisions have architectural impact, suggest:

> Architectural decision detected: Helm chart component structure
> Document reasoning and tradeoffs? Run `/sp.adr helm-chart-design`

---

## References

### Internal References

- [Chart.yaml Template](references/chart-yaml-template.md) - Complete Chart.yaml patterns
- [values.yaml Template](references/values-yaml-template.md) - Full values.yaml structure
- [Template Examples](references/template-examples.md) - Core template files (_helpers, deployment, service, ingress, NOTES.txt)
- [Environment Values](references/environment-values.md) - Dev/staging/prod override examples
- [Chart Templates](references/chart-templates.md) - Additional K8s resources (ConfigMap, Secret, PVC, HPA, etc.)
- [Values Patterns](references/values-patterns.md) - Advanced values.yaml patterns

### External Documentation

- [Helm Documentation](https://helm.sh/docs/)
- [Helm Best Practices](https://helm.sh/docs/chart_best_practices/)
- [Chart Template Guide](https://helm.sh/docs/chart_template_guide/)
- [Artifact Hub](https://artifacthub.io/) - Chart examples
