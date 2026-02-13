# Pytest Fixtures Guide

## What Are Fixtures?

Fixtures are functions that provide reusable test data, setup, and teardown logic. They help eliminate duplication and make tests more maintainable.

**Without fixtures:**
```python
def test_user_login():
    db = Database("test.db")
    db.connect()
    user = User("alice", "password123")
    db.save(user)

    result = login("alice", "password123")

    assert result.success
    db.disconnect()
    db.delete()

def test_user_logout():
    db = Database("test.db")  # Duplicated setup
    db.connect()
    user = User("alice", "password123")
    db.save(user)

    result = logout(user)

    assert result.success
    db.disconnect()  # Duplicated teardown
    db.delete()
```

**With fixtures:**
```python
@pytest.fixture
def database():
    db = Database("test.db")
    db.connect()
    yield db
    db.disconnect()
    db.delete()

@pytest.fixture
def user(database):
    user = User("alice", "password123")
    database.save(user)
    return user

def test_user_login(user):
    result = login("alice", "password123")
    assert result.success

def test_user_logout(user):
    result = logout(user)
    assert result.success
```

## Basic Fixture Usage

### Simple Fixture

```python
import pytest

@pytest.fixture
def sample_data():
    """Provide sample data for tests."""
    return {"name": "Alice", "age": 30}

def test_user_name(sample_data):
    assert sample_data["name"] == "Alice"

def test_user_age(sample_data):
    assert sample_data["age"] == 30
```

### Fixture with Setup and Teardown

Use `yield` to separate setup from teardown:

```python
@pytest.fixture
def temp_file():
    """Create temporary file for testing."""
    # Setup
    file_path = "/tmp/test_file.txt"
    with open(file_path, "w") as f:
        f.write("test data")

    # Provide to test
    yield file_path

    # Teardown (runs after test completes)
    import os
    os.remove(file_path)

def test_read_file(temp_file):
    with open(temp_file) as f:
        content = f.read()
    assert content == "test data"
    # temp_file is automatically deleted after this test
```

## Fixture Scopes

Control how often fixtures are created and destroyed.

### Function Scope (Default)

Fixture runs once per test function.

```python
@pytest.fixture  # scope="function" is default
def database_connection():
    print("Connecting to database...")
    conn = connect_to_db()
    yield conn
    print("Disconnecting from database...")
    conn.close()

def test_query_users(database_connection):
    # Fresh connection for this test
    users = database_connection.query("SELECT * FROM users")
    assert len(users) > 0

def test_query_posts(database_connection):
    # New connection for this test
    posts = database_connection.query("SELECT * FROM posts")
    assert len(posts) > 0
```

### Class Scope

Fixture runs once per test class.

```python
@pytest.fixture(scope="class")
def expensive_resource():
    print("Creating expensive resource...")
    resource = ExpensiveResource()
    resource.initialize()
    yield resource
    print("Cleaning up expensive resource...")
    resource.cleanup()

class TestDatabaseOperations:
    def test_insert(self, expensive_resource):
        # Same resource used for all tests in class
        expensive_resource.insert("data")
        assert True

    def test_update(self, expensive_resource):
        # Same resource instance
        expensive_resource.update("data")
        assert True

    def test_delete(self, expensive_resource):
        # Same resource instance
        expensive_resource.delete("data")
        assert True
```

### Module Scope

Fixture runs once per test module (file).

```python
@pytest.fixture(scope="module")
def database():
    """Create database once per test file."""
    print("Creating database...")
    db = Database("test.db")
    db.create_tables()
    yield db
    print("Dropping database...")
    db.drop_tables()

# All tests in this file share the same database
def test_user_creation(database):
    user = User("alice")
    database.save(user)
    assert database.get_user("alice") is not None

def test_user_deletion(database):
    database.delete_user("alice")
    assert database.get_user("alice") is None
```

### Session Scope

Fixture runs once per entire test session.

```python
@pytest.fixture(scope="session")
def browser():
    """Launch browser once for all tests."""
    print("Launching browser...")
    driver = webdriver.Chrome()
    yield driver
    print("Closing browser...")
    driver.quit()

# Browser stays open across all test files
def test_homepage(browser):
    browser.get("http://example.com")
    assert "Example" in browser.title

def test_login_page(browser):
    browser.get("http://example.com/login")
    assert "Login" in browser.title
```

### Scope Comparison

| Scope | Runs | Use When |
|-------|------|----------|
| function | Once per test | Default; fast setup |
| class | Once per test class | Shared state within class |
| module | Once per test file | Expensive setup (DB, API) |
| session | Once per test run | Very expensive (browser, services) |

## Fixture Dependencies

