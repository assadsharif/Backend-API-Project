---
name: fastapi-dapr-agent
description: |
  Scaffold FastAPI + Dapr microservices with OpenAI Agents SDK integration.
  Creates service structure, Dapr component configs, agent definitions, and
  Dockerfiles. Triggers on: "scaffold dapr service", "fastapi dapr", "dapr agent",
  "create microservice with dapr", "dapr pub/sub service".
---

# FastAPI + Dapr Agent

Scaffolding skill. Creates FastAPI microservices wired with Dapr sidecars and OpenAI Agents SDK agent definitions.

## Scope

**Does**: Scaffold a complete FastAPI service directory with Dapr component YAMLs (state store, pub/sub), agent class files, Dockerfile, and requirements. Initialize Dapr components on a Kubernetes cluster.

**Does NOT**: Deploy to production clusters. Write business logic inside agents. Configure TLS or auth. Build Docker images (use docker-containerization skill). Manage Helm releases (use helm-packaging skill).

---

## Tool Map

| Action | Script | Input | Output |
|--------|--------|-------|--------|
| Scaffold new service | `scripts/scaffold.py` | `--name <svc> --port <port> --agents <a,b> --output-dir <dir>` | Service directory tree |
| Initialize Dapr components | `scripts/init_dapr.sh` | `<service-name> [--namespace <ns>]` | kubectl apply output |

---

## Execution Pattern (MCP Code Execution)

1. Agent reads this SKILL.md (~100 tokens)
2. Agent executes: `python scripts/scaffold.py --name order-svc --agents triage,fulfillment`
3. Script creates files on disk (0 context tokens consumed)
4. Only the final summary enters context
5. Optionally: `bash scripts/init_dapr.sh order-svc` to apply Dapr components to K8s

---

## Default Dapr Configuration

```yaml
# State store: Redis
statestore:
  type: state.redis
  metadata:
    redisHost: redis-master:6379
    redisPassword: ""

# Pub/Sub: Redis (default) or Kafka
pubsub:
  type: pubsub.redis          # swap to pubsub.kafka for Kafka
  metadata:
    redisHost: redis-master:6379
    # Kafka alternative:
    # brokers: kafka-broker-0.kafka-broker-headless.kafka.svc.cluster.local:9092

# Service invocation: HTTP (Dapr default)
service_invocation:
  protocol: HTTP
```

---

## Clarification Triggers

### Required
1. **Service name** -- what should the microservice be called?
2. **Agent list** -- which agents should be scaffolded? (comma-separated names)

### Optional
3. **Port** -- FastAPI port (default: 8000)
4. **Pub/Sub type** -- Redis (default) or Kafka?
5. **Output directory** -- where to write the scaffold (default: current directory)
6. **Namespace** -- Kubernetes namespace for Dapr components (default: `default`)

---

## Must Follow

- [ ] Always include a `/health` endpoint in main.py
- [ ] Always include a `/dapr/subscribe` endpoint for Dapr pub/sub
- [ ] Each agent gets its own file under `agents/`
- [ ] Dapr component YAMLs go under `dapr/components/`
- [ ] requirements.txt pins major versions
- [ ] Dockerfile uses Python 3.12-slim base
- [ ] Output structured summary of created files

## Must Avoid

- Hardcoding secrets or passwords in component YAMLs
- Including business logic in scaffold (templates only)
- Running `kubectl delete` without explicit user confirmation
- Assuming Dapr is already installed -- check first
- Creating agents without `name` and `instructions` fields

---

## Cross-Platform Compatibility

This skill works on:
- **Claude Code** -- via SKILL.md + scripts/
- **OpenAI Codex** -- same pattern
- **Goose** -- via recipe.yaml

### Goose Recipe
```yaml
name: fastapi-dapr-agent
description: Scaffold FastAPI + Dapr microservice with OpenAI Agents SDK
steps:
  - run: python .claude/skills/fastapi-dapr-agent/scripts/scaffold.py --name {{service_name}} --agents {{agents}}
  - run: bash .claude/skills/fastapi-dapr-agent/scripts/init_dapr.sh {{service_name}}
```
