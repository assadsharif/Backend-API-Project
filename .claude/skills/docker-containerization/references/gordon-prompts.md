# Gordon (Docker AI Agent) Prompt Patterns

Curated prompts for Docker AI Agent (Gordon) integration. These prompts are suggestions only - they must be executed by the user or operator, not by this skill.

---

## How to Use Gordon

Gordon is Docker's AI-powered assistant integrated into Docker Desktop. Access it via:

1. **Docker Desktop**: Click the Gordon icon or use the command palette
2. **CLI**: `docker ai` command (requires Docker Desktop with AI enabled)
3. **VS Code Extension**: Docker extension with Gordon integration

---

## Dockerfile Analysis Prompts

### Security Audit

```
@gordon analyze this Dockerfile for security issues:

[PASTE DOCKERFILE HERE]

Check for:
1. Running as root (should use non-root user)
2. Hardcoded secrets or credentials
3. Unnecessary packages increasing attack surface
4. Missing security updates
5. Exposed sensitive ports
6. Insecure base image versions

Provide severity rating and remediation steps.
```

### Size Optimization

```
@gordon optimize this Dockerfile to reduce image size:

[PASTE DOCKERFILE HERE]

Suggestions needed:
1. Multi-stage build opportunities
2. Alpine/slim base image alternatives
3. Layer consolidation for RUN commands
4. Unnecessary file removal
5. Build cache optimization
6. .dockerignore improvements

Show before/after estimated sizes.
```

### Build Performance

```
@gordon improve build speed for this Dockerfile:

[PASTE DOCKERFILE HERE]

Analyze:
1. Layer ordering for cache efficiency
2. Parallelizable operations
3. Dependency caching strategies
4. BuildKit features to leverage
5. Multi-stage build optimization

Provide specific line-by-line recommendations.
```

---

## Debugging Prompts

### Container Won't Start

```
@gordon debug: my container exits immediately after starting

Container info:
- Image: [IMAGE_NAME]
- Command: docker run [FULL_COMMAND]
- Error output: [PASTE ERROR]

Help me:
1. Identify the root cause
2. Check CMD/ENTRYPOINT configuration
3. Verify environment variables
4. Review logs for crash reason
5. Suggest fixes
```

### Health Check Failing

```
@gordon debug: container health check keeps failing

Dockerfile HEALTHCHECK:
[PASTE HEALTHCHECK INSTRUCTION]

Container status: unhealthy
Health check output: [PASTE OUTPUT]

Diagnose:
1. Is the health check endpoint correct?
2. Network/port issues inside container?
3. Timing issues (start period too short)?
4. Application startup dependencies?
```

### Permission Denied Errors

```
@gordon debug: getting permission denied errors in container

Error message: [PASTE ERROR]
Dockerfile USER directive: [USER INSTRUCTION]
Affected files/directories: [LIST]

Help me:
1. Identify ownership/permission issues
2. Fix file permissions in Dockerfile
3. Maintain non-root user security
4. Avoid running as root
```

### Network Connectivity Issues

```
@gordon debug: container cannot reach external services

Container: [IMAGE_NAME]
Network mode: [bridge/host/none/custom]
Target service: [URL or IP]
Error: [PASTE ERROR]

Check:
1. DNS resolution inside container
2. Network configuration
3. Firewall/security group rules
4. Proxy configuration
5. Container network isolation
```

### Environment Variable Problems

```
@gordon debug: environment variables not working correctly

Expected: [EXPECTED_BEHAVIOR]
Actual: [ACTUAL_BEHAVIOR]

How I'm setting env vars:
- Dockerfile ENV: [LIST]
- docker run -e: [LIST]
- .env file: [DESCRIBE]

Help identify:
1. Variable scope (build vs runtime)
2. ARG vs ENV usage
3. Shell expansion issues
4. Precedence conflicts
```

---

## Best Practices Prompts

### Production Readiness

```
@gordon review this Dockerfile for production deployment:

[PASTE DOCKERFILE HERE]

Evaluate against:
1. Security hardening (non-root, minimal image)
2. Health checks configured
3. Proper signal handling (PID 1)
4. Graceful shutdown support
5. Log handling (stdout/stderr)
6. Resource limits compatibility
7. Secrets management approach

Rate production-readiness: Not Ready / Needs Work / Ready
```

### Stateless Design Verification

```
@gordon verify this container follows stateless design:

[PASTE DOCKERFILE HERE]

Check for violations:
1. VOLUME instructions for app state
2. Local file writes for persistence
3. In-container databases
4. Session storage on filesystem
5. Cache directories not externalized

Confirm: stateless / has state concerns
```

