#!/usr/bin/env bash
# Build and deploy a Docusaurus site to Kubernetes.
#
# Usage:
#   bash deploy.sh --name my-docs                          # Default: namespace=docs, port=3000
#   bash deploy.sh --name my-docs --namespace my-ns        # Custom namespace
#   bash deploy.sh --name my-docs --port 8080              # Custom port
set -euo pipefail

NAME=""
NAMESPACE="docs"
PORT="3000"

while [[ $# -gt 0 ]]; do
    case "$1" in
        --name|-n)      NAME="$2"; shift 2 ;;
        --namespace|-s) NAMESPACE="$2"; shift 2 ;;
        --port|-p)      PORT="$2"; shift 2 ;;
        *) echo "Unknown arg: $1"; exit 1 ;;
    esac
done

if [[ -z "$NAME" ]]; then
    echo "ERROR: --name is required"
    exit 1
fi

IMAGE_TAG="${NAME}:latest"

echo "=== Docusaurus K8s Deployment ==="
echo "Name:      $NAME"
echo "Namespace: $NAMESPACE"
echo "Port:      $PORT"
echo "Image:     $IMAGE_TAG"
echo ""

# Step 1: Build the Docusaurus site
echo "--- Building Docusaurus site ---"
if [[ -f "package.json" ]]; then
    npm run build
elif [[ -f "${NAME}/package.json" ]]; then
    cd "$NAME"
    npm run build
    cd ..
else
    echo "ERROR: Cannot find package.json. Run from project root or parent directory."
    exit 1
fi

# Step 2: Build Docker image using Minikube's Docker daemon
echo ""
echo "--- Configuring Minikube Docker environment ---"
eval $(minikube docker-env)

echo "--- Building Docker image: $IMAGE_TAG ---"
if [[ -f "Dockerfile" ]]; then
    docker build -t "$IMAGE_TAG" .
elif [[ -f "${NAME}/Dockerfile" ]]; then
    docker build -t "$IMAGE_TAG" "${NAME}/"
else
    echo "ERROR: Cannot find Dockerfile. Run init_docs.sh first."
    exit 1
fi

# Step 3: Create namespace if needed
echo ""
echo "--- Ensuring namespace '$NAMESPACE' exists ---"
kubectl get namespace "$NAMESPACE" >/dev/null 2>&1 || \
    kubectl create namespace "$NAMESPACE"

# Step 4: Apply K8s manifests
echo ""
echo "--- Applying Kubernetes manifests ---"

kubectl apply -f - <<EOF
apiVersion: apps/v1
kind: Deployment
metadata:
  name: ${NAME}
  namespace: ${NAMESPACE}
  labels:
    app: ${NAME}
    managed-by: docusaurus-deploy-skill
spec:
  replicas: 1
  selector:
    matchLabels:
      app: ${NAME}
  template:
    metadata:
      labels:
        app: ${NAME}
    spec:
      containers:
        - name: ${NAME}
          image: ${IMAGE_TAG}
          imagePullPolicy: Never
          ports:
            - containerPort: 80
              protocol: TCP
          resources:
            requests:
              memory: "64Mi"
              cpu: "50m"
            limits:
              memory: "128Mi"
              cpu: "100m"
          readinessProbe:
            httpGet:
              path: /
              port: 80
            initialDelaySeconds: 5
            periodSeconds: 10
          livenessProbe:
            httpGet:
              path: /
              port: 80
            initialDelaySeconds: 10
            periodSeconds: 30
---
apiVersion: v1
kind: Service
metadata:
  name: ${NAME}
  namespace: ${NAMESPACE}
  labels:
    app: ${NAME}
    managed-by: docusaurus-deploy-skill
spec:
  type: NodePort
  selector:
    app: ${NAME}
  ports:
    - port: ${PORT}
      targetPort: 80
      protocol: TCP
      name: http
EOF

# Step 5: Wait for rollout
echo ""
echo "--- Waiting for rollout to complete ---"
kubectl rollout status deployment/"$NAME" -n "$NAMESPACE" --timeout=120s

# Step 6: Get access info
echo ""
echo "--- Deployment complete ---"
kubectl get pods -n "$NAMESPACE" -l app="$NAME"

echo ""
NODE_PORT=$(kubectl get svc "$NAME" -n "$NAMESPACE" -o jsonpath='{.spec.ports[0].nodePort}')
MINIKUBE_IP=$(minikube ip)

echo "=== Docusaurus site deployed successfully ==="
echo ""
echo "Access URL: http://${MINIKUBE_IP}:${NODE_PORT}"
echo ""
echo "Useful commands:"
echo "  kubectl get pods -n $NAMESPACE          # Check pod status"
echo "  kubectl logs -n $NAMESPACE -l app=$NAME # View logs"
echo "  minikube service $NAME -n $NAMESPACE    # Open in browser"
