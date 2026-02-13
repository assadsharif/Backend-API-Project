---
name: docker-containerization
description: Enable AI-assisted, spec-governed containerization of applications using Docker and Docker AI Agent (Gordon). Use when generating Dockerfiles, validating container configurations, or creating Gordon prompts. Triggers on requests involving Docker setup, container configuration, or deployment preparation.
---

# Docker Containerization Skill

AI-assisted, spec-governed containerization for applications using Docker and Docker AI Agent (Gordon).

## Purpose

Enable generation of production-ready Dockerfiles and container configurations that:
- Follow spec-driven development principles
- Maintain stateless container design
- Support environment-based configuration
- Integrate with Docker AI (Gordon) for intelligent assistance

---

## When to Use This Skill

**Use this skill when:**
- Creating Dockerfiles for new applications
- Containerizing existing applications for Kubernetes
- Optimizing existing Dockerfiles for production
- Generating Docker AI (Gordon) prompts for assistance
- Preparing applications for Helm chart packaging

**Do NOT use this skill when:**
- Deploying containers (use minikube-cluster + helm-packaging)
- Debugging running containers (use kubectl-ai)
- Analyzing container performance (use kagent-analysis)
- Working with non-containerized applications
- Managing container orchestration (use Helm skills)

---

## Required Clarifications

Before generating output, clarify these with the user:

### Mandatory Clarifications

1. **Application framework?** (e.g., FastAPI, Express, Next.js)
2. **Production or development image?**
3. **Any specific base image requirements?**

### Optional Clarifications (if relevant)

4. **Build arguments needed?** (e.g., API URLs, feature flags)
5. **Health check endpoint available?**
6. **Multi-stage build preferred?** (default: yes)

---

## Version Compatibility

| Component | Supported Versions | Notes |
|-----------|-------------------|-------|
| Docker Engine | 20.10+ | BuildKit recommended |
| Docker Compose | 2.0+ | V2 syntax |
| BuildKit | 0.10+ | For advanced features |
| Gordon (Docker AI) | Latest | Requires Docker Desktop |

### Base Image Recommendations

| Runtime | Recommended Base | Size |
|---------|-----------------|------|
| Python 3.11-3.13 | `python:3.13-slim` | ~150MB |
| Node.js 18-22 | `node:22-alpine` | ~180MB |
| Go 1.21+ | `golang:1.22-alpine` | ~250MB |
| Java 17+ | `eclipse-temurin:21-jre-alpine` | ~200MB |

---

## Inputs

### Required Inputs

| Input | Type | Description |
|-------|------|-------------|
| `application_role` | `frontend` \| `backend` | The application tier being containerized |
| `runtime_requirements` | Object | Language, version, dependencies |
| `environment_variables` | Array | Required env vars (names only, no values) |
| `port_exposure` | Number \| Array | Port(s) the container exposes |

### Optional Inputs

| Input | Type | Default | Description |
|-------|------|---------|-------------|
| `base_image` | String | Auto-detected | Override base image selection |
| `build_args` | Object | `{}` | Build-time arguments |
| `healthcheck` | Object | `null` | Health check configuration |
| `multi_stage` | Boolean | `true` | Use multi-stage builds |

---

## Outputs

### Primary Outputs

1. **Dockerfile** (generated, NOT executed)
   - Multi-stage build optimized
   - Security-hardened (non-root user)
   - Layer-optimized for caching

2. **Docker Build Command Suggestions**
   - Build commands with recommended flags
   - Tag naming conventions

3. **Docker Run Command Suggestions**
   - Runtime configuration
   - Volume mounts
   - Network settings

4. **Gordon Prompt Suggestions**
   - AI-assisted optimization prompts
   - Debugging assistance prompts
   - Security analysis prompts

---

## Allowed Actions

- Generate Dockerfile content (text output)
- Suggest `docker build` commands (as documentation)
- Suggest `docker run` commands (as documentation)
- Suggest Docker Compose configurations
- Generate Gordon (Docker AI) prompts
- Validate container logic against project specs
- Recommend base images based on requirements
- Suggest multi-stage build optimizations
- Propose health check configurations
- Review Dockerfile for security best practices