Fixtures can depend on other fixtures.

```python
@pytest.fixture
def database():
    db = Database()
    db.connect()
    yield db
    db.disconnect()

@pytest.fixture
def user(database):  # Depends on database
    user = User("alice")
    database.save(user)
    return user

@pytest.fixture
def logged_in_user(user):  # Depends on user (which depends on database)
    user.login()
    return user

def test_user_profile(logged_in_user):
    # All three fixtures run: database → user → logged_in_user
    assert logged_in_user.is_authenticated
```

## Autouse Fixtures

Fixtures that run automatically without being requested.

```python
@pytest.fixture(autouse=True)
def reset_state():
    """Reset global state before each test."""
    GlobalState.reset()
    yield
    # Cleanup after test

def test_something():
    # reset_state runs automatically
    assert GlobalState.counter == 0

def test_another_thing():
    # reset_state runs again
    assert GlobalState.counter == 0
```

### Autouse with Scope

```python
@pytest.fixture(scope="module", autouse=True)
def setup_test_environment():
    """Set up test environment once per module."""
    print("Setting up test environment...")
    os.environ["ENV"] = "test"
    yield
    print("Tearing down test environment...")
    del os.environ["ENV"]

# All tests in this module automatically get test environment
def test_api_call():
    assert os.environ["ENV"] == "test"
```

## Parametrized Fixtures

Create multiple versions of a fixture.

```python
@pytest.fixture(params=["sqlite", "postgres", "mysql"])
def database(request):
    """Test with multiple database backends."""
    db_type = request.param
    db = Database(db_type)
    db.connect()
    yield db
    db.disconnect()

def test_user_creation(database):
    # This test runs 3 times:
    # 1. with sqlite database
    # 2. with postgres database
    # 3. with mysql database
    user = User("alice")
    database.save(user)
    assert database.get_user("alice") is not None
```

### Fixture IDs

Add readable names to parametrized fixtures:

```python
@pytest.fixture(params=[
    {"name": "sqlite", "port": None},
    {"name": "postgres", "port": 5432},
    {"name": "mysql", "port": 3306},
], ids=["sqlite", "postgres", "mysql"])
def database(request):
    config = request.param
    db = Database(config["name"], port=config["port"])
    yield db
    db.disconnect()

# Test output shows readable names:
# test_user_creation[sqlite] PASSED
# test_user_creation[postgres] PASSED
# test_user_creation[mysql] PASSED
```

## Built-in Fixtures

Pytest provides useful built-in fixtures.

### tmp_path (Recommended)

Provides a temporary directory unique to the test.

```python
def test_create_file(tmp_path):
    # tmp_path is a pathlib.Path object
    file = tmp_path / "test.txt"
    file.write_text("hello world")

    assert file.read_text() == "hello world"
    # Directory automatically cleaned up after test
```

### tmpdir (Legacy)

Legacy version of tmp_path (uses py.path instead of pathlib).

```python
def test_create_file(tmpdir):
    file = tmpdir.join("test.txt")
    file.write("hello world")
    assert file.read() == "hello world"
```

### monkeypatch

Safely modify objects, dictionaries, environment variables.

```python
def test_api_key(monkeypatch):
    # Set environment variable
    monkeypatch.setenv("API_KEY", "test_key_123")

    # Now code using os.environ["API_KEY"] will see "test_key_123"
    assert get_api_key() == "test_key_123"
    # Environment variable automatically restored after test
```

### capsys

Capture stdout/stderr output.

```python
def test_print_output(capsys):
    print("Hello, World!")
    captured = capsys.readouterr()
    assert captured.out == "Hello, World!\n"
    assert captured.err == ""
```

### request

Access information about the requesting test.

```python
@pytest.fixture
def resource(request):
    # Get test name
    print(f"Setting up for {request.node.name}")

    # Get marker
    if request.node.get_closest_marker("slow"):
        print("This is a slow test")

    resource = Resource()
    yield resource
    resource.cleanup()
```

## Fixture Factories

Create fixtures that return factory functions for generating multiple instances.

```python
@pytest.fixture
def user_factory():
    """Factory for creating multiple users."""
    created_users = []

    def _create_user(name, age):
        user = User(name, age)
        created_users.append(user)
        return user

    yield _create_user

    # Cleanup all created users
    for user in created_users:
        user.delete()

def test_multiple_users(user_factory):
    alice = user_factory("Alice", 30)
    bob = user_factory("Bob", 25)

    assert alice.name == "Alice"
    assert bob.name == "Bob"
    # Both users automatically cleaned up
```

## Organizing Fixtures

### conftest.py

Place shared fixtures in `conftest.py` for automatic discovery.

