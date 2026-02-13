# Testing Anti-Patterns Guide

Common mistakes and pitfalls to avoid in TDD and pytest testing.

## TDD Anti-Patterns

### 1. Writing Too Much Code at Once

**Problem:** Implementing multiple features before writing tests.

**Symptom:** You're writing 50+ lines of code before running any test.

**Solution:** Write one test, write minimal code to pass, repeat.

```python
# Bad: Giant implementation first
class UserService:
    def create_user(self): ...
    def update_user(self): ...
    def delete_user(self): ...
    def authenticate(self): ...
    # 200 lines later... now let's write tests

# Good: One test at a time
def test_create_user():
    # RED: Test fails
    user = create_user("alice")
    assert user.name == "alice"

# GREEN: Minimal code
def create_user(name):
    return User(name)

# Then write next test...
```

### 2. Testing Implementation Details

**Problem:** Tests break when refactoring, even though behavior is unchanged.

**Symptom:** Changing internal code breaks tests that should still pass.

**Solution:** Test public interfaces and behavior, not private methods.

```python
# Bad: Testing implementation
def test_user_uses_dict_for_storage():
    user = User("alice")
    assert isinstance(user._data, dict)  # Private attribute!
    assert user._data["name"] == "alice"

# Good: Testing behavior
def test_user_has_name():
    user = User("alice")
    assert user.name == "alice"  # Public interface
```

### 3. Skipping the Refactor Step

**Problem:** Accumulating technical debt because "tests are green."

**Symptom:** Green tests, but duplicated or messy code.

**Solution:** Always refactor after green. Make it right, not just working.

```python
# After GREEN, don't stop here:
def calculate_total(items):
    total = 0
    for item in items:
        total = total + item["price"] * item["quantity"]
    return total

# REFACTOR to:
def calculate_total(items):
    return sum(item["price"] * item["quantity"] for item in items)
```

### 4. Not Running Tests Frequently

**Problem:** Writing lots of code before running tests, making debugging hard.

**Symptom:** Multiple failing tests with unclear root cause.

**Solution:** Run tests after every small change. Use watch mode.

```bash
# Use watch mode for continuous feedback
./scripts/run_tdd_cycle.sh

# Or
ptw -- -v --tb=short
```

### 5. Ignoring Failing Tests

**Problem:** Commenting out or skipping failing tests to make builds pass.

**Symptom:** `@pytest.mark.skip` or `# TODO: fix later` everywhere.

**Solution:** Fix or delete broken tests. Never commit failing tests.

```python
# Bad: Ignoring failures
@pytest.mark.skip("Will fix later")  # Never gets fixed
def test_important_feature():
    ...

# Good: Fix it or delete it
def test_important_feature():
    # Actually implement the fix
    assert feature_works()
```

## Mocking Anti-Patterns

### 6. Over-Mocking

**Problem:** Mocking so much that you're not testing anything real.

**Symptom:** 10+ mocks in a single test.

**Solution:** Only mock external dependencies, not your own logic.

```python
# Bad: Over-mocked
def test_user_service(mocker):
    mocker.patch("user_service.validate")
    mocker.patch("user_service.transform")
    mocker.patch("user_service.save")
    mocker.patch("user_service.notify")
    # You're not testing anything!

# Good: Mock only external dependencies
def test_user_service(mocker):
    mocker.patch("requests.post")  # External API only
    result = user_service.create_user("alice")
    assert result.success
```

### 7. Patching in Wrong Location

**Problem:** Mocks don't take effect because patched in wrong place.

**Solution:** Patch where the object is **used**, not where it's **defined**.

```python
# mymodule.py
from external_lib import ExternalClass

def my_function():
    return ExternalClass().method()

# test_mymodule.py
# Bad: Patch where defined
mocker.patch("external_lib.ExternalClass")  # Won't work!

# Good: Patch where used
mocker.patch("mymodule.ExternalClass")  # Works!
```

### 8. Mock State Leaking

**Problem:** Mock state persists between tests.

**Symptom:** Tests pass individually but fail when run together.

**Solution:** Use fresh mocks in each test via the `mocker` fixture.

