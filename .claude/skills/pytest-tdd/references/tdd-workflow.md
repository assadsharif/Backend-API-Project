# Test-Driven Development (TDD) Workflow

## The Red-Green-Refactor Cycle

TDD follows a three-step cycle that ensures code is well-tested and well-designed:

```
RED → GREEN → REFACTOR → (repeat)
```

### 1. RED: Write a Failing Test

Write a test for the next bit of functionality you want to add. The test should fail because the functionality doesn't exist yet.

**Key principles:**
- Write the smallest possible test that fails
- Test should fail for the right reason (not syntax errors)
- Focus on behavior, not implementation
- Write the assertion first, then work backwards

**Example:**

```python
def test_calculate_total_price():
    """Test calculating total price with tax."""
    cart = ShoppingCart()
    cart.add_item("Apple", price=1.00, quantity=3)

    # This will fail - calculate_total() doesn't exist yet
    assert cart.calculate_total(tax_rate=0.1) == 3.30
```

**Run the test:**
```bash
pytest tests/test_shopping_cart.py::test_calculate_total_price -v
```

**Expected:** Test fails with clear error message.

### 2. GREEN: Write Minimum Code to Pass

Write just enough code to make the test pass. Don't worry about perfect design yet.

**Key principles:**
- Write the simplest implementation that passes
- No extra features or "what if" code
- Hard-coded values are acceptable at this stage
- Focus on making the test green, not on elegance

**Example:**

```python
class ShoppingCart:
    def __init__(self):
        self.items = []

    def add_item(self, name: str, price: float, quantity: int):
        self.items.append({
            "name": name,
            "price": price,
            "quantity": quantity
        })

    def calculate_total(self, tax_rate: float = 0.0) -> float:
        """Calculate total price with tax."""
        subtotal = sum(item["price"] * item["quantity"] for item in self.items)
        return round(subtotal * (1 + tax_rate), 2)
```

**Run the test:**
```bash
pytest tests/test_shopping_cart.py::test_calculate_total_price -v
```

**Expected:** Test passes ✓

### 3. REFACTOR: Improve Code Quality

Now that tests are green, improve the code design while keeping tests passing.

**Key principles:**
- Remove duplication
- Improve names and clarity
- Extract methods/classes
- Apply design patterns
- Tests must stay green throughout

**Example refactoring:**

```python
from dataclasses import dataclass
from typing import List

@dataclass
class CartItem:
    """Represents an item in the shopping cart."""
    name: str
    price: float
    quantity: int

    @property
    def subtotal(self) -> float:
        return self.price * self.quantity


class ShoppingCart:
    def __init__(self):
        self.items: List[CartItem] = []

    def add_item(self, name: str, price: float, quantity: int):
        """Add item to cart."""
        self.items.append(CartItem(name, price, quantity))

    def calculate_total(self, tax_rate: float = 0.0) -> float:
        """Calculate total price with tax."""
        subtotal = sum(item.subtotal for item in self.items)
        return round(subtotal * (1 + tax_rate), 2)
```

**Run all tests:**
```bash
pytest tests/ -v
```

**Expected:** All tests still pass ✓

## TDD Workflow Patterns

### Pattern 1: Triangulation

When unsure of the correct abstraction, write multiple tests with different inputs to "triangulate" the solution.

```python
def test_add_positive_numbers():
    assert add(2, 3) == 5

def test_add_negative_numbers():
    assert add(-2, -3) == -5

def test_add_mixed_numbers():
    assert add(-2, 5) == 3
```

Each test forces you toward a more general solution.

### Pattern 2: Test List

Keep a running list of tests to write. Cross them off as you go.

```python
# TODO Tests:
# [x] test_add_item_to_cart
# [x] test_calculate_total_no_tax
# [x] test_calculate_total_with_tax
# [ ] test_remove_item_from_cart
# [ ] test_apply_discount_code
# [ ] test_empty_cart_total_is_zero
```

### Pattern 3: Fake It Till You Make It

Start with hard-coded values, then generalize through refactoring.

**RED:**
```python
def test_fibonacci_first_number():
    assert fibonacci(0) == 0
```

**GREEN (fake it):**
```python
def fibonacci(n):
    return 0  # Hard-coded!
```

**RED (add another test):**
```python
def test_fibonacci_second_number():
    assert fibonacci(1) == 1
```

**GREEN (still faking):**
```python
def fibonacci(n):
    if n == 0:
        return 0
    return 1  # Hard-coded!
```

**RED (add more tests):**
```python
def test_fibonacci_sequence():
    assert fibonacci(2) == 1
    assert fibonacci(3) == 2
    assert fibonacci(4) == 3
```

