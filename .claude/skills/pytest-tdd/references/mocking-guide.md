# Pytest Mocking Guide

## What is Mocking?

Mocking replaces real objects with test doubles that simulate their behavior. This allows you to:
- Test code in isolation
- Avoid slow external dependencies (databases, APIs, file systems)
- Control test conditions precisely
- Verify interactions between objects

## Pytest-Mock vs unittest.mock

Pytest provides two ways to mock:

1. **pytest-mock** - Pytest plugin (recommended)
2. **unittest.mock** - Standard library (works but more verbose)

This guide focuses on **pytest-mock** with references to unittest.mock where relevant.

### Installation

```bash
pip install pytest-mock
# or
uv add --dev pytest-mock
```

## Basic Mocking with mocker Fixture

The `mocker` fixture provides all mocking functionality.

### Simple Mock

```python
def test_api_call(mocker):
    # Create a mock object
    mock_response = mocker.Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"data": "test"}

    # Use the mock
    assert mock_response.status_code == 200
    assert mock_response.json() == {"data": "test"}
```

### Mocking Functions

```python
# Source code: api.py
import requests

def fetch_user(user_id):
    response = requests.get(f"https://api.example.com/users/{user_id}")
    return response.json()

# Test code
def test_fetch_user(mocker):
    # Mock the requests.get function
    mock_get = mocker.patch("requests.get")
    mock_get.return_value.json.return_value = {"id": 1, "name": "Alice"}

    result = fetch_user(1)

    assert result == {"id": 1, "name": "Alice"}
    mock_get.assert_called_once_with("https://api.example.com/users/1")
```

### Mocking Methods

```python
# Source code: database.py
class Database:
    def query(self, sql):
        # Expensive database operation
        ...

# Test code
def test_user_count(mocker):
    db = Database()

    # Mock the query method
    mocker.patch.object(db, "query", return_value=[{"count": 42}])

    result = db.query("SELECT COUNT(*) FROM users")

    assert result == [{"count": 42}]
```

## Patching

### patch() - Basic Usage

```python
def test_read_file(mocker):
    # Mock the built-in open() function
    mock_open = mocker.patch("builtins.open", mocker.mock_open(read_data="test data"))

    with open("file.txt") as f:
        content = f.read()

    assert content == "test data"
    mock_open.assert_called_once_with("file.txt")
```

### patch.object() - Mocking Specific Objects

```python
class EmailService:
    def send(self, to, subject, body):
        # Send actual email
        ...

def test_send_notification(mocker):
    service = EmailService()

    # Mock only the send method
    mock_send = mocker.patch.object(service, "send")

    service.send("user@example.com", "Test", "Body")

    mock_send.assert_called_once_with("user@example.com", "Test", "Body")
```

### Where to Patch

**Critical Rule:** Patch where the object is used, not where it's defined.

```python
# mymodule.py
from external_lib import ExternalClass

def my_function():
    obj = ExternalClass()
    return obj.method()

# test_mymodule.py
def test_my_function(mocker):
    # ✅ Correct: Patch where ExternalClass is used
    mocker.patch("mymodule.ExternalClass")

    # ❌ Wrong: Patching where it's defined won't work
    # mocker.patch("external_lib.ExternalClass")
```

## Return Values

### Simple Return Values

```python
def test_simple_return(mocker):
    mock_func = mocker.Mock(return_value=42)

    result = mock_func()

    assert result == 42
```

### Multiple Return Values

```python
def test_multiple_calls(mocker):
    mock_func = mocker.Mock(side_effect=[1, 2, 3])

    assert mock_func() == 1
    assert mock_func() == 2
    assert mock_func() == 3
```

### Dynamic Return Values

```python
def test_dynamic_return(mocker):
    def custom_side_effect(x, y):
        return x + y

    mock_func = mocker.Mock(side_effect=custom_side_effect)

    assert mock_func(2, 3) == 5
    assert mock_func(10, 20) == 30
```

### Raising Exceptions

```python
def test_exception(mocker):
    mock_func = mocker.Mock(side_effect=ValueError("Invalid input"))

    with pytest.raises(ValueError, match="Invalid input"):
        mock_func()
```

