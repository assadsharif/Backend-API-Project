# Pytest Parametrization Guide

## What is Parametrization?

Parametrization allows you to run the same test with different input values, reducing code duplication and improving test coverage.

**Without parametrization:**
```python
def test_add_1_and_2():
    assert add(1, 2) == 3

def test_add_5_and_7():
    assert add(5, 7) == 12

def test_add_negative_numbers():
    assert add(-1, -1) == -2

def test_add_zero():
    assert add(0, 0) == 0
```

**With parametrization:**
```python
@pytest.mark.parametrize("a,b,expected", [
    (1, 2, 3),
    (5, 7, 12),
    (-1, -1, -2),
    (0, 0, 0),
])
def test_add(a, b, expected):
    assert add(a, b) == expected
```

## Basic Parametrization

### Single Parameter

```python
import pytest

@pytest.mark.parametrize("number", [1, 2, 3, 4, 5])
def test_is_positive(number):
    assert number > 0

# Runs 5 tests:
# test_is_positive[1] PASSED
# test_is_positive[2] PASSED
# test_is_positive[3] PASSED
# test_is_positive[4] PASSED
# test_is_positive[5] PASSED
```

### Multiple Parameters

```python
@pytest.mark.parametrize("a,b,expected", [
    (2, 3, 5),
    (10, 20, 30),
    (-5, 5, 0),
    (0, 0, 0),
])
def test_addition(a, b, expected):
    result = add(a, b)
    assert result == expected

# Runs 4 tests:
# test_addition[2-3-5] PASSED
# test_addition[10-20-30] PASSED
# test_addition[-5-5-0] PASSED
# test_addition[0-0-0] PASSED
```

### Named Parameters

Use a list of tuples for better readability:

```python
@pytest.mark.parametrize("input,expected", [
    ("hello", "HELLO"),
    ("World", "WORLD"),
    ("123", "123"),
    ("", ""),
])
def test_to_uppercase(input, expected):
    assert to_uppercase(input) == expected
```

## Custom Test IDs

Add readable test names using `ids` parameter.

### String IDs

```python
@pytest.mark.parametrize("number,expected", [
    (1, True),
    (2, True),
    (3, False),
    (4, True),
], ids=["one_is_even", "two_is_even", "three_is_odd", "four_is_even"])
def test_is_even(number, expected):
    assert is_even(number) == expected

# Output:
# test_is_even[one_is_even] PASSED
# test_is_even[two_is_even] PASSED
# test_is_even[three_is_odd] PASSED
# test_is_even[four_is_even] PASSED
```

### Function-Generated IDs

```python
def idfn(val):
    """Generate readable ID from test value."""
    if isinstance(val, dict):
        return f"user_{val.get('name', 'unknown')}"
    return str(val)

@pytest.mark.parametrize("user_data", [
    {"name": "alice", "age": 30},
    {"name": "bob", "age": 25},
    {"name": "charlie", "age": 35},
], ids=idfn)
def test_user_creation(user_data):
    user = create_user(user_data)
    assert user.name == user_data["name"]

# Output:
# test_user_creation[user_alice] PASSED
# test_user_creation[user_bob] PASSED
# test_user_creation[user_charlie] PASSED
```

## Multiple Parametrize Decorators

Stack decorators to create a test matrix (Cartesian product).

```python
@pytest.mark.parametrize("x", [1, 2])
@pytest.mark.parametrize("y", [3, 4])
def test_multiplication(x, y):
    result = x * y
    assert result > 0

# Runs 4 tests (2 × 2):
# test_multiplication[3-1] PASSED  (1 * 3)
# test_multiplication[3-2] PASSED  (2 * 3)
# test_multiplication[4-1] PASSED  (1 * 4)
# test_multiplication[4-2] PASSED  (2 * 4)
```

### Real-World Example

