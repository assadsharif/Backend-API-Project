# Pytest Troubleshooting Guide

Common issues and solutions when running pytest.

## Tests Not Discovered

### Symptoms
- `collected 0 items`
- Tests exist but don't run

### Solutions

```bash
# Check naming conventions
# Files must be: test_*.py or *_test.py
# Functions must be: test_*
# Classes must be: Test*

# Verify pytest can see the files
pytest --collect-only

# Check for __init__.py in test directories
touch tests/__init__.py
touch tests/unit/__init__.py

# Verify testpaths in pytest.ini
[pytest]
testpaths = tests
```

## Import Errors

### Symptoms
- `ModuleNotFoundError`
- `ImportError: cannot import name`

### Solutions

```bash
# Install package in development mode
pip install -e .

# Or add src to PYTHONPATH
export PYTHONPATH="${PYTHONPATH}:${PWD}/src"

# Or use conftest.py to fix imports
# tests/conftest.py
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))
```

## Fixture Not Found

### Symptoms
- `fixture 'xxx' not found`

### Solutions

```python
# Ensure fixture is in conftest.py (not test file)
# tests/conftest.py
import pytest

@pytest.fixture
def my_fixture():
    return "data"

# Ensure conftest.py is in correct directory
# tests/conftest.py      <- Available to all tests
# tests/unit/conftest.py <- Available to unit tests only

# Check fixture scope
@pytest.fixture(scope="session")  # Once per session
@pytest.fixture(scope="module")   # Once per file
@pytest.fixture(scope="function") # Each test (default)
```

## Tests Affecting Each Other

### Symptoms
- Tests pass individually but fail together
- Random test failures

### Solutions

```python
# Use fresh fixtures per test
@pytest.fixture
def database():
    db = Database()
    db.reset()  # Clean state
    yield db
    db.cleanup()

# Run tests in random order to detect dependencies
pip install pytest-randomly
pytest

# Isolate tests
pytest -x  # Stop on first failure to identify issue
```

## Slow Tests

### Symptoms
- Test suite takes too long
- CI timeouts

### Solutions

```bash
# Profile test duration
pytest --durations=10

# Run only fast tests
pytest -m "not slow"

# Parallelize
pip install pytest-xdist
pytest -n auto

# Use lighter fixtures
@pytest.fixture(scope="session")  # Reuse expensive setup
def database():
    return create_database()
```

## Coverage Not Working

### Symptoms
- Coverage shows 0%
- Wrong files covered

### Solutions

```bash
# Specify source directory
pytest --cov=src --cov-report=term-missing

# Check .coveragerc configuration
[run]
source = src
omit = */tests/*

# Ensure source is importable
pip install -e .
```

## Mocks Not Working

### Symptoms
- Mock not applied
- Original function still called

### Solutions

```python
# Patch where it's USED, not where it's DEFINED
# mymodule.py
from requests import get
def fetch():
    return get(url)

# test_mymodule.py
# BAD: Patching where defined
mocker.patch("requests.get")

# GOOD: Patching where used
mocker.patch("mymodule.get")
```

## Async Test Issues

### Symptoms
- `RuntimeWarning: coroutine was never awaited`

### Solutions

```bash
# Install pytest-asyncio
pip install pytest-asyncio

# Mark async tests
@pytest.mark.asyncio
async def test_async_function():
    result = await async_function()
    assert result == expected

# Or configure globally in pytest.ini
[pytest]
asyncio_mode = auto
```

## Parametrize Errors

### Symptoms
- `TypeError: argument of type 'int' is not iterable`

### Solutions

```python
# Wrong: Values must be iterable
@pytest.mark.parametrize("x", 1, 2, 3)  # Error!

# Correct: Use list
@pytest.mark.parametrize("x", [1, 2, 3])

# Multiple parameters: tuple list
@pytest.mark.parametrize("x,y,expected", [
    (1, 2, 3),
    (2, 3, 5),
])
def test_add(x, y, expected):
    assert x + y == expected
```

## Environment Issues

### Symptoms
- Tests pass locally, fail in CI
- Different behavior across machines

### Solutions

```bash
# Pin dependencies
pip freeze > requirements-test.txt

# Use same Python version
python --version

# Check environment variables
pytest -v  # Verbose output

# Use tox for multiple environments
pip install tox
tox
```

## Quick Debugging Commands

```bash
# Verbose output
pytest -v

# Very verbose
pytest -vv

# Show print statements
pytest -s

# Drop into debugger on failure
pytest --pdb

# Stop on first failure
pytest -x

# Run last failed
pytest --lf

# Show local variables in traceback
pytest -l

# Collect without running
pytest --collect-only
```
