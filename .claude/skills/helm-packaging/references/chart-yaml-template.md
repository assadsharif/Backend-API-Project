# Chart.yaml Template Reference

Complete Chart.yaml template with all configuration options.

---

## Basic Chart.yaml Template

```yaml
apiVersion: v2
name: {{ .ApplicationName }}
description: A Helm chart for {{ .ApplicationDescription }}
type: application
version: 0.1.0
appVersion: "1.0.0"

# Maintainers
maintainers:
  - name: {{ .MaintainerName }}
    email: {{ .MaintainerEmail }}

# Keywords for search
keywords:
  - {{ .Keywords }}

# Home and sources
home: {{ .HomeURL }}
sources:
  - {{ .SourceURL }}

# Dependencies (if any)
dependencies: []
```

---

## Chart.yaml Fields Reference

| Field | Required | Description |
|-------|----------|-------------|
| `apiVersion` | Yes | Chart API version, use `v2` for Helm 3 |
| `name` | Yes | Chart name (lowercase, hyphenated) |
| `version` | Yes | SemVer 2 chart version |
| `description` | No | Single-sentence description |
| `type` | No | `application` or `library` |
| `appVersion` | No | Application version (informational) |
| `kubeVersion` | No | Kubernetes version constraint |
| `home` | No | Project homepage URL |
| `sources` | No | List of source URLs |
| `keywords` | No | Search keywords |
| `maintainers` | No | List of maintainers |
| `icon` | No | URL to chart icon (SVG/PNG) |
| `deprecated` | No | Mark chart as deprecated |
| `dependencies` | No | List of chart dependencies |

---

## Chart Dependencies

### Basic Dependencies

```yaml
dependencies:
  - name: postgresql
    version: "12.x.x"
    repository: "https://charts.bitnami.com/bitnami"
    condition: postgresql.enabled
```

### Conditional Dependencies

```yaml
dependencies:
  - name: redis
    version: "17.x.x"
    repository: "https://charts.bitnami.com/bitnami"
    condition: redis.enabled
    tags:
      - cache
```

### Local Dependencies

```yaml
dependencies:
  - name: common
    version: "1.x.x"
    repository: "file://../common"
```

### Alias for Multiple Instances

```yaml
dependencies:
  - name: postgresql
    version: "12.x.x"
    repository: "https://charts.bitnami.com/bitnami"
    alias: primary-db
  - name: postgresql
    version: "12.x.x"
    repository: "https://charts.bitnami.com/bitnami"
    alias: replica-db
```

---

## Complete Chart.yaml Example

```yaml
apiVersion: v2
name: myapp
description: A full-stack application with backend API and frontend
type: application

# Chart version (increment for chart changes)
version: 1.2.3

# Application version (your app's version)
appVersion: "2.1.0"

# Kubernetes version constraint
kubeVersion: ">=1.23.0-0"

# Project metadata
home: https://github.com/myorg/myapp
sources:
  - https://github.com/myorg/myapp
icon: https://myapp.example.com/icon.png

# Search keywords
keywords:
  - api
  - web
  - fullstack

# Maintainers
maintainers:
  - name: Platform Team
    email: platform@example.com
    url: https://platform.example.com

# Chart annotations
annotations:
  artifacthub.io/license: Apache-2.0
  artifacthub.io/maintainers: |
    - name: Platform Team
      email: platform@example.com

# Dependencies
dependencies:
  - name: postgresql
    version: "12.12.10"
    repository: "https://charts.bitnami.com/bitnami"
    condition: postgresql.enabled
  - name: redis
    version: "17.15.6"
    repository: "https://charts.bitnami.com/bitnami"
    condition: redis.enabled
    tags:
      - cache
```

---

## Version Guidelines

### Chart Version (version)

- Use [SemVer 2](https://semver.org/)
- Increment for ANY chart changes
- MAJOR: Breaking changes to values.yaml schema
- MINOR: New features, backward compatible
- PATCH: Bug fixes, documentation updates

### App Version (appVersion)

- Reflects your application version
- Informational only (used in NOTES.txt)
- Can be any string

### Kubernetes Version (kubeVersion)

```yaml
# Minimum version
kubeVersion: ">=1.23.0-0"

# Range
kubeVersion: ">=1.23.0-0 <1.28.0-0"

# Multiple constraints
kubeVersion: ">=1.23.0-0, <1.28.0-0"
```

---

## Chart Annotations

### Artifact Hub Annotations

```yaml
annotations:
  # License
  artifacthub.io/license: Apache-2.0

  # Container images used
  artifacthub.io/images: |
    - name: backend
      image: myapp/backend:1.0.0
    - name: frontend
      image: myapp/frontend:1.0.0

  # Links
  artifacthub.io/links: |
    - name: Documentation
      url: https://docs.myapp.example.com
    - name: Support
      url: https://support.myapp.example.com

  # Pre-release
  artifacthub.io/prerelease: "true"

  # Security
  artifacthub.io/containsSecurityUpdates: "true"
```

---

## Best Practices

1. **Always use apiVersion: v2** for Helm 3 charts
2. **Increment chart version** for every change
3. **Use specific dependency versions** (not ranges in production)
4. **Add conditions** to all optional dependencies
5. **Document kubeVersion** requirements
6. **Add maintainer contact** information
7. **Use semantic versioning** consistently