### 12-Factor App Compliance

```
@gordon check 12-factor compliance for this container setup:

Dockerfile:
[PASTE DOCKERFILE]

docker-compose.yml (if applicable):
[PASTE COMPOSE]

Evaluate:
1. Config via environment variables
2. Stateless processes
3. Port binding
4. Disposability (fast startup/shutdown)
5. Dev/prod parity
6. Log streaming

List violations and fixes.
```

---

## Migration Prompts

### VM to Container

```
@gordon help migrate this application from VM to container:

Current setup:
- OS: [Linux/Windows]
- Runtime: [Python/Node/Java/etc]
- Dependencies: [LIST]
- Config files: [LOCATIONS]
- Data storage: [DESCRIBE]

Generate:
1. Appropriate base image
2. Dockerfile with all dependencies
3. Volume mapping strategy
4. Environment variable list
5. Migration checklist
```

### Update Base Image

```
@gordon help update base image from [OLD_IMAGE] to [NEW_IMAGE]:

Current Dockerfile:
[PASTE DOCKERFILE]

Concerns:
1. Breaking changes in new base
2. Package name differences
3. Path changes
4. User/permission changes
5. Deprecated features

Generate updated Dockerfile with notes.
```

### Monolith to Microservices

```
@gordon help containerize this monolith as microservices:

Current application:
- Language: [LANGUAGE]
- Components: [LIST COMPONENTS]
- Shared dependencies: [LIST]
- Communication: [HTTP/gRPC/etc]

For each service, generate:
1. Individual Dockerfile
2. Shared base image strategy
3. Network configuration
4. Service discovery approach
```

---

## Docker Compose Prompts

### Generate Compose File

```
@gordon generate docker-compose.yml for:

Services:
1. Backend: [FRAMEWORK] on port [PORT]
2. Frontend: [FRAMEWORK] on port [PORT]
3. Database: [TYPE]
4. Cache: [TYPE] (optional)

Requirements:
- Development environment
- Hot reload support
- Shared network
- Volume persistence for data
- Environment variable files
```

### Compose Optimization

```
@gordon optimize this docker-compose.yml:

[PASTE COMPOSE FILE]

Check for:
1. Build context size issues
2. Missing health checks
3. Restart policy configuration
4. Resource limits
5. Network segmentation
6. Security improvements
```

---

## CI/CD Integration Prompts

### GitHub Actions

```
@gordon generate GitHub Actions workflow for:

- Build and push to: [REGISTRY]
- Dockerfile location: [PATH]
- Build args: [LIST]
- Cache strategy: GitHub Actions cache
- Multi-platform: [amd64/arm64]
- Vulnerability scanning: yes/no
```

### Multi-Architecture Build

```
@gordon help build multi-architecture image:

Current Dockerfile: [PASTE OR DESCRIBE]
Target architectures: linux/amd64, linux/arm64

Generate:
1. BuildKit configuration
2. docker buildx commands
3. Base image compatibility notes
4. Testing strategy per architecture
```

---

## Troubleshooting Quick Reference

### Common Issues → Gordon Prompts

| Issue | Prompt |
|-------|--------|
| Image too large | `@gordon why is my image [SIZE]? How to reduce?` |
| Slow builds | `@gordon my build takes [TIME]. Optimize cache.` |
| Can't find command | `@gordon [COMMAND] not found in container` |
| Out of memory | `@gordon container OOM killed. Help diagnose.` |
| Layers not caching | `@gordon why aren't my layers caching?` |
| Wrong file permissions | `@gordon files owned by root, need [USER]` |
| Port not accessible | `@gordon port [PORT] not reachable from host` |
| Build args not working | `@gordon ARG not available at runtime` |

---

## Prompt Best Practices

### Be Specific

**Good:**
```
@gordon why does my Python FastAPI container exit with code 137?
Image: python:3.13-slim
Memory limit: 512MB
Load: 100 concurrent requests
```

**Bad:**
```
@gordon my container crashes
```

### Include Context

**Good:**
```
@gordon analyze this Dockerfile for a FastAPI backend
that connects to PostgreSQL and uses JWT auth:

[DOCKERFILE]
```

**Bad:**
```
@gordon is this Dockerfile good?

[DOCKERFILE]
```

### Ask for Specifics

**Good:**
```
@gordon list the top 3 security issues in this Dockerfile,
with severity and exact line numbers to fix
```

**Bad:**
```
@gordon check security
```
