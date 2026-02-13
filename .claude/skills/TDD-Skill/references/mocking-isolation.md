# Mocking & Test Isolation

## Core Principle

Mock at boundaries only. If you're mocking your own code, refactor the design instead.

## When to Mock

| Boundary | Mock With | Example |
|----------|-----------|---------|
| HTTP APIs | `responses`, `httpx_mock`, `respx` | External REST calls |
| Time | `freezegun`, `time_machine` | `datetime.now()`, `time.time()` |
| Randomness | `pytest-mock` (patch `random`) | UUIDs, tokens, shuffles |
| File system | `tmp_path` fixture (real FS) | File read/write |
| Database | In-memory SQLite or transaction rollback | Queries, inserts |
| Environment | `monkeypatch.setenv` | `os.environ` access |

## Tools

| Tool | Use For |
|------|---------|
| `pytest-mock` (mocker fixture) | General-purpose patching |
| `responses` | `requests` library mocking |
| `respx` | `httpx` library mocking |
| `freezegun` / `time_machine` | Time freezing |
| `monkeypatch` | Environment variables, attributes |
| `tmp_path` | Temporary filesystem |

## Pattern: Dependency Injection

```python
# BAD: Hard to test (hidden dependency)
class OrderService:
    def place_order(self, order):
        client = PaymentGateway()  # Hidden dependency
        return client.charge(order.total)

# GOOD: Testable (injected dependency)
class OrderService:
    def __init__(self, payment_gateway):
        self.gateway = payment_gateway

    def place_order(self, order):
        return self.gateway.charge(order.total)

# Test with fake
class FakePaymentGateway:
    def charge(self, amount):
        return {"status": "ok", "charged": amount}

def test_place_order_charges_total():
    service = OrderService(FakePaymentGateway())
    result = service.place_order(Order(total=100))
    assert result["charged"] == 100
```

## Pattern: HTTP Mocking with responses

```python
import responses
import requests

@responses.activate
def test_fetch_user_returns_name():
    responses.add(
        responses.GET,
        "https://api.example.com/users/1",
        json={"name": "Alice"},
        status=200
    )

    result = fetch_user(1)
    assert result["name"] == "Alice"

@responses.activate
def test_fetch_user_handles_404():
    responses.add(
        responses.GET,
        "https://api.example.com/users/999",
        json={"error": "not found"},
        status=404
    )

    with pytest.raises(UserNotFoundError):
        fetch_user(999)
```

## Pattern: Time Freezing

```python
from freezegun import freeze_time

@freeze_time("2025-01-15 10:00:00")
def test_report_uses_current_date():
    report = generate_daily_report()
    assert report.date == date(2025, 1, 15)

@freeze_time("2025-01-15 23:59:59")
def test_deadline_check_at_boundary():
    task = Task(deadline=datetime(2025, 1, 15))
    assert task.is_due() is True
```

## Pattern: monkeypatch for Environment

```python
def test_config_reads_from_env(monkeypatch):
    monkeypatch.setenv("API_KEY", "test-key-123")
    monkeypatch.setenv("DEBUG", "true")

    config = load_config()
    assert config.api_key == "test-key-123"
    assert config.debug is True

def test_config_defaults_when_env_missing(monkeypatch):
    monkeypatch.delenv("API_KEY", raising=False)

    config = load_config()
    assert config.api_key is None
```

## Must Follow

- [ ] Mock only at system boundaries (network, time, filesystem, env)
- [ ] Prefer dependency injection over `patch()`
- [ ] Use `tmp_path` for filesystem tests (real FS, auto-cleaned)
- [ ] Verify mock was called with expected arguments (`assert_called_once_with`)
- [ ] Reset mocks between tests (pytest-mock does this automatically)

## Must Avoid

- Mocking your own classes (refactor to use injection instead)
- Mocking too deep (patch at the nearest boundary)
- Forgetting to assert mock interactions (mock existed but was never verified)
- Using `patch()` as decorator AND context manager in the same test
- Mocking return values without testing error paths