```python
@pytest.mark.parametrize("browser", ["chrome", "firefox", "safari"])
@pytest.mark.parametrize("viewport", ["mobile", "tablet", "desktop"])
def test_responsive_design(browser, viewport):
    # Tests all browser × viewport combinations
    # 3 browsers × 3 viewports = 9 tests
    page = load_page(browser, viewport)
    assert page.is_responsive()
```

## Parametrizing Fixtures

### Basic Fixture Parametrization

```python
@pytest.fixture(params=["sqlite", "postgres", "mysql"])
def database(request):
    """Test with multiple database backends."""
    db_type = request.param
    db = Database(db_type)
    db.connect()
    yield db
    db.disconnect()

def test_user_query(database):
    # Runs 3 times, once for each database type
    users = database.query("SELECT * FROM users")
    assert len(users) >= 0
```

### Fixture with IDs

```python
@pytest.fixture(params=[
    "en_US",
    "es_ES",
    "fr_FR",
    "de_DE",
], ids=["english", "spanish", "french", "german"])
def locale(request):
    return request.param

def test_translation(locale):
    translator = Translator(locale)
    assert translator.translate("hello") != "hello"

# Output:
# test_translation[english] PASSED
# test_translation[spanish] PASSED
# test_translation[french] PASSED
# test_translation[german] PASSED
```

## Indirect Parametrization

Transform parameters before passing to fixtures.

```python
@pytest.fixture
def user(request):
    """Create user from username."""
    username = request.param
    user = User(username)
    user.save()
    yield user
    user.delete()

@pytest.mark.parametrize("user", ["alice", "bob", "charlie"], indirect=True)
def test_user_login(user):
    # user is the User object, not the string
    result = user.login()
    assert result.success
```

### Multiple Indirect Parameters

```python
@pytest.fixture
def database(request):
    db = Database(request.param)
    db.connect()
    yield db
    db.disconnect()

@pytest.fixture
def user(request):
    return User(request.param)

@pytest.mark.parametrize("database,user", [
    ("sqlite", "alice"),
    ("postgres", "bob"),
], indirect=True)  # Both parameters use fixtures
def test_save_user(database, user):
    database.save(user)
    assert database.get(user.name) is not None
```

### Selective Indirect

```python
@pytest.fixture
def user(request):
    return User(request.param)

@pytest.mark.parametrize("user,expected_role", [
    ("alice", "admin"),
    ("bob", "user"),
], indirect=["user"])  # Only user is indirect
def test_user_role(user, expected_role):
    # user is a User object (indirect)
    # expected_role is a string (direct)
    assert user.role == expected_role
```

## Edge Cases and Boundary Values

Test boundary conditions systematically.

```python
@pytest.mark.parametrize("age,valid", [
    (-1, False),     # Below minimum
    (0, True),       # Minimum
    (1, True),       # Just above minimum
    (17, True),      # Just below boundary
    (18, True),      # Boundary
    (19, True),      # Just above boundary
    (120, True),     # Maximum
    (121, False),    # Above maximum
])
def test_age_validation(age, valid):
    if valid:
        assert validate_age(age) is True
    else:
        with pytest.raises(ValueError):
            validate_age(age)
```

## Testing Exceptions

```python
@pytest.mark.parametrize("dividend,divisor,expected_exception", [
    (10, 2, None),           # Valid division
    (10, 0, ZeroDivisionError),  # Division by zero
    ("10", 2, TypeError),    # Invalid type
    (10, "2", TypeError),    # Invalid type
])
def test_division(dividend, divisor, expected_exception):
    if expected_exception is None:
        result = divide(dividend, divisor)
        assert isinstance(result, (int, float))
    else:
        with pytest.raises(expected_exception):
            divide(dividend, divisor)
```

## Complex Data Structures

### Dictionaries

```python
@pytest.mark.parametrize("user_data", [
    {"username": "alice", "email": "alice@example.com", "age": 30},
    {"username": "bob", "email": "bob@example.com", "age": 25},
    {"username": "charlie", "email": "charlie@example.com", "age": 35},
])
def test_user_registration(user_data):
    user = register_user(**user_data)
    assert user.username == user_data["username"]
    assert user.email == user_data["email"]
```