```python
# Bad: Shared mock
mock_func = Mock()

def test_1():
    mock_func()
    assert mock_func.call_count == 1

def test_2():
    # Fails! call_count is 2 from test_1
    assert mock_func.call_count == 1

# Good: Fresh mock each test
def test_1(mocker):
    mock_func = mocker.Mock()
    mock_func()
    assert mock_func.call_count == 1

def test_2(mocker):
    mock_func = mocker.Mock()  # Fresh mock
    assert mock_func.call_count == 0
```

## Fixture Anti-Patterns

### 9. Modifying Fixture Return Values

**Problem:** Test modifies fixture data, affecting other tests.

```python
@pytest.fixture
def users():
    return ["alice", "bob"]

def test_add_user(users):
    users.append("charlie")  # Mutates fixture!
    assert len(users) == 3

def test_user_count(users):
    # May fail if test_add_user ran first (list has 3 items)
    assert len(users) == 2
```

**Solution:** Return fresh copies or use function scope.

```python
@pytest.fixture
def users():
    return ["alice", "bob"].copy()  # Fresh copy each time
```

### 10. Hidden Dependencies via Autouse

**Problem:** `autouse=True` fixtures hide test dependencies.

```python
# Bad: Hidden dependency
@pytest.fixture(autouse=True)
def database():
    db = Database()
    db.connect()
    yield db
    db.disconnect()

def test_user():
    # Unclear that this needs database
    ...
```

**Solution:** Explicit is better than implicit.

```python
# Good: Explicit dependency
@pytest.fixture
def database():
    ...

def test_user(database):  # Clear dependency
    ...
```

### 11. Forgetting Cleanup

**Problem:** Resources not cleaned up after tests.

```python
# Bad: Resource leak
@pytest.fixture
def temp_file():
    f = open("/tmp/test.txt", "w")
    return f
    # File never closed!

# Good: Proper cleanup
@pytest.fixture
def temp_file():
    f = open("/tmp/test.txt", "w")
    yield f
    f.close()
```

## Test Design Anti-Patterns

### 12. Test Interdependence

**Problem:** Tests depend on execution order.

```python
# Bad: Order-dependent
user = None

def test_create_user():
    global user
    user = User("alice")

def test_user_has_name():
    assert user.name == "alice"  # Fails if run first!
```

**Solution:** Each test creates its own data.

```python
# Good: Independent
def test_create_user():
    user = User("alice")
    assert user is not None

def test_user_has_name():
    user = User("alice")  # Creates own user
    assert user.name == "alice"
```

### 13. Testing Multiple Things

**Problem:** Single test verifies multiple unrelated behaviors.

```python
# Bad: Testing too much
def test_user():
    user = User("alice")
    assert user.name == "alice"
    assert user.login("password")
    assert user.update_profile({"bio": "Hello"})
    assert user.logout()
    assert user.delete()
```

**Solution:** One test, one behavior.

```python
# Good: Focused tests
def test_user_has_name():
    user = User("alice")
    assert user.name == "alice"

def test_user_can_login():
    user = User("alice")
    assert user.login("password")
```

### 14. Brittle Assertions

**Problem:** Tests break from insignificant changes.

```python
# Bad: Fragile assertion
def test_error_message():
    with pytest.raises(ValueError) as exc:
        validate("")
    assert str(exc.value) == "Input cannot be empty. Please provide a valid value."

# Good: Check key content
def test_error_message():
    with pytest.raises(ValueError, match="cannot be empty"):
        validate("")
```

### 15. Testing Framework Code

**Problem:** Writing tests for external libraries instead of your code.

```python
# Bad: Testing Python/pytest
def test_list_append():
    items = []
    items.append(1)
    assert items == [1]  # Testing Python lists!

# Good: Test YOUR code using lists
def test_cart_add_item():
    cart = Cart()
    cart.add("apple")
    assert cart.items == ["apple"]
```

## Quick Checklist

Before committing tests, verify:

- [ ] Each test has one clear purpose
- [ ] Tests are independent (run in any order)
- [ ] Mocks are only for external dependencies
- [ ] Fixtures clean up after themselves
- [ ] No `@pytest.mark.skip` without ticket reference
- [ ] No commented-out tests
- [ ] Test names describe the behavior being tested

## See Also

- `tdd-workflow.md` - Proper TDD cycle
- `mocking-guide.md` - When and how to mock
- `fixtures-guide.md` - Fixture best practices
