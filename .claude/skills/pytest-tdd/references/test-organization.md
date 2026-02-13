# Test Organization Guide

Best practices for organizing pytest test suites.

## Directory Structure

### Standard Layout

```
project/
├── src/
│   ├── __init__.py
│   ├── models.py
│   ├── services.py
│   └── utils.py
├── tests/
│   ├── __init__.py
│   ├── conftest.py          # Project-wide fixtures
│   ├── unit/
│   │   ├── __init__.py
│   │   ├── conftest.py      # Unit test fixtures
│   │   ├── test_models.py
│   │   └── test_utils.py
│   ├── integration/
│   │   ├── __init__.py
│   │   ├── conftest.py      # Integration fixtures
│   │   └── test_api.py
│   └── fixtures/
│       ├── sample_data.json
│       └── test_config.yaml
├── pytest.ini
└── .coveragerc
```

### Flat Layout (Small Projects)

```
project/
├── mymodule.py
├── tests/
│   ├── conftest.py
│   ├── test_mymodule.py
│   └── test_helpers.py
└── pytest.ini
```

## conftest.py

Place shared fixtures in `conftest.py` for automatic discovery:

```python
# tests/conftest.py - Available to ALL tests
import pytest

@pytest.fixture(scope="session")
def database():
    """Session-wide database connection."""
    db = Database()
    db.connect()
    yield db
    db.disconnect()

# tests/unit/conftest.py - Available to unit tests only
@pytest.fixture
def mock_api():
    """Mock API for unit tests."""
    return MockAPI()

# tests/integration/conftest.py - Available to integration tests only
@pytest.fixture
def live_api():
    """Real API connection for integration tests."""
    return RealAPI()
```

## Test Naming

### Files

```
test_*.py      # Preferred
*_test.py      # Alternative
```

### Classes

```python
class TestUserAuthentication:
    """Group related tests."""
    pass

class TestUserRegistration:
    """Another group."""
    pass
```

### Functions

```python
# Good: Descriptive names
def test_user_can_login_with_valid_credentials():
    ...

def test_user_cannot_login_with_invalid_password():
    ...

def test_user_receives_error_when_email_already_exists():
    ...

# Avoid: Vague names
def test_login():
    ...

def test_fail():
    ...
```

## Markers

Organize tests with markers:

```python
import pytest

@pytest.mark.unit
def test_user_validation():
    """Fast, isolated test."""
    ...

@pytest.mark.integration
def test_database_query():
    """Requires database connection."""
    ...

@pytest.mark.slow
def test_full_migration():
    """Takes >30 seconds."""
    ...

@pytest.mark.wip
def test_new_feature():
    """Work in progress."""
    ...
```

### Running by Marker

```bash
# Run only unit tests
pytest -m unit

# Run integration tests, skip slow ones
pytest -m "integration and not slow"

# Skip work in progress
pytest -m "not wip"
```

### Registering Markers

In `pytest.ini`:

```ini
[pytest]
markers =
    unit: Unit tests (fast, isolated)
    integration: Integration tests (require services)
    slow: Slow tests (>1 second)
    wip: Work in progress
    smoke: Quick sanity checks
```

## Test Categories

### Unit Tests

```python
# tests/unit/test_calculator.py
"""Unit tests: fast, isolated, no external dependencies."""

def test_add():
    assert add(2, 3) == 5

def test_divide():
    assert divide(10, 2) == 5.0

def test_divide_by_zero():
    with pytest.raises(ValueError):
        divide(10, 0)
```

### Integration Tests

```python
# tests/integration/test_database.py
"""Integration tests: test component interactions."""

def test_save_and_retrieve_user(database):
    user = User("alice")
    database.save(user)

    retrieved = database.get("alice")
    assert retrieved.name == "alice"
```

### End-to-End Tests

```python
# tests/e2e/test_user_journey.py
"""E2E tests: full user flows."""

def test_complete_registration_flow(browser):
    browser.get("/register")
    browser.fill("email", "user@example.com")
    browser.fill("password", "secure123")
    browser.click("submit")

    assert browser.current_url == "/dashboard"
```

## Fixture Organization

### Scope Hierarchy

```python
# tests/conftest.py
@pytest.fixture(scope="session")
def app():
    """Application instance (once per session)."""
    return create_app()

@pytest.fixture(scope="module")
def database(app):
    """Database connection (once per file)."""
    return app.get_db()

@pytest.fixture(scope="function")
def user(database):
    """Test user (fresh for each test)."""
    user = User("test_user")
    database.save(user)
    yield user
    database.delete(user)
```

### Fixture Files

For complex fixtures, create dedicated files:

```
tests/
├── conftest.py
├── fixtures/
│   ├── __init__.py
│   ├── database.py    # Database fixtures
│   ├── users.py       # User fixtures
│   └── mocks.py       # Mock fixtures
```

Then import in conftest.py:

```python
# tests/conftest.py
from .fixtures.database import *
from .fixtures.users import *
from .fixtures.mocks import *
```

## Best Practices

### 1. One Assert Per Test (When Possible)

```python
# Good: Focused tests
def test_user_has_correct_name():
    user = User("Alice")
    assert user.name == "Alice"

def test_user_has_correct_default_role():
    user = User("Alice")
    assert user.role == "member"
```

### 2. Arrange-Act-Assert Pattern

```python
def test_user_registration():
    # Arrange
    data = {"name": "Alice", "email": "alice@example.com"}

    # Act
    user = register_user(data)

    # Assert
    assert user.name == "Alice"
    assert user.email == "alice@example.com"
```

### 3. Independent Tests

Each test should be able to run in any order:

```python
# Good: Independent
def test_create_user():
    user = User("alice")
    assert user.name == "alice"

def test_delete_user():
    user = User("bob")  # Creates its own user
    user.delete()
    assert user.is_deleted

# Bad: Dependent
user = None

def test_create():
    global user
    user = User("alice")

def test_delete():
    user.delete()  # Depends on test_create running first!
```

## See Also

- `fixtures-guide.md` - Comprehensive fixture patterns
- `configuration.md` - pytest.ini setup
- `tdd-workflow.md` - TDD cycle
