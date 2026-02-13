---
name: k8s-foundation
description: |
  Check Kubernetes cluster health, apply Helm charts, and verify K8s readiness.
  Foundation skill for all cloud-native deployments. Triggers on: "check cluster",
  "cluster health", "k8s ready", "verify kubernetes", "helm install".
---

# Kubernetes Foundation

Operations skill. Checks cluster health, applies Helm charts, and verifies Kubernetes readiness for deployments.

## Scope

**Does**: Check cluster connectivity, node status, namespace readiness. Add Helm repos. Apply Helm charts with custom values. Verify pod status post-deploy.

**Does NOT**: Create Kubernetes manifests from scratch (use kubernetes-deployment skill). Build Docker images. Configure Ingress or TLS.

---

## Tool Map

| Action | Script | Input | Output |
|--------|--------|-------|--------|
| Check cluster health | `scripts/check_cluster.py` | `--context <ctx>` | JSON health report |
| Apply Helm chart | `scripts/apply_chart.sh` | `<repo> <chart> <release> [--values]` | Helm install output |
| Verify deployment | `scripts/check_cluster.py` | `--verify <namespace>` | Pod status report |

---

## Execution Pattern (MCP Code Execution)

1. Agent reads this SKILL.md (~100 tokens)
2. Agent executes: `python scripts/check_cluster.py` or `bash scripts/apply_chart.sh`
3. Script runs kubectl/helm commands (0 context tokens consumed)
4. Only the final JSON/text result enters context

---

## Clarification Triggers

### Required
1. **Action** — check health, apply chart, or verify deployment?

### Optional (for chart deployment)
2. **Helm repo** — which Helm repository? (e.g., bitnami)
3. **Chart name** — which chart to install?
4. **Release name** — Helm release name
5. **Namespace** — target namespace (default: `default`)
6. **Values** — custom values file path

---

## Must Follow

- [ ] Always check cluster connectivity before any operation
- [ ] Use `--wait` flag for Helm installs
- [ ] Verify pods reach Running state after deployment
- [ ] Report warnings for pods in CrashLoopBackOff or Pending
- [ ] Output structured JSON for programmatic consumption

## Must Avoid

- Deleting namespaces or resources without explicit confirmation
- Running `helm uninstall` without user consent
- Hardcoding cluster credentials

---

## Cross-Platform Compatibility

This skill works on:
- **Claude Code** — via SKILL.md + scripts/
- **OpenAI Codex** — same pattern
- **Goose** — via recipe.yaml

### Goose Recipe
```yaml
name: k8s-foundation
description: Check cluster health and apply Helm charts
steps:
  - run: python .claude/skills/k8s-foundation/scripts/check_cluster.py
```
