#!/usr/bin/env bash
# Scaffold a new Docusaurus project and add a production Dockerfile.
#
# Usage:
#   bash init_docs.sh --name my-docs --title "My Documentation"
#   bash init_docs.sh --name my-docs --title "My Docs" --output-dir /tmp/projects
set -euo pipefail

NAME=""
TITLE=""
OUTPUT_DIR="."

while [[ $# -gt 0 ]]; do
    case "$1" in
        --name|-n)    NAME="$2"; shift 2 ;;
        --title|-t)   TITLE="$2"; shift 2 ;;
        --output-dir) OUTPUT_DIR="$2"; shift 2 ;;
        *) echo "Unknown arg: $1"; exit 1 ;;
    esac
done

# Validate required args
if [[ -z "$NAME" ]]; then
    echo "ERROR: --name is required"
    exit 1
fi

if [[ -z "$TITLE" ]]; then
    echo "ERROR: --title is required"
    exit 1
fi

echo "=== Docusaurus Project Init ==="
echo "Name:       $NAME"
echo "Title:      $TITLE"
echo "Output dir: $OUTPUT_DIR"
echo ""

# Check npx availability
if ! command -v npx &>/dev/null; then
    echo "ERROR: npx is not installed. Install Node.js (v18+) to proceed."
    echo "  macOS:   brew install node"
    echo "  Ubuntu:  sudo apt install nodejs npm"
    echo "  WSL:     sudo apt install nodejs npm"
    exit 1
fi

echo "--- Scaffolding Docusaurus project ---"
cd "$OUTPUT_DIR"

npx create-docusaurus@latest "$NAME" classic --javascript <<< "y"

echo ""
echo "--- Adding production Dockerfile ---"

cat > "${NAME}/Dockerfile" << 'DOCKERFILE'
# Stage 1: Build the Docusaurus site
FROM node:18-alpine AS builder

WORKDIR /app

COPY package.json package-lock.json* ./
RUN npm ci --prefer-offline

COPY . .
RUN npm run build

# Stage 2: Serve with nginx
FROM nginx:alpine

# Remove default nginx content
RUN rm -rf /usr/share/nginx/html/*

# Copy built static files
COPY --from=builder /app/build /usr/share/nginx/html

# Copy custom nginx config for SPA routing
RUN printf 'server {\n\
    listen 80;\n\
    server_name _;\n\
    root /usr/share/nginx/html;\n\
    index index.html;\n\
\n\
    location / {\n\
        try_files $uri $uri/ /index.html;\n\
    }\n\
\n\
    # Cache static assets\n\
    location ~* \\.(js|css|png|jpg|jpeg|gif|ico|svg|woff|woff2|ttf|eot)$ {\n\
        expires 1y;\n\
        add_header Cache-Control "public, immutable";\n\
    }\n\
\n\
    # Security headers\n\
    add_header X-Frame-Options "SAMEORIGIN" always;\n\
    add_header X-Content-Type-Options "nosniff" always;\n\
}\n' > /etc/nginx/conf.d/default.conf

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
DOCKERFILE

echo ""
echo "--- Adding .dockerignore ---"

cat > "${NAME}/.dockerignore" << 'DOCKERIGNORE'
node_modules
build
.docusaurus
.git
.gitignore
*.md
!docs/**/*.md
!blog/**/*.md
!README.md
Dockerfile
.dockerignore
DOCKERIGNORE

echo ""
echo "=== Docusaurus project scaffolded successfully ==="
echo ""
echo "Project location: ${OUTPUT_DIR}/${NAME}"
echo ""
echo "Next steps:"
echo "  1. cd ${NAME}"
echo "  2. npm start              # Local dev server"
echo "  3. Edit docs/ and blog/   # Add your content"
echo "  4. Run deploy.sh          # Build + deploy to K8s"
