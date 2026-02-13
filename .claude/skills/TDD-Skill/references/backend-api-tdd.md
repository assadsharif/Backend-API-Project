# Backend / API TDD (FastAPI / Flask)

## Core Principle

Define API contracts through tests FIRST. If a 400 test doesn't exist, the bug already exists.

## Test Order (Strict)

1. Validation errors (400 / 422) before success
2. Auth & permission failures (401 / 403) before happy path
3. Not found (404) before resource operations
4. Status codes before response body assertions

## Tools

| Tool | Use For |
|------|---------|
| `fastapi.testclient.TestClient` | Sync FastAPI endpoint testing |
| `httpx.AsyncClient` | Async FastAPI endpoint testing |
| `factory-boy` | Test data generation (model factories) |
| `faker` | Realistic field values (names, emails, dates) |

## Pattern: FastAPI Test Structure

```python
import pytest
from fastapi.testclient import TestClient
from app.main import app

@pytest.fixture
def client():
    return TestClient(app)

class TestCreateUser:
    """Test POST /users endpoint."""

    def test_missing_required_field_returns_422(self, client):
        response = client.post("/users", json={})
        assert response.status_code == 422

    def test_invalid_email_returns_422(self, client):
        response = client.post("/users", json={"email": "not-email", "name": "X"})
        assert response.status_code == 422

    def test_valid_user_returns_201(self, client):
        response = client.post("/users", json={"email": "a@b.com", "name": "Test"})
        assert response.status_code == 201
        assert response.json()["email"] == "a@b.com"
```

## Pattern: Auth Testing

```python
def test_unauthenticated_request_returns_401(self, client):
    response = client.get("/protected")
    assert response.status_code == 401

def test_unauthorized_role_returns_403(self, client, regular_user_token):
    response = client.get("/admin", headers={"Authorization": f"Bearer {regular_user_token}"})
    assert response.status_code == 403
```

## Anti-Patterns

- Testing framework internals (Pydantic validation, FastAPI routing)
- Hardcoding URLs instead of using `app.url_path_for()`
- Testing with real databases in unit tests
- Asserting response body without checking status code first