---

## Forbidden Actions

- Running any `docker` commands
- Executing `docker build`, `docker run`, `docker push`
- Modifying application source code
- Hardcoding secrets, tokens, passwords, or API keys
- Bypassing spec-driven development workflow
- Creating containers that persist state locally
- Embedding credentials in Dockerfile
- Using `latest` tag without explicit user approval
- Auto-executing Gordon commands

---

## Constraints

### Phase III Compliance
- Respect read-only behavior for Phase I and II
- Containerization is infrastructure (Phase IV scope)
- Must not modify existing application logic

### Stateless Design (MANDATORY)
- No local file storage for state
- Session data via external services only
- Database connections via environment variables
- All persistent data externalized

### Configuration Requirements
- All configuration via environment variables
- No hardcoded URLs, ports, or credentials
- Support for `.env` file mounting
- Clear documentation of required env vars

### Security Requirements
- Non-root user in production images
- Minimal base images (alpine/slim preferred)
- No secrets in build layers
- Multi-stage builds to exclude dev dependencies

---

## Dockerfile Templates

### Backend (FastAPI/Python)

```dockerfile
# syntax=docker/dockerfile:1

# ============================================
# Stage 1: Builder
# ============================================
FROM python:3.13-slim AS builder

WORKDIR /app

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt

# ============================================
# Stage 2: Production
# ============================================
FROM python:3.13-slim AS production

# Create non-root user
RUN groupadd --gid 1000 appgroup \
    && useradd --uid 1000 --gid appgroup --shell /bin/bash --create-home appuser

WORKDIR /app

# Copy installed packages from builder
COPY --from=builder /root/.local /home/appuser/.local

# Copy application code
COPY --chown=appuser:appgroup . .

# Set environment
ENV PATH=/home/appuser/.local/bin:$PATH
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# Switch to non-root user
USER appuser

# Expose port (configurable)
EXPOSE ${PORT:-8000}

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:${PORT:-8000}/health')" || exit 1

# Run application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "${PORT:-8000}"]
```

### Frontend (Next.js)

```dockerfile
# syntax=docker/dockerfile:1

# ============================================
# Stage 1: Dependencies
# ============================================
FROM node:20-alpine AS deps

WORKDIR /app

# Copy package files
COPY package.json package-lock.json* ./

# Install dependencies
RUN npm ci --only=production

# ============================================
# Stage 2: Builder
# ============================================
FROM node:20-alpine AS builder

WORKDIR /app

COPY --from=deps /app/node_modules ./node_modules
COPY . .

# Build arguments for environment
ARG NEXT_PUBLIC_API_URL
ENV NEXT_PUBLIC_API_URL=$NEXT_PUBLIC_API_URL

# Build the application
RUN npm run build

# ============================================
# Stage 3: Production
# ============================================
FROM node:20-alpine AS production

WORKDIR /app

# Create non-root user
RUN addgroup --system --gid 1001 nodejs \
    && adduser --system --uid 1001 nextjs

# Copy built assets
COPY --from=builder /app/public ./public
COPY --from=builder --chown=nextjs:nodejs /app/.next/standalone ./
COPY --from=builder --chown=nextjs:nodejs /app/.next/static ./.next/static

USER nextjs

EXPOSE 3000

ENV PORT=3000
ENV HOSTNAME="0.0.0.0"

CMD ["node", "server.js"]
```

---

## Docker Command Suggestions

### Build Commands

```bash
# Backend build (suggested, not executed)
docker build \
    --tag myapp-backend:$(git rev-parse --short HEAD) \
    --build-arg PORT=8000 \
    --file Dockerfile.backend \
    --target production \
    ./backend

# Frontend build (suggested, not executed)
docker build \
    --tag myapp-frontend:$(git rev-parse --short HEAD) \
    --build-arg NEXT_PUBLIC_API_URL=http://localhost:8000 \
    --file Dockerfile.frontend \
    --target production \
    ./frontend
```

### Run Commands

