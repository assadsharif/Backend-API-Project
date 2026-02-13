#!/usr/bin/env bash
# Build a Next.js Docker image inside Minikube and deploy via a generated Helm chart.
#
# Usage:
#   bash build_and_deploy.sh --app-name myapp
#   bash build_and_deploy.sh --app-name myapp --image-tag v1.0.0
#   bash build_and_deploy.sh --app-name myapp --namespace staging --port 3000
#
# Prerequisites:
#   - Minikube running (minikube status)
#   - Helm 3 installed
#   - Next.js project with output: 'standalone' in next.config.js
set -euo pipefail

# ---------------------------------------------------------------------------
# Defaults
# ---------------------------------------------------------------------------
APP_NAME=""
IMAGE_TAG="latest"
NAMESPACE="default"
PORT="3000"

# ---------------------------------------------------------------------------
# Parse arguments
# ---------------------------------------------------------------------------
while [[ $# -gt 0 ]]; do
    case "$1" in
        --app-name)   APP_NAME="$2";   shift 2 ;;
        --image-tag)  IMAGE_TAG="$2";  shift 2 ;;
        --namespace)  NAMESPACE="$2";  shift 2 ;;
        --port)       PORT="$2";       shift 2 ;;
        *)            echo "Unknown argument: $1"; exit 1 ;;
    esac
done

if [[ -z "$APP_NAME" ]]; then
    echo "ERROR: --app-name is required"
    echo "Usage: bash build_and_deploy.sh --app-name <name> [--image-tag <tag>] [--namespace <ns>] [--port <port>]"
    exit 1
fi

IMAGE_NAME="${APP_NAME}:${IMAGE_TAG}"
CHART_DIR="/tmp/helm-${APP_NAME}"

echo "=== Next.js K8s Deploy ==="
echo "App:       $APP_NAME"
echo "Image:     $IMAGE_NAME"
echo "Namespace: $NAMESPACE"
echo "Port:      $PORT"
echo ""

# ---------------------------------------------------------------------------
# Step 1 — Verify Minikube is running
# ---------------------------------------------------------------------------
echo "--- Checking Minikube status ---"
if ! minikube status --format='{{.Host}}' 2>/dev/null | grep -q "Running"; then
    echo "ERROR: Minikube is not running. Start it with: minikube start"
    exit 1
fi
echo "Minikube is running."
echo ""

# ---------------------------------------------------------------------------
# Step 2 — Point Docker CLI at Minikube's Docker daemon
# ---------------------------------------------------------------------------
echo "--- Configuring Minikube Docker environment ---"
eval $(minikube docker-env)
echo "Docker daemon: Minikube"
echo ""

# ---------------------------------------------------------------------------
# Step 3 — Build Docker image
# ---------------------------------------------------------------------------
echo "--- Building Docker image: $IMAGE_NAME ---"

# Use the skill's Dockerfile template if no local Dockerfile exists
DOCKERFILE_PATH="Dockerfile"
SKILL_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
if [[ ! -f "$DOCKERFILE_PATH" ]]; then
    if [[ -f "${SKILL_DIR}/templates/Dockerfile" ]]; then
        DOCKERFILE_PATH="${SKILL_DIR}/templates/Dockerfile"
        echo "Using skill template Dockerfile: $DOCKERFILE_PATH"
    else
        echo "ERROR: No Dockerfile found in current directory or skill templates"
        exit 1
    fi
fi

docker build -t "$IMAGE_NAME" -f "$DOCKERFILE_PATH" .
echo ""
echo "Image built: $IMAGE_NAME"
echo ""

# ---------------------------------------------------------------------------
# Step 4 — Generate Helm chart in /tmp
# ---------------------------------------------------------------------------
echo "--- Generating Helm chart at $CHART_DIR ---"
rm -rf "$CHART_DIR"
mkdir -p "${CHART_DIR}/templates"

# Chart.yaml
cat > "${CHART_DIR}/Chart.yaml" <<EOF
apiVersion: v2
name: ${APP_NAME}
description: Auto-generated Helm chart for ${APP_NAME} (Next.js)
type: application
version: 0.1.0
appVersion: "${IMAGE_TAG}"
EOF

