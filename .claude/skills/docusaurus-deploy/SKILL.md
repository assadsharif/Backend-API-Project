---
name: docusaurus-deploy
description: |
  Deploy Docusaurus documentation sites on Kubernetes. Scaffolds a new Docusaurus
  project, containerizes it with nginx, and deploys to K8s with service exposure.
  Triggers on: "deploy docs", "docusaurus kubernetes", "docs site k8s",
  "create documentation site", "deploy docusaurus".
---

# Docusaurus Deploy

Infrastructure skill. Scaffolds, containerizes, and deploys Docusaurus documentation sites on Kubernetes.

## Scope

**Does**: Initialize a new Docusaurus project (classic template). Generate a production Dockerfile (nginx:alpine). Build the static site. Deploy to Kubernetes with Deployment + Service manifests. Verify deployment health. Expose the documentation site via NodePort.

**Does NOT**: Write documentation content. Configure custom Docusaurus plugins or themes. Set up Ingress or TLS termination. Manage DNS records. Configure CI/CD pipelines.

---

## Tool Map

| Action | Script | Input | Output |
|--------|--------|-------|--------|
| Scaffold project | `scripts/init_docs.sh` | `--name <name> --title <title> [--output-dir <dir>]` | Docusaurus project + Dockerfile |
| Build + Deploy | `scripts/deploy.sh` | `--name <name> [--namespace <ns>] [--port <port>]` | K8s Deployment + Service |
| Verify health | `scripts/verify.py` | `--name <name> [--namespace <ns>]` | JSON health report |

---

## Execution Pattern (MCP Code Execution)

1. Agent reads this SKILL.md (~100 tokens)
2. Agent executes scripts sequentially: init_docs.sh -> deploy.sh -> verify.py
3. Scripts run npx/npm/docker/kubectl commands (0 context tokens consumed)
4. Only the final JSON/text result enters context

---

## Clarification Triggers

### Required
1. **Project name** -- used for directory name, Docker image tag, and K8s resource names
2. **Site title** -- the display title shown on the Docusaurus site

### Optional
3. **Port** -- container/service port (default: `3000`)
4. **Namespace** -- Kubernetes namespace (default: `docs`)
5. **Output directory** -- where to scaffold the project (default: current directory)

---

## Must Follow

- [ ] Verify `npx` is available before scaffolding
- [ ] Use Docusaurus classic template for consistent structure
- [ ] Use `nginx:alpine` as the production image base (minimal footprint)
- [ ] Create namespace if it does not already exist
- [ ] Wait for rollout completion before reporting success
- [ ] Output structured JSON from verify.py for programmatic consumption
- [ ] Use Minikube Docker daemon for image builds (no registry push needed)

## Must Avoid

- Modifying user-authored documentation content
- Installing custom Docusaurus plugins without user consent
- Hardcoding cluster credentials or secrets
- Using `latest` as the only image tag (always include project name)
- Deleting namespaces or resources without explicit confirmation

---

## Cross-Platform Compatibility

This skill works on:
- **Claude Code** -- via SKILL.md + scripts/
- **OpenAI Codex** -- same pattern
- **Goose** -- via recipe.yaml

### Goose Recipe
```yaml
name: docusaurus-deploy
description: Deploy Docusaurus documentation site on Kubernetes
steps:
  - run: bash .claude/skills/docusaurus-deploy/scripts/init_docs.sh --name my-docs --title "My Docs"
  - run: bash .claude/skills/docusaurus-deploy/scripts/deploy.sh --name my-docs
  - run: python .claude/skills/docusaurus-deploy/scripts/verify.py --name my-docs
```
