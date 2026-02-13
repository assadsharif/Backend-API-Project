#!/usr/bin/env bash
# Initialize Dapr components on Kubernetes for a scaffolded service.
#
# Usage:
#   bash init_dapr.sh <service-name>                      # Default namespace
#   bash init_dapr.sh <service-name> --namespace my-ns    # Custom namespace
#
# Prerequisites:
#   - Dapr CLI installed (https://docs.dapr.io/getting-started/install-dapr-cli/)
#   - kubectl configured with cluster access
#   - Dapr initialized on the cluster (dapr init -k)
set -euo pipefail

# --- Parse arguments ---
SERVICE_NAME="${1:-}"
NAMESPACE="default"

if [[ -z "$SERVICE_NAME" ]]; then
    echo "ERROR: Service name is required."
    echo "Usage: bash init_dapr.sh <service-name> [--namespace <ns>]"
    exit 1
fi

shift
while [[ $# -gt 0 ]]; do
    case "$1" in
        --namespace|-n) NAMESPACE="$2"; shift 2 ;;
        *) echo "Unknown arg: $1"; exit 1 ;;
    esac
done

echo "=== Dapr Component Init ==="
echo "Service:   $SERVICE_NAME"
echo "Namespace: $NAMESPACE"
echo ""

# --- Check Dapr CLI ---
echo "--- Checking Dapr CLI ---"
if ! command -v dapr &>/dev/null; then
    echo "WARNING: Dapr CLI not found."
    echo "Install it with:"
    echo "  curl -fsSL https://raw.githubusercontent.com/dapr/cli/master/install/install.sh | /bin/bash"
    echo ""
    echo "Then initialize Dapr on your cluster:"
    echo "  dapr init -k"
    echo ""
    echo "Continuing with kubectl apply only..."
else
    DAPR_VERSION=$(dapr --version 2>/dev/null | head -1 || echo "unknown")
    echo "Dapr CLI found: $DAPR_VERSION"
fi

# --- Check kubectl ---
echo ""
echo "--- Checking kubectl ---"
if ! command -v kubectl &>/dev/null; then
    echo "ERROR: kubectl not found. Install kubectl first."
    exit 1
fi

if ! kubectl cluster-info &>/dev/null; then
    echo "ERROR: Cannot connect to Kubernetes cluster."
    echo "Ensure your kubeconfig is set up correctly."
    exit 1
fi
echo "kubectl connected to cluster."

# --- Create namespace if needed ---
echo ""
echo "--- Ensuring namespace '$NAMESPACE' exists ---"
kubectl get namespace "$NAMESPACE" &>/dev/null || \
    kubectl create namespace "$NAMESPACE"

# --- Locate component YAMLs ---
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SCAFFOLD_DAPR_DIR=""

# Try standard scaffold output locations
for candidate in \
    "./$SERVICE_NAME/dapr/components" \
    "$SCRIPT_DIR/../$SERVICE_NAME/dapr/components" \
    "$SERVICE_NAME/dapr/components"; do
    if [[ -d "$candidate" ]]; then
        SCAFFOLD_DAPR_DIR="$candidate"
        break
    fi
done

if [[ -z "$SCAFFOLD_DAPR_DIR" ]]; then
    echo "WARNING: Could not find dapr/components/ directory for '$SERVICE_NAME'."
    echo "Looked in:"
    echo "  ./$SERVICE_NAME/dapr/components"
    echo "  $SCRIPT_DIR/../$SERVICE_NAME/dapr/components"
    echo ""
    echo "Run scaffold.py first to generate component YAMLs."
    exit 1
fi

echo "Found Dapr components at: $SCAFFOLD_DAPR_DIR"

# --- Apply component YAMLs ---
echo ""
echo "--- Applying Dapr component YAMLs ---"
for yaml_file in "$SCAFFOLD_DAPR_DIR"/*.yaml; do
    if [[ -f "$yaml_file" ]]; then
        echo "Applying: $yaml_file"
        kubectl apply -f "$yaml_file" -n "$NAMESPACE"
    fi
done

# --- Apply Dapr configuration if present ---
DAPR_CONFIG="$(dirname "$SCAFFOLD_DAPR_DIR")/config.yaml"
if [[ -f "$DAPR_CONFIG" ]]; then
    echo ""
    echo "--- Applying Dapr configuration ---"
    echo "Applying: $DAPR_CONFIG"
    kubectl apply -f "$DAPR_CONFIG" -n "$NAMESPACE"
fi

# --- Verify Dapr sidecar injector ---
echo ""
echo "--- Verifying Dapr sidecar injector ---"
INJECTOR_PODS=$(kubectl get pods -n dapr-system -l app=dapr-sidecar-injector -o jsonpath='{.items[*].metadata.name}' 2>/dev/null || true)

if [[ -n "$INJECTOR_PODS" ]]; then
    echo "Dapr sidecar injector running: $INJECTOR_PODS"
else
    echo "WARNING: Dapr sidecar injector not found in dapr-system namespace."
    echo "Dapr may not be initialized on this cluster."
    echo "Run: dapr init -k"
fi

echo ""
echo "=== Dapr components applied for '$SERVICE_NAME' in namespace '$NAMESPACE' ==="
echo ""
echo "Verify with:"
echo "  kubectl get components -n $NAMESPACE"
echo "  kubectl get configurations -n $NAMESPACE"
