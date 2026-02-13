#!/usr/bin/env bash
# Deploy PostgreSQL on Kubernetes using Bitnami Helm chart.
#
# Usage:
#   bash deploy.sh                              # Default: namespace=postgres, db=appdb
#   bash deploy.sh --namespace my-pg            # Custom namespace
#   bash deploy.sh --password secret123         # Set postgres password
#   bash deploy.sh --database mydb              # Custom database name
#   bash deploy.sh --release pg-main            # Custom Helm release name
set -euo pipefail

NAMESPACE="postgres"
PASSWORD=""
DATABASE="appdb"
RELEASE_NAME="postgresql"

while [[ $# -gt 0 ]]; do
    case "$1" in
        --namespace|-n) NAMESPACE="$2"; shift 2 ;;
        --password|-p) PASSWORD="$2"; shift 2 ;;
        --database|-d) DATABASE="$2"; shift 2 ;;
        --release) RELEASE_NAME="$2"; shift 2 ;;
        *) echo "Unknown arg: $1"; exit 1 ;;
    esac
done

echo "=== PostgreSQL Deployment ==="
echo "Namespace: $NAMESPACE"
echo "Database:  $DATABASE"
echo "Release:   $RELEASE_NAME"
echo ""

# Add Bitnami repo
echo "--- Adding Bitnami Helm repo ---"
helm repo add bitnami https://charts.bitnami.com/bitnami 2>/dev/null || true
helm repo update

# Create namespace if it does not exist
kubectl get namespace "$NAMESPACE" >/dev/null 2>&1 || \
    kubectl create namespace "$NAMESPACE"

# Build Helm command
HELM_CMD=(helm upgrade --install "$RELEASE_NAME" bitnami/postgresql
    --namespace "$NAMESPACE"
    --set auth.database="$DATABASE"
    --set primary.persistence.size=2Gi
    --set primary.resourcesPreset=small
    --wait
    --timeout 10m)

# Set password if provided; otherwise Helm auto-generates one
if [[ -n "$PASSWORD" ]]; then
    HELM_CMD+=(--set auth.postgresPassword="$PASSWORD")
fi

echo ""
echo "--- Installing PostgreSQL via Helm ---"
"${HELM_CMD[@]}"

echo ""
echo "--- Verifying Pods ---"
kubectl get pods -n "$NAMESPACE" -l app.kubernetes.io/instance="$RELEASE_NAME"

echo ""
echo "--- Verifying PVCs ---"
kubectl get pvc -n "$NAMESPACE"

echo ""
echo "PostgreSQL deployed successfully in namespace '$NAMESPACE'"
echo ""
echo "Connection info:"
echo "  Host (in-cluster): ${RELEASE_NAME}.${NAMESPACE}.svc.cluster.local"
echo "  Port:              5432"
echo "  Database:          $DATABASE"
echo "  User:              postgres"
if [[ -n "$PASSWORD" ]]; then
    echo "  Password:          (provided via --password flag)"
else
    echo "  Password:          (auto-generated, retrieve with:)"
    echo "    kubectl get secret -n $NAMESPACE ${RELEASE_NAME} -o jsonpath='{.data.postgres-password}' | base64 -d"
fi
echo ""
echo "Port-forward for local access:"
echo "  kubectl port-forward -n $NAMESPACE svc/$RELEASE_NAME 5432:5432"
