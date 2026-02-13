# Venv Best Practices

## Project Layout Convention

```
project/
├── .venv/              # Virtual environment (gitignored)
├── requirements.txt    # Pinned production dependencies
├── requirements-dev.txt # Development/test dependencies
├── pyproject.toml      # Modern project metadata
└── .gitignore          # Must include .venv/
```

## Dependency Management

### Pin Versions for Reproducibility

```
# requirements.txt - GOOD (pinned)
fastapi==0.100.0
uvicorn==0.23.0
pydantic==2.0.0

# requirements.txt - BAD (unpinned)
fastapi
uvicorn
pydantic
```

### Separate Dev Dependencies

```
# requirements-dev.txt
-r requirements.txt
pytest==7.4.0
pytest-asyncio==0.21.0
httpx==0.27.0
ruff==0.1.0
```

## Naming Conventions

| Convention | Path | Used By |
|-----------|------|---------|
| `.venv` | `.venv/` | Most modern tools (VS Code, PyCharm auto-detect) |
| `venv` | `venv/` | Python docs default |
| Named | `~/.venvs/project-name/` | Centralized management |

**Recommendation**: Use `.venv` in project root. Most IDEs auto-detect it.

## Security

- Never commit `.venv/` to git
- Never store secrets in venv activation scripts
- Use `.env` files for environment variables (with python-dotenv)
- Audit dependencies periodically: `pip audit`

## Performance

- Use `pip install --no-cache-dir` in CI/CD (smaller image layers)
- Use `pip install --compile` for production (pre-compile .pyc files)
- Consider `uv` as faster pip alternative: `uv pip install -r requirements.txt`

## Gitignore Pattern

```gitignore
# Virtual environments
.venv/
venv/
ENV/
env/
```
