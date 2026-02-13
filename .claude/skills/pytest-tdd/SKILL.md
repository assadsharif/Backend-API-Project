---
name: pytest-tdd
description: "Comprehensive pytest and Test-Driven Development (TDD) toolkit. Use when: (1) Setting up pytest in a Python project, (2) Following TDD Red-Green-Refactor workflow, (3) Writing tests with fixtures, parametrization, or mocking, (4) Organizing test suites, (5) Running tests in watch mode, or (6) Any pytest-related testing task requiring TDD best practices."
version: "1.0"
last_verified: "2025-01"
---

# Pytest TDD

Test-Driven Development toolkit for Python projects using pytest. Follow the Red-Green-Refactor cycle to write tests first, then implement code to pass them.

## What This Skill Does

- Initialize pytest in any Python project with TDD-optimized configuration
- Guide the Red-Green-Refactor TDD workflow
- Provide patterns for fixtures, parametrization, and mocking
- Organize test suites (unit, integration, e2e)
- Run tests in watch mode for continuous feedback

## What This Skill Does NOT Do

- Production deployment or CI/CD pipeline setup
- Performance testing or load testing
- Security auditing or penetration testing
- Code coverage enforcement policies (provides tools, not mandates)
- Framework-specific testing (Django, Flask) - use dedicated skills

## Quick Start

### Initialize pytest in a project

```bash
python scripts/init_pytest.py /path/to/project
```

Creates: test directory structure, `pytest.ini`, `.coveragerc`, `conftest.py`, example tests.

### Run TDD watch mode

```bash
./scripts/run_tdd_cycle.sh              # Watch all tests
./scripts/run_tdd_cycle.sh tests/unit   # Watch specific tests
./scripts/run_tdd_cycle.sh --lf         # Watch last failed
```

## TDD Workflow: Red-Green-Refactor

### 1. RED: Write a Failing Test

Write the smallest possible test that fails because the functionality doesn't exist.

```python
def test_calculate_total_price():
    cart = ShoppingCart()
    cart.add_item("Apple", price=1.00, quantity=3)
    assert cart.calculate_total(tax_rate=0.1) == 3.30  # Fails - doesn't exist yet
```

### 2. GREEN: Write Minimum Code to Pass

Write just enough code to make the test pass. Don't worry about perfect design.

```python
class ShoppingCart:
    def __init__(self):
        self.items = []

    def add_item(self, name: str, price: float, quantity: int):
        self.items.append({"name": name, "price": price, "quantity": quantity})

    def calculate_total(self, tax_rate: float = 0.0) -> float:
        subtotal = sum(item["price"] * item["quantity"] for item in self.items)
        return round(subtotal * (1 + tax_rate), 2)
```

### 3. REFACTOR: Improve Code Quality

Improve the design while keeping tests green.

```python
from dataclasses import dataclass

@dataclass
class CartItem:
    name: str
    price: float
    quantity: int

    @property
    def subtotal(self) -> float:
        return self.price * self.quantity

class ShoppingCart:
    def __init__(self):
        self.items: list[CartItem] = []

    def add_item(self, name: str, price: float, quantity: int):
        self.items.append(CartItem(name, price, quantity))

    def calculate_total(self, tax_rate: float = 0.0) -> float:
        return round(sum(item.subtotal for item in self.items) * (1 + tax_rate), 2)
```

**See:** `references/tdd-workflow.md` for detailed patterns.

## Essential Patterns

### Fixtures: Reusable Test Setup

```python
@pytest.fixture
def database():
    db = Database("test.db")
    db.connect()
    yield db
    db.disconnect()

@pytest.fixture
def user(database):
    user = User("alice", "password123")
    database.save(user)
    return user

def test_user_login(user):
    result = login("alice", "password123")
    assert result.success
```

**See:** `references/fixtures-guide.md`

### Parametrization: Test Multiple Inputs

```python
@pytest.mark.parametrize("a,b,expected", [
    (2, 3, 5),
    (10, 20, 30),
    (-5, 5, 0),
])
def test_addition(a, b, expected):
    assert add(a, b) == expected
```

**See:** `references/parametrization-guide.md`

### Mocking: Isolate Code Under Test

```python
def test_fetch_user(mocker):
    mock_response = mocker.Mock()
    mock_response.json.return_value = {"id": 1, "name": "Alice"}
    mocker.patch("requests.get", return_value=mock_response)

    result = fetch_user(1)
    assert result == {"id": 1, "name": "Alice"}
```