**GREEN (now generalize):**
```python
def fibonacci(n):
    if n <= 1:
        return n
    return fibonacci(n - 1) + fibonacci(n - 2)
```

### Pattern 4: One Test at a Time

Focus on making one test pass before writing the next. Don't write multiple failing tests.

**Good:**
```python
# 1. Write test
def test_user_can_login():
    ...

# 2. Make it pass
# 3. Refactor
# 4. Now write next test
def test_user_cannot_login_with_wrong_password():
    ...
```

**Avoid:**
```python
# Don't write multiple failing tests
def test_user_can_login():
    ...  # FAILS

def test_user_cannot_login_with_wrong_password():
    ...  # FAILS

def test_user_can_logout():
    ...  # FAILS
```

## TDD Best Practices

### Start with the Assertion

Write the assertion first, then work backwards to create the necessary setup.

```python
def test_user_full_name():
    # 1. Write what you want to assert
    assert user.full_name == "John Doe"

    # 2. Work backwards - what do we need?
    user = User(first_name="John", last_name="Doe")
```

### Test Behavior, Not Implementation

Focus on what the code does, not how it does it.

**Good (tests behavior):**
```python
def test_sort_users_by_age():
    users = [User("Bob", 30), User("Alice", 25)]
    sorted_users = sort_users(users, by="age")
    assert sorted_users[0].name == "Alice"
    assert sorted_users[1].name == "Bob"
```

**Avoid (tests implementation):**
```python
def test_sort_uses_quicksort():
    # Don't test the sorting algorithm used
    # Test the result instead
    ...
```

### Keep Tests Fast

Fast tests encourage running them frequently.

- Avoid sleep() calls
- Mock external services
- Use in-memory databases for tests
- Run slow tests separately with markers

```python
@pytest.mark.slow
def test_full_database_migration():
    # This test takes 30 seconds
    ...

# Run fast tests: pytest -m "not slow"
# Run all tests: pytest
```

### Make Tests Independent

Each test should be able to run in any order.

**Good:**
```python
def test_create_user():
    user = User("Alice")
    assert user.name == "Alice"

def test_delete_user():
    user = User("Bob")
    user.delete()
    assert user.is_deleted
```

**Avoid:**
```python
# Don't depend on test execution order
def test_create_user():
    global user
    user = User("Alice")  # Bad: global state

def test_delete_user():
    user.delete()  # Bad: depends on previous test
```

## Watch Mode for TDD

Use pytest-watch to automatically re-run tests when files change:

```bash
# Install
pip install pytest-watch

# Run watch mode
ptw

# Watch with coverage
ptw -- --cov=src

# Watch specific tests
ptw tests/unit/
```

Or use the provided script:
```bash
./scripts/run_tdd_cycle.sh
```

## Common TDD Mistakes

### 1. Writing Too Much Code at Once

**Problem:** Implementing multiple features before writing tests.

**Solution:** Write one test, write minimal code to pass, repeat.

### 2. Testing Implementation Details

**Problem:** Tests break when refactoring, even though behavior unchanged.

**Solution:** Test public interfaces and behavior, not private methods.

### 3. Skipping Refactoring

**Problem:** Accumulating technical debt because "tests are green."

**Solution:** Always refactor after green. Make it right, not just working.

### 4. Not Running Tests Frequently

**Problem:** Writing lots of code before running tests, making debugging hard.

**Solution:** Run tests after every small change. Use watch mode.

### 5. Ignoring Failing Tests

**Problem:** Commenting out failing tests to make build pass.

**Solution:** Fix or delete broken tests. Never commit failing tests.

## TDD Rhythm

Develop a rhythm: short cycles (2-10 minutes per cycle).

```
00:00 - Write failing test (RED)     [2 min]
00:02 - Write code to pass (GREEN)   [5 min]
00:07 - Refactor (keep green)        [3 min]
00:10 - Commit, start next cycle
```

**Signs you're in the zone:**
- Tests run every 30-60 seconds
- Small, focused commits
- Clear separation: test → code → refactor
- Confidence in changes (tests have your back)

## Resources

- **Test runners:** pytest, pytest-watch
- **Coverage:** pytest-cov
- **Mocking:** pytest-mock, unittest.mock
- **Fixtures:** conftest.py, @pytest.fixture
- **Markers:** @pytest.mark for organizing tests

See other reference guides:
- `fixtures-guide.md` - Comprehensive fixture patterns
- `parametrization-guide.md` - Data-driven testing
- `mocking-guide.md` - Mocking and patching
