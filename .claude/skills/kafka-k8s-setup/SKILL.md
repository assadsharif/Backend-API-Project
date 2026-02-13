---
name: kafka-k8s-setup
description: |
  Deploy Apache Kafka on Kubernetes via Helm (Bitnami chart). Create topics,
  verify broker health, and manage Kafka infrastructure. Triggers on:
  "deploy kafka", "kafka kubernetes", "setup kafka", "create kafka topic".
---

# Kafka K8s Setup

Infrastructure skill. Deploys and manages Apache Kafka on Kubernetes using Bitnami Helm charts.

## Scope

**Does**: Add Bitnami Helm repo. Deploy Kafka with Kraft mode (no ZooKeeper). Create topics. Verify broker health. Configure resource limits for Minikube.

**Does NOT**: Write Kafka producers/consumers. Configure Kafka Connect. Set up Schema Registry. Manage Kafka Streams applications.

---

## Tool Map

| Action | Script | Input | Output |
|--------|--------|-------|--------|
| Deploy Kafka | `scripts/deploy.sh` | `[--namespace] [--replicas] [--values]` | Helm install output |
| Verify brokers | `scripts/verify.py` | `[--namespace]` | JSON health report |
| Create topics | `scripts/create_topics.py` | `--topics <t1,t2>` `[--namespace]` | Topic creation status |

---

## Execution Pattern (MCP Code Execution)

1. Agent reads this SKILL.md (~100 tokens)
2. Agent executes scripts sequentially: deploy → verify → create_topics
3. Scripts run helm/kubectl commands (0 context tokens consumed)
4. Only the final result enters context

---

## Default Configuration (Minikube-friendly)

```yaml
# Kraft mode (no ZooKeeper dependency)
kraft:
  enabled: true
listeners:
  client:
    protocol: PLAINTEXT
controller:
  replicaCount: 1
broker:
  replicaCount: 1
  resourcesPreset: small
  persistence:
    size: 2Gi
```

---

## Clarification Triggers

### Required
1. **Action** — deploy, verify, or create topics?

### Optional
2. **Namespace** — target namespace (default: `kafka`)
3. **Replica count** — number of brokers (default: 1 for Minikube)
4. **Topics** — comma-separated list of topics to create

---

## Must Follow

- [ ] Always add bitnami repo before install: `helm repo add bitnami https://charts.bitnami.com/bitnami`
- [ ] Use Kraft mode (no ZooKeeper) for simpler setup
- [ ] Verify all pods Running before creating topics
- [ ] Use resource-constrained settings for Minikube

## Must Avoid

- Deploying ZooKeeper-based Kafka (use Kraft mode)
- Setting replica count > 1 on Minikube without checking memory
- Hardcoding authentication credentials

---

## Cross-Platform Compatibility

```yaml
# Goose recipe.yaml
name: kafka-k8s-setup
description: Deploy Kafka on Kubernetes
steps:
  - run: bash .claude/skills/kafka-k8s-setup/scripts/deploy.sh
  - run: python .claude/skills/kafka-k8s-setup/scripts/verify.py
```
