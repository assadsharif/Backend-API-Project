#!/usr/bin/env bash
# Apply a Helm chart to the Kubernetes cluster.
#
# Usage:
#   bash apply_chart.sh <repo-name> <chart-name> <release-name> [--namespace <ns>] [--values <file>] [--set key=value]
#
# Examples:
#   bash apply_chart.sh bitnami postgresql my-postgres --namespace db
#   bash apply_chart.sh bitnami kafka my-kafka --values custom-values.yaml
set -euo pipefail

REPO_NAME="${1:?Usage: apply_chart.sh <repo> <chart> <release> [--namespace ns] [--values file]}"
CHART_NAME="${2:?Missing chart name}"
RELEASE_NAME="${3:?Missing release name}"
shift 3

NAMESPACE="default"
VALUES_FILE=""
SET_ARGS=()

while [[ $# -gt 0 ]]; do
    case "$1" in
        --namespace|-n)
            NAMESPACE="$2"
            shift 2
            ;;
        --values|-f)
            VALUES_FILE="$2"
            shift 2
            ;;
        --set)
            SET_ARGS+=("--set" "$2")
            shift 2
            ;;
        *)
            echo "Unknown argument: $1"
            exit 1
            ;;
    esac
done

echo "=== Helm Chart Deployment ==="
echo "Repo:      $REPO_NAME"
echo "Chart:     $CHART_NAME"
echo "Release:   $RELEASE_NAME"
echo "Namespace: $NAMESPACE"

# Create namespace if it doesn't exist
kubectl get namespace "$NAMESPACE" >/dev/null 2>&1 || \
    kubectl create namespace "$NAMESPACE"

# Build helm install command
HELM_CMD=(helm upgrade --install "$RELEASE_NAME" "$REPO_NAME/$CHART_NAME"
    --namespace "$NAMESPACE"
    --wait
    --timeout 5m)

if [[ -n "$VALUES_FILE" ]]; then
    HELM_CMD+=(--values "$VALUES_FILE")
fi

if [[ ${#SET_ARGS[@]} -gt 0 ]]; then
    HELM_CMD+=("${SET_ARGS[@]}")
fi

echo ""
echo "Running: ${HELM_CMD[*]}"
echo ""

"${HELM_CMD[@]}"

echo ""
echo "=== Verifying Deployment ==="
kubectl get pods -n "$NAMESPACE" -l "app.kubernetes.io/instance=$RELEASE_NAME" --no-headers

echo ""
echo "✅ Helm chart deployed successfully: $RELEASE_NAME"
