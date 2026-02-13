# Database TDD (SQLModel / SQLAlchemy)

## Core Principle

Test behavior, not implementation. Each test runs in a transaction and rolls back.

## Tools

| Tool | Use For |
|------|---------|
| SQLModel | Model definitions + ORM queries |
| SQLAlchemy | Complex queries, raw SQL |
| In-memory SQLite | Unit test database |
| PostgreSQL (testcontainers) | Integration test database |

## Test Database Setup

```python
import pytest
from sqlmodel import Session, SQLModel, create_engine

@pytest.fixture
def engine():
    engine = create_engine("sqlite://", echo=False)
    SQLModel.metadata.create_all(engine)
    return engine

@pytest.fixture
def session(engine):
    with Session(engine) as session:
        yield session
        session.rollback()
```

## Test Order

1. Model validation errors (required fields, constraints)
2. CRUD operations (create, read)
3. Query filters and edge cases
4. Relationship loading
5. Migration compatibility

## Pattern: Repository Testing

```python
class TestUserRepository:
    def test_create_user_missing_email_raises(self, session):
        with pytest.raises(ValidationError):
            User(name="Test")

    def test_create_user_stores_in_db(self, session):
        user = User(name="Test", email="a@b.com")
        session.add(user)
        session.commit()
        assert session.get(User, user.id) is not None

    def test_find_by_email_returns_none_when_missing(self, session):
        result = find_user_by_email(session, "missing@x.com")
        assert result is None
```

## Must Follow

- [ ] Use in-memory SQLite for unit tests
- [ ] Each test in its own transaction (rollback after)
- [ ] Apply Repository Pattern (separate DB logic from business logic)
- [ ] Test migrations with alembic upgrade/downgrade
- [ ] No test-to-test data dependencies

## Must Avoid

- Shared database state between tests
- Testing ORM internals (e.g., SQL generation)
- Production database in tests
- `session.commit()` without rollback strategy