# values.yaml
cat > "${CHART_DIR}/values.yaml" <<EOF
replicaCount: 1

image:
  repository: "${APP_NAME}"
  tag: "${IMAGE_TAG}"
  pullPolicy: Never

service:
  type: NodePort
  port: ${PORT}
  targetPort: 3000

resources:
  requests:
    cpu: 100m
    memory: 128Mi
  limits:
    cpu: 500m
    memory: 512Mi

nodeSelector: {}
tolerations: []
affinity: {}
EOF

# deployment.yaml
cat > "${CHART_DIR}/templates/deployment.yaml" <<'TMPL'
apiVersion: apps/v1
kind: Deployment
metadata:
  name: {{ .Release.Name }}
  labels:
    app: {{ .Release.Name }}
    chart: {{ .Chart.Name }}-{{ .Chart.Version }}
spec:
  replicas: {{ .Values.replicaCount }}
  selector:
    matchLabels:
      app: {{ .Release.Name }}
  template:
    metadata:
      labels:
        app: {{ .Release.Name }}
    spec:
      containers:
        - name: {{ .Chart.Name }}
          image: "{{ .Values.image.repository }}:{{ .Values.image.tag }}"
          imagePullPolicy: {{ .Values.image.pullPolicy }}
          ports:
            - containerPort: {{ .Values.service.targetPort }}
              protocol: TCP
          resources:
            requests:
              cpu: {{ .Values.resources.requests.cpu }}
              memory: {{ .Values.resources.requests.memory }}
            limits:
              cpu: {{ .Values.resources.limits.cpu }}
              memory: {{ .Values.resources.limits.memory }}
          readinessProbe:
            httpGet:
              path: /
              port: {{ .Values.service.targetPort }}
            initialDelaySeconds: 10
            periodSeconds: 5
          livenessProbe:
            httpGet:
              path: /
              port: {{ .Values.service.targetPort }}
            initialDelaySeconds: 15
            periodSeconds: 10
      {{- with .Values.nodeSelector }}
      nodeSelector:
        {{- toYaml . | nindent 8 }}
      {{- end }}
      {{- with .Values.tolerations }}
      tolerations:
        {{- toYaml . | nindent 8 }}
      {{- end }}
      {{- with .Values.affinity }}
      affinity:
        {{- toYaml . | nindent 8 }}
      {{- end }}
TMPL

# service.yaml
cat > "${CHART_DIR}/templates/service.yaml" <<'TMPL'
apiVersion: v1
kind: Service
metadata:
  name: {{ .Release.Name }}
  labels:
    app: {{ .Release.Name }}
    chart: {{ .Chart.Name }}-{{ .Chart.Version }}
spec:
  type: {{ .Values.service.type }}
  ports:
    - port: {{ .Values.service.port }}
      targetPort: {{ .Values.service.targetPort }}
      protocol: TCP
      name: http
  selector:
    app: {{ .Release.Name }}
TMPL

echo "Chart generated with deployment.yaml, service.yaml, values.yaml"
echo ""

# ---------------------------------------------------------------------------
# Step 5 — Create namespace if needed
# ---------------------------------------------------------------------------
if [[ "$NAMESPACE" != "default" ]]; then
    kubectl get namespace "$NAMESPACE" >/dev/null 2>&1 || \
        kubectl create namespace "$NAMESPACE"
fi

# ---------------------------------------------------------------------------
# Step 6 — Deploy via Helm
# ---------------------------------------------------------------------------
echo "--- Deploying via Helm ---"
helm upgrade --install "$APP_NAME" "$CHART_DIR" \
    --namespace "$NAMESPACE" \
    --wait \
    --timeout 5m

echo ""
echo "--- Verifying Pods ---"
kubectl get pods -n "$NAMESPACE" -l "app=${APP_NAME}" --no-headers
echo ""

# ---------------------------------------------------------------------------
# Step 7 — Print access URL
# ---------------------------------------------------------------------------
echo "--- Access URL ---"
minikube service "$APP_NAME" --namespace "$NAMESPACE" --url 2>/dev/null || \
    echo "Run: minikube service ${APP_NAME} --namespace ${NAMESPACE} --url"

echo ""
echo "=== Deployment complete: ${APP_NAME} ==="