```
tests/
├── conftest.py          # Project-wide fixtures
├── unit/
│   ├── conftest.py      # Unit test fixtures
│   └── test_users.py
└── integration/
    ├── conftest.py      # Integration test fixtures
    └── test_api.py
```

**tests/conftest.py:**
```python
import pytest

@pytest.fixture
def database():
    """Available to all tests."""
    db = Database()
    db.connect()
    yield db
    db.disconnect()
```

**tests/unit/test_users.py:**
```python
def test_user_creation(database):  # Uses fixture from conftest.py
    user = User("alice")
    database.save(user)
    assert True
```

### Fixture Naming

Use clear, descriptive names:

```python
# Good
@pytest.fixture
def authenticated_user():
    ...

@pytest.fixture
def temporary_directory():
    ...

# Avoid
@pytest.fixture
def x():  # Too vague
    ...

@pytest.fixture
def auth():  # Unclear what this returns
    ...
```

## Advanced Patterns

### Fixture Finalization

Alternative to yield for cleanup:

```python
@pytest.fixture
def resource(request):
    res = Resource()

    def cleanup():
        res.close()

    request.addfinalizer(cleanup)
    return res
```

### Conditional Fixtures

```python
@pytest.fixture
def cache(request):
    """Use Redis in CI, in-memory cache locally."""
    if os.getenv("CI"):
        cache = RedisCache()
    else:
        cache = InMemoryCache()

    yield cache
    cache.clear()
```

### Fixture Caching with Memoization

```python
@pytest.fixture(scope="session")
def expensive_data():
    """Compute expensive data once."""
    print("Computing expensive data...")
    data = compute_expensive_operation()
    return data

# All tests share the same computed data
def test_operation_1(expensive_data):
    assert expensive_data is not None

def test_operation_2(expensive_data):
    # No recomputation
    assert len(expensive_data) > 0
```

## Best Practices

### 1. Keep Fixtures Focused

Each fixture should do one thing.

```python
# Good: Separate fixtures
@pytest.fixture
def database():
    return Database()

@pytest.fixture
def user(database):
    user = User("alice")
    database.save(user)
    return user

# Avoid: One fixture does everything
@pytest.fixture
def everything():
    db = Database()
    user = User("alice")
    db.save(user)
    return db, user  # Hard to reuse
```

### 2. Use Appropriate Scope

Balance performance and isolation.

```python
# Fast operations: function scope (default)
@pytest.fixture
def user_data():
    return {"name": "Alice"}

# Expensive operations: module or session scope
@pytest.fixture(scope="session")
def browser():
    return webdriver.Chrome()
```

### 3. Explicit is Better Than Implicit

Request fixtures explicitly in test signatures.

```python
# Good: Clear dependencies
def test_user_login(database, user):
    ...

# Avoid: Autouse hides dependencies
@pytest.fixture(autouse=True)
def database():  # Hard to see which tests use this
    ...
```

### 4. Document Complex Fixtures

```python
@pytest.fixture(scope="module")
def initialized_application():
    """Fully initialized application with test database.

    Returns:
        Application instance with:
        - Test database with sample data
        - Authentication configured
        - Cache enabled

    Example:
        def test_homepage(initialized_application):
            response = initialized_application.get("/")
            assert response.status == 200
    """
    app = create_app("test")
    app.db.create_tables()
    app.db.seed_data()
    return app
```

### 5. Avoid Fixture Side Effects

Fixtures should be independent.

```python
# Good: No side effects
@pytest.fixture
def user():
    return User("alice")

# Avoid: Modifies global state
@pytest.fixture
def user():
    global current_user
    current_user = User("alice")  # Side effect!
    return current_user
```

## Common Pitfalls

### Modifying Fixture Return Values

```python
@pytest.fixture
def users():
    return ["alice", "bob"]

def test_add_user(users):
    users.append("charlie")  # Mutates fixture!
    assert len(users) == 3

def test_user_count(users):
    # This fails if test_add_user ran first
    assert len(users) == 2  # Expected 2, got 3
```

**Solution:** Return a fresh copy or use function scope.

```python
@pytest.fixture
def users():
    return ["alice", "bob"].copy()  # Fresh copy each time
```

### Forgetting Cleanup

```python
@pytest.fixture
def temp_file():
    file = open("/tmp/test.txt", "w")
    return file
    # Forgot to close the file!

# Better:
@pytest.fixture
def temp_file():
    file = open("/tmp/test.txt", "w")
    yield file
    file.close()  # Cleanup
```

## See Also

- `parametrization-guide.md` - Data-driven testing
- `mocking-guide.md` - Mocking with fixtures
- `tdd-workflow.md` - TDD Red-Green-Refactor cycle