```bash
# Backend run (suggested, not executed)
docker run \
    --name myapp-backend \
    --publish 8000:8000 \
    --env-file .env \
    --env DATABASE_URL \
    --env JWT_SECRET \
    --restart unless-stopped \
    --detach \
    myapp-backend:latest

# Frontend run (suggested, not executed)
docker run \
    --name myapp-frontend \
    --publish 3000:3000 \
    --env-file .env.local \
    --restart unless-stopped \
    --detach \
    myapp-frontend:latest
```

---

## Gordon (Docker AI) Prompt Suggestions

### Dockerfile Optimization

```
@gordon optimize this Dockerfile for production:
- Minimize image size
- Reduce build time with layer caching
- Apply security best practices
- Suggest multi-stage improvements
```

### Security Analysis

```
@gordon analyze this Dockerfile for security vulnerabilities:
- Check for hardcoded secrets
- Verify non-root user configuration
- Identify exposed attack surface
- Recommend security hardening
```

### Debugging Assistance

```
@gordon help debug this container issue:
- Container exits immediately after start
- Environment variables not loading
- Health check failing
- Network connectivity problems
```

### Performance Tuning

```
@gordon suggest performance improvements:
- Memory allocation optimization
- CPU limit recommendations
- Build cache strategies
- Image size reduction
```

### Compliance Check

```
@gordon verify this Dockerfile meets these requirements:
- Stateless design (no local state)
- Configuration via environment variables only
- Non-root user execution
- No secrets in build layers
```

---

## Validation Checklist

Before finalizing any Dockerfile output, validate against:

### Security
- [ ] No secrets or credentials in Dockerfile
- [ ] Uses non-root user for runtime
- [ ] Minimal base image (alpine/slim)
- [ ] No unnecessary packages installed

### Statelessness
- [ ] No `VOLUME` for application state
- [ ] No local file writes for state
- [ ] All data via external services
- [ ] Session/cache externalized

### Configuration
- [ ] All config via `ENV` or `ARG`
- [ ] No hardcoded URLs/ports
- [ ] `.env` file support documented
- [ ] All required vars listed

### Spec Compliance
- [ ] Aligns with project constitution
- [ ] Does not modify Phase I/II/III code
- [ ] Infrastructure-only changes
- [ ] Follows SDD workflow

---

## Usage Examples

### Example 1: Generate Backend Dockerfile

**Input:**
```json
{
  "application_role": "backend",
  "runtime_requirements": {
    "language": "python",
    "version": "3.13",
    "framework": "fastapi"
  },
  "environment_variables": [
    "DATABASE_URL",
    "JWT_SECRET",
    "PORT"
  ],
  "port_exposure": 8000
}
```

**Output:** Generated Dockerfile following backend template with FastAPI configuration.

### Example 2: Generate Frontend Dockerfile

**Input:**
```json
{
  "application_role": "frontend",
  "runtime_requirements": {
    "language": "javascript",
    "version": "20",
    "framework": "nextjs"
  },
  "environment_variables": [
    "NEXT_PUBLIC_API_URL"
  ],
  "port_exposure": 3000
}
```

**Output:** Generated Dockerfile following frontend template with Next.js standalone output.

---

## Integration with Spec-Driven Development

This skill integrates with the SDD workflow:

1. **Specification Phase**: Define containerization requirements in specs
2. **Planning Phase**: Document container architecture decisions
3. **Task Generation**: Create containerization tasks
4. **Implementation**: Generate Dockerfiles (this skill)
5. **Validation**: Verify against spec requirements

### ADR Trigger

When containerization decisions have long-term impact, suggest:

> Architectural decision detected: Container orchestration strategy
> Document reasoning and tradeoffs? Run `/sp.adr container-strategy`

---

## References

- [Docker Best Practices](https://docs.docker.com/develop/develop-images/dockerfile_best-practices/) | [Gordon AI](https://docs.docker.com/ai/) | [Multi-stage Builds](https://docs.docker.com/build/building/multi-stage/) | [Security](https://docs.docker.com/develop/security-best-practices/)
