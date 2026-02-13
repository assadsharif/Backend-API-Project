# Running Tests Guide

Comprehensive guide to running pytest tests in various modes.

## Basic Usage

```bash
# Run all tests
pytest

# Verbose output
pytest -v

# Very verbose (show parameter values)
pytest -vv

# Run specific file
pytest tests/test_users.py

# Run specific test
pytest tests/test_users.py::test_login

# Run specific class
pytest tests/test_users.py::TestAuthentication

# Show print statements
pytest -s
```

## With Coverage

```bash
# Run with coverage
pytest --cov=src

# Coverage report in terminal
pytest --cov=src --cov-report=term-missing

# Generate HTML coverage report
pytest --cov=src --cov-report=html

# Open coverage report
open htmlcov/index.html

# Fail if coverage below threshold
pytest --cov=src --cov-fail-under=80
```

## Filtering Tests

```bash
# Run last failed tests
pytest --lf

# Run failed tests first
pytest --ff

# Run by keyword
pytest -k "login"
pytest -k "not slow"
pytest -k "login and not integration"

# Run by marker
pytest -m "unit"
pytest -m "integration and not slow"

# Stop on first failure
pytest -x

# Stop after N failures
pytest --maxfail=3
```

## Watch Mode (TDD)

For continuous test running during development:

```bash
# Use provided script
./scripts/run_tdd_cycle.sh

# Or install pytest-watch
pip install pytest-watch
ptw

# Watch with coverage
ptw -- --cov=src

# Watch specific directory
ptw tests/unit/

# Watch with specific options
ptw -- -v --tb=short
```

## Output Formatting

```bash
# Short traceback
pytest --tb=short

# Long traceback
pytest --tb=long

# Line-by-line traceback
pytest --tb=line

# No traceback
pytest --tb=no

# Only first and last frames
pytest --tb=native
```

## Parallel Execution

```bash
# Install pytest-xdist
pip install pytest-xdist

# Run with N workers
pytest -n auto  # Auto-detect CPUs
pytest -n 4     # 4 workers

# Distribute by file
pytest -n auto --dist=loadfile
```

## Debugging

```bash
# Drop into debugger on failure
pytest --pdb

# Drop into debugger on first failure only
pytest --pdb -x

# Start debugger at test start
pytest --trace

# Show local variables in tracebacks
pytest -l
```

## Common Combinations

```bash
# TDD development
pytest -v --tb=short --lf

# CI pipeline
pytest --cov=src --cov-fail-under=80 -v

# Quick check
pytest -x -q

# Full test run with coverage
pytest --cov=src --cov-report=html --cov-report=term-missing -v
```

## See Also

- `tdd-workflow.md` - TDD Red-Green-Refactor cycle
- `fixtures-guide.md` - Fixture patterns
- `configuration.md` - pytest.ini and .coveragerc setup