## Assertions

### Basic Assertions

```python
def test_call_assertions(mocker):
    mock_func = mocker.Mock()

    mock_func("arg1", key="value")

    # Verify called
    mock_func.assert_called()

    # Verify called once
    mock_func.assert_called_once()

    # Verify called with specific arguments
    mock_func.assert_called_with("arg1", key="value")

    # Verify called once with specific arguments
    mock_func.assert_called_once_with("arg1", key="value")
```

### Call Count

```python
def test_call_count(mocker):
    mock_func = mocker.Mock()

    mock_func()
    mock_func()
    mock_func()

    assert mock_func.call_count == 3
```

### Not Called

```python
def test_not_called(mocker):
    mock_func = mocker.Mock()

    # Verify never called
    mock_func.assert_not_called()
```

### Any Called

```python
def test_any_call(mocker):
    mock_func = mocker.Mock()

    mock_func(1, 2)
    mock_func(3, 4)
    mock_func(5, 6)

    # Verify called with these args at some point
    mock_func.assert_any_call(3, 4)
```

### All Calls

```python
def test_all_calls(mocker):
    mock_func = mocker.Mock()

    mock_func(1)
    mock_func(2)
    mock_func(3)

    # Verify exact sequence of calls
    assert mock_func.call_args_list == [
        mocker.call(1),
        mocker.call(2),
        mocker.call(3),
    ]
```

## Spies

Spies wrap real objects and record calls while still executing the real code.

```python
def test_spy(mocker):
    real_list = [1, 2, 3]

    # Spy on the append method
    spy = mocker.spy(real_list, "append")

    real_list.append(4)  # Real method is called
    real_list.append(5)

    # List is actually modified
    assert real_list == [1, 2, 3, 4, 5]

    # But we can verify the calls
    assert spy.call_count == 2
    spy.assert_any_call(4)
    spy.assert_any_call(5)
```

## Mocking External Dependencies

### Mocking HTTP Requests

```python
# Source: api_client.py
import requests

class APIClient:
    def get_user(self, user_id):
        response = requests.get(f"https://api.example.com/users/{user_id}")
        response.raise_for_status()
        return response.json()

# Test
def test_get_user(mocker):
    client = APIClient()

    # Mock requests.get
    mock_response = mocker.Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"id": 1, "name": "Alice"}

    mocker.patch("requests.get", return_value=mock_response)

    result = client.get_user(1)

    assert result == {"id": 1, "name": "Alice"}
```

### Mocking Database Queries

```python
# Source: user_service.py
from database import db

def get_active_users():
    return db.query("SELECT * FROM users WHERE active = true")

# Test
def test_get_active_users(mocker):
    # Mock db.query
    mock_users = [
        {"id": 1, "name": "Alice"},
        {"id": 2, "name": "Bob"},
    ]
    mocker.patch("user_service.db.query", return_value=mock_users)

    result = get_active_users()

    assert len(result) == 2
    assert result[0]["name"] == "Alice"
```

### Mocking File Operations

```python
def test_read_config(mocker):
    # Mock file reading
    mock_file_data = """
    {
        "api_key": "test_key",
        "timeout": 30
    }
    """
    mocker.patch("builtins.open", mocker.mock_open(read_data=mock_file_data))

    config = load_config("config.json")

    assert config["api_key"] == "test_key"
    assert config["timeout"] == 30
```

### Mocking Environment Variables

```python
def test_get_api_key(mocker):
    # Mock environment variable
    mocker.patch.dict("os.environ", {"API_KEY": "test_key_123"})

    api_key = get_api_key()

    assert api_key == "test_key_123"
```

### Mocking datetime

```python
from datetime import datetime

def test_current_timestamp(mocker):
    # Mock datetime.now()
    fake_now = datetime(2024, 1, 1, 12, 0, 0)
    mocker.patch("datetime.datetime").now.return_value = fake_now

    timestamp = get_current_timestamp()

    assert timestamp == "2024-01-01 12:00:00"
```

## MagicMock

MagicMock automatically handles Python magic methods (`__str__`, `__len__`, etc.).

