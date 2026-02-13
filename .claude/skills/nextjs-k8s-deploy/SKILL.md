---
name: nextjs-k8s-deploy
description: |
  Deploy Next.js applications on Kubernetes using Docker + Helm charts on Minikube.
  Builds container images, generates Helm charts, and deploys with verification.
  Triggers on: "deploy nextjs", "next.js kubernetes", "nextjs k8s", "deploy frontend k8s".
---

# Next.js K8s Deploy

Deployment skill. Builds and deploys Next.js applications on Kubernetes via Minikube's Docker daemon and auto-generated Helm charts.

## Scope

**Does**: Build Next.js Docker images using Minikube's Docker daemon. Generate temporary Helm charts (deployment, service, values). Deploy via `helm upgrade --install --wait`. Print Minikube service access URL. Verify pod health and service endpoints.

**Does NOT**: Create Next.js applications from scratch (use nextjs-app-router skill). Configure Ingress or TLS. Set up CI/CD pipelines. Manage production cluster deployments. Push images to external registries.

---

## Tool Map

| Action | Script | Input | Output |
|--------|--------|-------|--------|
| Build image + deploy | `scripts/build_and_deploy.sh` | `--app-name <name> [--image-tag] [--namespace] [--port]` | Helm install output + access URL |
| Verify deployment | `scripts/verify.py` | `--app-name <name> [--namespace]` | JSON health report |

---

## Execution Pattern (MCP Code Execution)

1. Agent reads this SKILL.md (~100 tokens)
2. Agent executes: `bash scripts/build_and_deploy.sh --app-name myapp`
3. Script builds Docker image and deploys Helm chart (0 context tokens consumed)
4. Agent executes: `python scripts/verify.py --app-name myapp`
5. Only the final JSON health report enters context

---

## Clarification Triggers

### Required
1. **App name** -- what is the application name? (used for image name, Helm release, and K8s labels)

### Optional
2. **Image tag** -- which tag for the Docker image? (default: `latest`)
3. **Namespace** -- target Kubernetes namespace? (default: `default`)
4. **Node port** -- which port does the Next.js app expose? (default: `3000`)

---

## Must Follow

- [ ] Always use `eval $(minikube docker-env)` to build images inside Minikube's Docker daemon
- [ ] Use the multi-stage Dockerfile from `templates/Dockerfile` for production builds
- [ ] Use `helm upgrade --install --wait` for idempotent deployments
- [ ] Verify pods reach Running state after deployment
- [ ] Set `imagePullPolicy: Never` since images are built locally in Minikube
- [ ] Output structured JSON from verify script for programmatic consumption
- [ ] Ensure the Next.js project has `output: 'standalone'` in `next.config.js`

## Must Avoid

- Pushing images to external registries (images stay local to Minikube)
- Deploying without verifying Minikube is running
- Hardcoding secrets, tokens, or credentials in charts or Dockerfiles
- Using `latest` tag without explicit user acknowledgment
- Deleting namespaces or Helm releases without user consent
- Modifying the Next.js application source code

---

## Cross-Platform Compatibility

This skill works on:
- **Claude Code** -- via SKILL.md + scripts/
- **OpenAI Codex** -- same pattern
- **Goose** -- via recipe.yaml

### Goose Recipe
```yaml
name: nextjs-k8s-deploy
description: Build and deploy Next.js app on Kubernetes via Minikube
steps:
  - run: bash .claude/skills/nextjs-k8s-deploy/scripts/build_and_deploy.sh --app-name $APP_NAME
  - run: python .claude/skills/nextjs-k8s-deploy/scripts/verify.py --app-name $APP_NAME
```
