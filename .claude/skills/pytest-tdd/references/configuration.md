# Pytest Configuration Guide

Complete configuration reference for pytest and coverage.

## pytest.ini

The main pytest configuration file:

```ini
[pytest]
# Test discovery patterns
python_files = test_*.py *_test.py
python_classes = Test*
python_functions = test_*

# Output options
addopts =
    -v
    --strict-markers
    --tb=short
    --cov=src
    --cov-report=term-missing
    --cov-report=html
    --cov-branch

# Minimum coverage percentage (uncomment to enable)
# --cov-fail-under=80

# Test paths
testpaths = tests

# Markers for organizing tests
markers =
    unit: Unit tests
    integration: Integration tests
    slow: Slow-running tests
    wip: Work in progress tests

# Ignore paths
norecursedirs = .git .tox dist build *.egg __pycache__
```

## pyproject.toml Alternative

If using pyproject.toml:

```toml
[tool.pytest.ini_options]
python_files = ["test_*.py", "*_test.py"]
python_classes = ["Test*"]
python_functions = ["test_*"]
testpaths = ["tests"]
addopts = "-v --strict-markers --tb=short"
markers = [
    "unit: Unit tests",
    "integration: Integration tests",
    "slow: Slow-running tests",
    "wip: Work in progress tests",
]
```

## .coveragerc

Coverage configuration file:

```ini
[run]
source = src
branch = True
omit =
    */tests/*
    */test_*
    */__pycache__/*
    */site-packages/*
    */venv/*
    */.venv/*

[report]
precision = 2
show_missing = True
skip_covered = False

exclude_lines =
    pragma: no cover
    def __repr__
    raise AssertionError
    raise NotImplementedError
    if __name__ == .__main__.:
    if TYPE_CHECKING:
    @abstractmethod
    @abc.abstractmethod

[html]
directory = htmlcov
```

## Configuration Options

### addopts

Common options to include by default:

| Option | Purpose |
|--------|---------|
| `-v` | Verbose output |
| `--strict-markers` | Error on unknown markers |
| `--tb=short` | Short tracebacks |
| `--cov=src` | Enable coverage for src/ |
| `--cov-branch` | Include branch coverage |

### Markers

Register custom markers to avoid warnings:

```ini
markers =
    unit: Fast, isolated unit tests
    integration: Tests requiring external services
    slow: Tests taking >1 second
    wip: Work in progress (skip in CI)
    smoke: Quick sanity checks
```

### Test Discovery

Customize how pytest finds tests:

```ini
# Find tests in these directories
testpaths = tests src

# Match these file patterns
python_files = test_*.py *_test.py check_*.py

# Match these class patterns
python_classes = Test* Check*

# Match these function patterns
python_functions = test_* check_*
```

## Environment Variables

Set environment variables for tests:

```ini
[pytest]
env =
    DATABASE_URL=sqlite:///:memory:
    DEBUG=true
    API_KEY=test_key
```

Requires `pytest-env` plugin:
```bash
pip install pytest-env
```

## Plugins Configuration

### pytest-xdist (Parallel)

```ini
addopts = -n auto
```

### pytest-timeout

```ini
timeout = 30
timeout_method = thread
```

### pytest-randomly

```ini
randomly_seed = last
randomly_dont_shuffle = true
```

## See Also

- `running-tests.md` - Command-line usage
- `fixtures-guide.md` - Fixture configuration
- `test-organization.md` - Directory structure