```python
def test_magic_methods(mocker):
    # Mock with magic methods
    mock_obj = mocker.MagicMock()
    mock_obj.__str__.return_value = "Mocked String"
    mock_obj.__len__.return_value = 42

    assert str(mock_obj) == "Mocked String"
    assert len(mock_obj) == 42
```

### Context Managers

```python
def test_context_manager(mocker):
    # Mock a context manager
    mock_cm = mocker.MagicMock()
    mock_cm.__enter__.return_value = "resource"
    mock_cm.__exit__.return_value = False

    with mock_cm as resource:
        assert resource == "resource"

    mock_cm.__enter__.assert_called_once()
    mock_cm.__exit__.assert_called_once()
```

## Partial Mocking

Mock some methods while keeping others real.

```python
class Calculator:
    def add(self, a, b):
        return a + b

    def multiply(self, a, b):
        return a * b

def test_partial_mock(mocker):
    calc = Calculator()

    # Mock only multiply, keep add() real
    mocker.patch.object(calc, "multiply", return_value=100)

    assert calc.add(2, 3) == 5        # Real method
    assert calc.multiply(2, 3) == 100  # Mocked method
```

## PropertyMock

Mock properties and attributes.

```python
class User:
    @property
    def full_name(self):
        # Expensive computation
        return f"{self.first_name} {self.last_name}"

def test_user_full_name(mocker):
    user = User()
    user.first_name = "Alice"
    user.last_name = "Smith"

    # Mock the property
    mocker.patch.object(
        type(user),
        "full_name",
        new_callable=mocker.PropertyMock,
        return_value="Mocked Name"
    )

    assert user.full_name == "Mocked Name"
```

## AsyncMock (Async Code)

For testing async functions and coroutines.

```python
import asyncio

async def fetch_data():
    # Async API call
    await asyncio.sleep(1)
    return {"data": "value"}

def test_async_function(mocker):
    # Mock async function
    mocker.patch("mymodule.fetch_data", return_value=asyncio.coroutine(
        lambda: {"data": "mocked"}
    )())

    result = asyncio.run(fetch_data())

    assert result == {"data": "mocked"}
```

Or with AsyncMock (Python 3.8+):

```python
def test_async_with_asyncmock(mocker):
    mock_fetch = mocker.AsyncMock(return_value={"data": "mocked"})
    mocker.patch("mymodule.fetch_data", mock_fetch)

    result = asyncio.run(fetch_data())

    assert result == {"data": "mocked"}
    mock_fetch.assert_awaited_once()
```

## Advanced Patterns

### Mocking Class Constructors

```python
class Database:
    def __init__(self, connection_string):
        # Expensive connection
        ...

def test_database_init(mocker):
    # Mock Database constructor
    mock_db_instance = mocker.Mock()
    mock_db_class = mocker.patch("mymodule.Database", return_value=mock_db_instance)

    db = Database("connection_string")

    assert db is mock_db_instance
    mock_db_class.assert_called_once_with("connection_string")
```

### Mocking Imported Modules

```python
# mymodule.py
import external_module

def process():
    result = external_module.expensive_function()
    return result * 2

# test_mymodule.py
def test_process(mocker):
    # Mock entire module
    mock_module = mocker.MagicMock()
    mock_module.expensive_function.return_value = 5
    mocker.patch.dict("sys.modules", {"external_module": mock_module})

    result = process()

    assert result == 10
```

### Mocking Chained Calls

```python
def test_chained_calls(mocker):
    # Mock chained method calls
    mock_obj = mocker.Mock()
    mock_obj.method1().method2().method3.return_value = "result"

    result = mock_obj.method1().method2().method3()

    assert result == "result"
```

### Conditional Mocking

```python
def test_conditional_mock(mocker):
    def side_effect(x):
        if x > 0:
            return "positive"
        elif x < 0:
            return "negative"
        else:
            return "zero"

    mock_func = mocker.Mock(side_effect=side_effect)

    assert mock_func(5) == "positive"
    assert mock_func(-3) == "negative"
    assert mock_func(0) == "zero"
```

## Testing with Fixtures and Mocks

Combine fixtures with mocks for powerful tests.

