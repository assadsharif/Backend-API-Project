# Architecture via TDD

## Core Principle

Let tests drive your architecture. If code is hard to test, the design needs improvement.

## Architecture Smells (Test-Detectable)

| Smell | Test Symptom | Refactor To |
|-------|-------------|-------------|
| God object | Test setup > 20 lines | Split into focused classes |
| Hidden dependency | Must patch internals | Dependency injection |
| Tight coupling | Changing A breaks B's tests | Interface/protocol |
| Missing abstraction | Duplicated test setup | Extract service/repository |
| Side effects | Tests need global cleanup | Pure functions + boundary layer |

## Pattern: Ports & Adapters via TDD

```python
# Step 1: Define the port (interface)
from typing import Protocol

class NotificationPort(Protocol):
    def send(self, to: str, message: str) -> bool: ...

# Step 2: Write tests against the port
class TestOrderNotification:
    def test_sends_notification_on_order_complete(self):
        fake_notifier = FakeNotifier()
        service = OrderService(notifier=fake_notifier)

        service.complete_order(order_id=1)

        assert fake_notifier.last_message == "Order #1 completed"

    def test_handles_notification_failure_gracefully(self):
        failing_notifier = FailingNotifier()
        service = OrderService(notifier=failing_notifier)

        # Should not raise, even if notification fails
        service.complete_order(order_id=1)

# Step 3: Implement the adapter (production)
class EmailNotifier:
    def send(self, to: str, message: str) -> bool:
        # Real email sending logic
        ...

# Step 4: Test the adapter separately
class TestEmailNotifier:
    @responses.activate
    def test_sends_via_smtp_api(self):
        responses.add(responses.POST, "https://mail.api/send", status=200)
        notifier = EmailNotifier(api_url="https://mail.api/send")
        assert notifier.send("user@test.com", "Hello") is True
```

## Pattern: Repository Pattern

```python
# Port
class UserRepository(Protocol):
    def find_by_id(self, user_id: int) -> User | None: ...
    def save(self, user: User) -> User: ...

# Test with in-memory implementation
class InMemoryUserRepo:
    def __init__(self):
        self._users = {}
        self._next_id = 1

    def find_by_id(self, user_id: int) -> User | None:
        return self._users.get(user_id)

    def save(self, user: User) -> User:
        if not user.id:
            user.id = self._next_id
            self._next_id += 1
        self._users[user.id] = user
        return user

# Business logic tests use in-memory repo
class TestUserService:
    def test_register_user_saves_to_repo(self):
        repo = InMemoryUserRepo()
        service = UserService(repo)

        user = service.register("alice@test.com", "Alice")

        assert repo.find_by_id(user.id) is not None
        assert repo.find_by_id(user.id).name == "Alice"

    def test_register_duplicate_email_raises(self):
        repo = InMemoryUserRepo()
        service = UserService(repo)
        service.register("alice@test.com", "Alice")

        with pytest.raises(DuplicateEmailError):
            service.register("alice@test.com", "Bob")
```

## TDD-Driven Refactoring Steps

1. **Write characterization tests** for existing behavior
2. **Identify the smell** (God object, hidden dependency, etc.)
3. **Write a test for the new design** (RED)
4. **Extract/refactor** to make it pass (GREEN)
5. **Verify characterization tests still pass** (no regressions)
6. **Remove duplication** between old and new tests (REFACTOR)

## Test Pyramid Enforcement

```
        /  E2E  \        <- Few: critical user journeys only
       /----------\
      / Integration \    <- Some: boundary interactions
     /----------------\
    /    Unit Tests     \ <- Many: business logic, fast, isolated
   /--------------------\
```

| Layer | What to Test | Speed Target |
|-------|-------------|--------------|
| Unit | Business logic, pure functions, models | < 10ms each |
| Integration | DB queries, HTTP clients, file I/O | < 500ms each |
| E2E | Critical user flows (login, checkout) | < 5s each |

## Must Follow

- [ ] Let hard-to-test code signal design problems
- [ ] Use Protocol/ABC for boundaries (ports)
- [ ] Test business logic with in-memory implementations
- [ ] Test adapters (DB, HTTP, FS) separately at integration level
- [ ] Maintain the test pyramid ratio (many unit, some integration, few E2E)

## Must Avoid

- Testing through the UI when a unit test suffices
- Skipping characterization tests before refactoring
- Creating abstractions without a failing test driving them
- Integration tests for pure business logic
- Mocking across layer boundaries (test each layer independently)
