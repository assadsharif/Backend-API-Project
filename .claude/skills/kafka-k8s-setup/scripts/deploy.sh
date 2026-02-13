#!/usr/bin/env bash
# Deploy Apache Kafka on Kubernetes using Bitnami Helm chart (Kraft mode).
#
# Usage:
#   bash deploy.sh                          # Default: namespace=kafka, 1 broker
#   bash deploy.sh --namespace my-kafka     # Custom namespace
#   bash deploy.sh --replicas 3             # Multiple brokers
#   bash deploy.sh --values custom.yaml     # Custom values file
set -euo pipefail

NAMESPACE="kafka"
REPLICAS="1"
VALUES_FILE=""
RELEASE_NAME="kafka"

while [[ $# -gt 0 ]]; do
    case "$1" in
        --namespace|-n) NAMESPACE="$2"; shift 2 ;;
        --replicas|-r) REPLICAS="$2"; shift 2 ;;
        --values|-f) VALUES_FILE="$2"; shift 2 ;;
        --release) RELEASE_NAME="$2"; shift 2 ;;
        *) echo "Unknown arg: $1"; exit 1 ;;
    esac
done

echo "=== Kafka Deployment ==="
echo "Namespace: $NAMESPACE"
echo "Brokers:   $REPLICAS"
echo "Release:   $RELEASE_NAME"
echo ""

# Add Bitnami repo
echo "--- Adding Bitnami Helm repo ---"
helm repo add bitnami https://charts.bitnami.com/bitnami 2>/dev/null || true
helm repo update

# Create namespace
kubectl get namespace "$NAMESPACE" >/dev/null 2>&1 || \
    kubectl create namespace "$NAMESPACE"

# Build Helm command
HELM_CMD=(helm upgrade --install "$RELEASE_NAME" bitnami/kafka
    --namespace "$NAMESPACE"
    --set kraft.enabled=true
    --set controller.replicaCount="$REPLICAS"
    --set broker.replicaCount="$REPLICAS"
    --set broker.resourcesPreset=small
    --set broker.persistence.size=2Gi
    --set listeners.client.protocol=PLAINTEXT
    --set listeners.interbroker.protocol=PLAINTEXT
    --set listeners.controller.protocol=PLAINTEXT
    --wait
    --timeout 10m)

if [[ -n "$VALUES_FILE" ]]; then
    HELM_CMD+=(--values "$VALUES_FILE")
fi

echo ""
echo "--- Installing Kafka via Helm ---"
"${HELM_CMD[@]}"

echo ""
echo "--- Verifying Pods ---"
kubectl get pods -n "$NAMESPACE" -l app.kubernetes.io/instance="$RELEASE_NAME"

echo ""
echo "✅ Kafka deployed successfully in namespace '$NAMESPACE'"
echo ""
echo "Connection info:"
echo "  Bootstrap: ${RELEASE_NAME}-broker-0.${RELEASE_NAME}-broker-headless.${NAMESPACE}.svc.cluster.local:9092"