### Custom Objects

```python
from dataclasses import dataclass

@dataclass
class TestCase:
    input: str
    expected: str
    description: str

@pytest.mark.parametrize("test_case", [
    TestCase("hello", "HELLO", "lowercase to uppercase"),
    TestCase("WORLD", "WORLD", "already uppercase"),
    TestCase("MiXeD", "MIXED", "mixed case"),
], ids=lambda tc: tc.description)
def test_to_uppercase(test_case):
    result = to_uppercase(test_case.input)
    assert result == test_case.expected
```

## Conditional Parametrization

### Skip Parameters Conditionally

```python
import sys

@pytest.mark.parametrize("operation", [
    "read",
    "write",
    pytest.param("symlink", marks=pytest.mark.skipif(
        sys.platform == "win32",
        reason="Symlinks not supported on Windows"
    )),
])
def test_file_operations(operation, tmp_path):
    if operation == "read":
        assert can_read(tmp_path)
    elif operation == "write":
        assert can_write(tmp_path)
    elif operation == "symlink":
        assert can_symlink(tmp_path)
```

### Mark Parameters

```python
@pytest.mark.parametrize("database", [
    "sqlite",
    "postgres",
    pytest.param("oracle", marks=pytest.mark.slow),
])
def test_query_performance(database):
    db = Database(database)
    result = db.query("SELECT * FROM users")
    assert result is not None

# Run fast tests only:
# pytest -m "not slow"
```

## Generating Parameters Dynamically

### Using Functions

```python
def generate_test_cases():
    """Generate test cases dynamically."""
    cases = []
    for i in range(1, 11):
        cases.append((i, i * 2, i * 2))  # (a, b, expected)
    return cases

@pytest.mark.parametrize("a,b,expected", generate_test_cases())
def test_multiplication(a, b, expected):
    assert a * b == expected
```

### From External Files

```python
import json
from pathlib import Path

def load_test_cases():
    """Load test cases from JSON file."""
    test_file = Path(__file__).parent / "test_data.json"
    with open(test_file) as f:
        return json.load(f)

@pytest.mark.parametrize("test_case", load_test_cases())
def test_api_responses(test_case):
    response = call_api(test_case["endpoint"])
    assert response.status_code == test_case["expected_status"]
    assert response.json() == test_case["expected_data"]
```

**test_data.json:**
```json
[
  {
    "endpoint": "/users",
    "expected_status": 200,
    "expected_data": {"users": []}
  },
  {
    "endpoint": "/posts",
    "expected_status": 200,
    "expected_data": {"posts": []}
  }
]
```

### From CSV Files

```python
import csv
from pathlib import Path

def load_csv_test_cases():
    """Load test cases from CSV."""
    test_file = Path(__file__).parent / "test_cases.csv"
    with open(test_file) as f:
        reader = csv.DictReader(f)
        return list(reader)

@pytest.mark.parametrize("case", load_csv_test_cases())
def test_validation(case):
    is_valid = validate(case["input"])
    expected = case["expected"] == "true"
    assert is_valid == expected
```

**test_cases.csv:**
```csv
input,expected,description
alice@example.com,true,valid email
not-an-email,false,invalid email
@example.com,false,missing local part
```

## Class-Level Parametrization

Apply parameters to all methods in a test class.

```python
@pytest.mark.parametrize("browser", ["chrome", "firefox"])
class TestWebsite:
    def test_homepage(self, browser):
        # Runs twice: chrome, firefox
        page = load_page("/", browser)
        assert page.title == "Home"

    def test_login_page(self, browser):
        # Runs twice: chrome, firefox
        page = load_page("/login", browser)
        assert "Login" in page.title

# Total: 4 tests (2 methods × 2 browsers)
```

## Parametrization Best Practices

### 1. Descriptive Test IDs

Make test failures easy to diagnose.