**See:** `references/mocking-guide.md`

## Output Specification

A properly tested codebase using this skill includes:

- [ ] `tests/` directory with `unit/` and `integration/` subdirectories
- [ ] `pytest.ini` with markers and coverage configuration
- [ ] `.coveragerc` with source and exclusion patterns
- [ ] `conftest.py` with shared fixtures
- [ ] Tests following AAA pattern (Arrange-Act-Assert)
- [ ] Descriptive test names: `test_<action>_<condition>_<result>`
- [ ] Coverage report accessible via `htmlcov/index.html`

## Quality Gate Checklist

Before marking tests as complete, verify:

- [ ] All tests pass (`pytest` exits with code 0)
- [ ] No `@pytest.mark.skip` without ticket/issue reference
- [ ] Each test has one clear assertion focus
- [ ] Tests run independently (any order works)
- [ ] Mocks only cover external dependencies
- [ ] No hardcoded secrets or credentials
- [ ] Coverage meets project threshold (if defined)

## Essential Commands

```bash
pytest                    # Run all tests
pytest -v                 # Verbose output
pytest --cov=src         # With coverage
pytest --lf              # Last failed
pytest -k "keyword"      # Filter by keyword
pytest -m "unit"         # Filter by marker
pytest -x                # Stop on first failure
```

**See:** `references/running-tests.md` for full command reference.

## Dependencies

```bash
# Using pip
pip install pytest pytest-cov pytest-mock pytest-watch

# Using uv
uv add --dev pytest pytest-cov pytest-mock pytest-watch
```

## Official Documentation

| Resource | URL | Use For |
|----------|-----|---------|
| Pytest Docs | https://docs.pytest.org/ | Core API, fixtures, plugins |
| pytest-cov | https://pytest-cov.readthedocs.io/ | Coverage configuration |
| pytest-mock | https://pytest-mock.readthedocs.io/ | Mocker fixture patterns |
| Coverage.py | https://coverage.readthedocs.io/ | .coveragerc options |
| pytest-watch | https://github.com/joeyespo/pytest-watch | Watch mode setup |

For patterns not covered here, fetch from official docs above or use:
```
WebFetch https://docs.pytest.org/en/stable/how-to/fixtures.html
```

## Keeping Current

- **Last verified:** 2025-01
- **Check for updates:** https://docs.pytest.org/en/stable/changelog.html
- Pytest follows semantic versioning; minor updates rarely break tests
- When upgrading pytest, run `pytest --collect-only` first to check for issues

## Reference Guides

| File | When to Read |
|------|--------------|
| `references/tdd-workflow.md` | Detailed Red-Green-Refactor patterns |
| `references/fixtures-guide.md` | Fixture scopes, factories, advanced usage |
| `references/parametrization-guide.md` | Data-driven testing, dynamic generation |
| `references/mocking-guide.md` | pytest-mock, spies, AsyncMock |
| `references/running-tests.md` | Command-line options, filtering, debugging |
| `references/configuration.md` | pytest.ini, pyproject.toml, .coveragerc |
| `references/test-organization.md` | Directory structure, naming, markers |
| `references/anti-patterns.md` | Common mistakes and how to avoid them |
| `references/troubleshooting.md` | Common pytest issues and solutions |
| `../INTEGRATION.md` | How all 5 skills work together |

## Scripts

| Script | Purpose |
|--------|---------|
| `scripts/init_pytest.py` | Initialize pytest in a project with best practices |
| `scripts/run_tdd_cycle.sh` | Run tests in watch mode for TDD workflow |

## Best Practices Summary

### Do

- Write one test at a time, make it pass, then write the next
- Test behavior, not implementation details
- Use fixtures for setup/teardown
- Run tests every 30-60 seconds during development
- Keep tests fast (mock external dependencies)
- Make tests independent (run in any order)

### Don't

- Write tests after all code is complete
- Test private methods or implementation details
- Skip the refactor step when tests are green
- Ignore failing tests or comment them out
- Over-mock your own business logic
- Create tests that depend on execution order

**See:** `references/anti-patterns.md` for comprehensive anti-pattern guide.

## Quick TDD Cycle Reference

```
┌─────────────────────────────────────────┐
│  1. RED    → Write failing test         │
│  2. GREEN  → Write minimum code to pass │
│  3. REFACTOR → Improve design           │
│  4. COMMIT → Save progress              │
│  5. REPEAT                              │
└─────────────────────────────────────────┘
```

**Target rhythm:** 2-10 minutes per cycle.