```python
@pytest.fixture
def mock_database(mocker):
    """Fixture providing a mocked database."""
    mock_db = mocker.Mock()
    mock_db.query.return_value = [{"id": 1, "name": "Alice"}]
    return mock_db

def test_get_users(mock_database):
    users = get_users_from_db(mock_database)

    assert len(users) == 1
    assert users[0]["name"] == "Alice"
    mock_database.query.assert_called_once()
```

## Best Practices

### 1. Mock at the Right Level

Mock external dependencies, not internal logic.

```python
# Good: Mock external API
def test_fetch_weather(mocker):
    mocker.patch("requests.get", return_value=mock_response)
    weather = fetch_weather("London")
    assert weather["temp"] == 20

# Avoid: Mocking your own logic
def test_calculate_total(mocker):
    # Don't mock your own business logic
    mocker.patch("mymodule.calculate_total", return_value=100)
```

### 2. Don't Over-Mock

Only mock what's necessary.

```python
# Good: Mock only external dependency
def test_user_service(mocker):
    mocker.patch("requests.get")  # External API
    # Test the actual service logic
    result = user_service.process_user(1)

# Avoid: Mocking everything
def test_user_service_overmocked(mocker):
    mocker.patch("requests.get")
    mocker.patch("user_service.validate_user")  # Your code!
    mocker.patch("user_service.transform_data")  # Your code!
    # You're not testing anything real anymore
```

### 3. Verify Behavior, Not Implementation

```python
# Good: Test behavior
def test_send_notification(mocker):
    mock_email = mocker.patch("email_service.send")

    notify_user(user_id=1, message="Hello")

    # Verify the notification was sent
    mock_email.assert_called_once()

# Avoid: Testing implementation details
def test_send_notification_bad(mocker):
    # Testing exact internal calls is brittle
    mock_db = mocker.patch("database.query")
    mock_format = mocker.patch("formatter.format_message")
    # Now test is coupled to implementation
```

### 4. Use Descriptive Names

```python
# Good
def test_api_returns_user_data(mocker):
    mock_api_response = mocker.Mock()
    mock_api_response.json.return_value = {"id": 1}

# Avoid
def test_1(mocker):
    m = mocker.Mock()
    m.j.return_value = {"id": 1}
```

### 5. Keep Mocks Simple

```python
# Good: Simple, focused mock
def test_simple_mock(mocker):
    mock_func = mocker.Mock(return_value=42)
    assert call_api(mock_func) == 42

# Avoid: Complex mock setup
def test_complex_mock(mocker):
    mock = mocker.Mock()
    mock.a.b.c.d.e.f.return_value = 42  # Too deep!
```

## Common Pitfalls

### 1. Patching in Wrong Location

```python
# module_a.py
from module_b import function_b

def function_a():
    return function_b()

# ❌ Wrong: Patch where defined
def test_wrong(mocker):
    mocker.patch("module_b.function_b")  # Doesn't work!

# ✅ Correct: Patch where used
def test_correct(mocker):
    mocker.patch("module_a.function_b")  # Works!
```

### 2. Forgetting to Reset Mocks

```python
# Avoid: Mock state leaking between tests
mock_func = mocker.Mock()

def test_1():
    mock_func()
    assert mock_func.call_count == 1

def test_2():
    # mock_func.call_count is still 1 from test_1!
    assert mock_func.call_count == 0  # Fails!
```

**Solution:** Use fresh mocks in each test or reset:

```python
def test_with_reset(mocker):
    mock_func = mocker.Mock()  # Fresh mock each test
    mock_func()
    assert mock_func.call_count == 1
```

### 3. Mocking Too Early

```python
# ❌ Wrong: Mock before import
def test_wrong(mocker):
    mocker.patch("requests.get")
    from mymodule import fetch_data  # Import after patch

# ✅ Correct: Patch after import
from mymodule import fetch_data

def test_correct(mocker):
    mocker.patch("mymodule.requests.get")
    result = fetch_data()
```

## See Also

- `fixtures-guide.md` - Fixture patterns and scoping
- `tdd-workflow.md` - Red-Green-Refactor cycle
- `parametrization-guide.md` - Data-driven testing