```python
# Good: Clear test IDs
@pytest.mark.parametrize("input,expected", [
    ("valid@email.com", True),
    ("invalid", False),
], ids=["valid_email", "invalid_email"])
def test_email_validation(input, expected):
    assert is_valid_email(input) == expected

# Avoid: Generic IDs
@pytest.mark.parametrize("input,expected", [
    ("valid@email.com", True),
    ("invalid", False),
])
# Test output: test_email_validation[valid@email.com-True]
# Hard to read!
```

### 2. Group Related Tests

```python
# Good: Group related parameter sets
@pytest.mark.parametrize("num,expected", [
    # Positive numbers
    (1, True),
    (5, True),
    (100, True),
    # Negative numbers
    (-1, False),
    (-5, False),
    # Zero
    (0, False),
])
def test_is_positive(num, expected):
    assert is_positive(num) == expected
```

### 3. Don't Overuse Parametrization

```python
# Good: Simple, focused test
def test_user_creation():
    user = User("alice", 30)
    assert user.name == "alice"
    assert user.age == 30

# Avoid: Over-parametrized for single case
@pytest.mark.parametrize("name,age", [("alice", 30)])
def test_user_creation(name, age):
    user = User(name, age)
    assert user.name == name
    assert user.age == age
```

### 4. Keep Parameters Simple

```python
# Good: Simple parameter values
@pytest.mark.parametrize("status_code", [200, 201, 204])
def test_successful_response(status_code):
    response = Response(status_code)
    assert response.is_success()

# Avoid: Complex nested structures in parameters
@pytest.mark.parametrize("config", [
    {"nested": {"deeply": {"value": 1}}},  # Hard to read
])
def test_config(config):
    ...
```

## Common Patterns

### Testing Multiple Implementations

```python
@pytest.mark.parametrize("sort_function", [
    bubble_sort,
    quick_sort,
    merge_sort,
])
def test_sorting_algorithm(sort_function):
    data = [3, 1, 4, 1, 5, 9, 2, 6]
    result = sort_function(data)
    assert result == [1, 1, 2, 3, 4, 5, 6, 9]
```

### Testing CRUD Operations

```python
@pytest.mark.parametrize("operation,expected_count", [
    ("create", 1),
    ("read", 1),
    ("update", 1),
    ("delete", 0),
])
def test_user_crud(operation, expected_count, database):
    user = User("alice")

    if operation == "create":
        database.save(user)
    elif operation == "read":
        database.save(user)
        retrieved = database.get(user.id)
        assert retrieved.name == "alice"
    elif operation == "update":
        database.save(user)
        user.name = "bob"
        database.update(user)
        retrieved = database.get(user.id)
        assert retrieved.name == "bob"
    elif operation == "delete":
        database.save(user)
        database.delete(user)

    assert database.count_users() == expected_count
```

### HTTP Status Codes

```python
@pytest.mark.parametrize("status_code,expected_category", [
    (200, "success"),
    (201, "success"),
    (301, "redirect"),
    (400, "client_error"),
    (404, "client_error"),
    (500, "server_error"),
])
def test_http_status_category(status_code, expected_category):
    response = Response(status_code)
    assert response.category == expected_category
```

## Debugging Parametrized Tests

### Run Single Parameter Set

```bash
# Run only the first parameter set
pytest test_file.py::test_name[param0]

# Run specific parameter by ID
pytest test_file.py::test_name[valid_email]
```

### Verbose Output

```bash
# Show all parameter combinations
pytest -v test_file.py

# Show parameter values in output
pytest -vv test_file.py
```

### Print Parameter Values

```python
@pytest.mark.parametrize("x,y", [(1, 2), (3, 4)])
def test_addition(x, y):
    print(f"Testing with x={x}, y={y}")  # Shown with -s flag
    assert x + y > 0
```

```bash
pytest -s test_file.py  # Show print statements
```

## See Also

- `fixtures-guide.md` - Fixture patterns and best practices
- `tdd-workflow.md` - Red-Green-Refactor cycle
- `mocking-guide.md` - Mocking and patching patterns
