# SQLModel Troubleshooting Guide

Common issues and solutions when using SQLModel ORM.

## Table Not Created

### Symptoms
- `Table 'xxx' doesn't exist`
- Missing tables in database

### Solutions

```python
# Ensure create_all is called
from sqlmodel import SQLModel

def create_db_and_tables():
    SQLModel.metadata.create_all(engine)

# Call on startup
create_db_and_tables()

# Ensure models are imported BEFORE create_all
from models import User, Todo  # Import first!
SQLModel.metadata.create_all(engine)

# Check table=True is set
class Todo(SQLModel, table=True):  # Not just SQLModel
    id: int
```

## Relationship Errors

### Symptoms
- `RelationshipProperty has no attribute`
- Circular import errors

### Solutions

```python
# Use forward references with quotes
class User(SQLModel, table=True):
    todos: list["Todo"] = Relationship(back_populates="owner")

class Todo(SQLModel, table=True):
    owner: Optional["User"] = Relationship(back_populates="todos")

# Ensure back_populates match
# User has: todos -> back_populates="owner"
# Todo has: owner -> back_populates="todos"

# For circular imports
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .user import User
```

## Foreign Key Issues

### Symptoms
- `Could not determine join condition`
- Foreign key not recognized

### Solutions

```python
# Correct foreign key syntax
class Todo(SQLModel, table=True):
    # Must reference table.column
    owner_id: Optional[int] = Field(
        default=None,
        foreign_key="users.id"  # Table name, not class name
    )

# Table name comes from __tablename__ or class name lowercase
class User(SQLModel, table=True):
    __tablename__ = "users"  # Explicit
    # or defaults to "user"
```

## Validation Errors

### Symptoms
- `ValidationError`
- `value is not a valid integer`

### Solutions

```python
# Check types match
class Todo(SQLModel):
    id: int          # Required, must be int
    title: str       # Required, must be str
    count: int = 0   # Optional with default

# Use Optional for nullable
from typing import Optional

class Todo(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    description: Optional[str] = None

# Convert types properly
todo = Todo(
    id=int(request.id),  # Convert from string
    title=str(request.title)
)
```

## Session Issues

### Symptoms
- `Object is already attached to session`
- `DetachedInstanceError`

### Solutions

```python
# Don't reuse session objects across sessions
# BAD
todo = session1.get(Todo, 1)
session2.add(todo)  # Error: attached to session1!

# GOOD
todo = session2.get(Todo, 1)

# Refresh after commit
session.add(todo)
session.commit()
session.refresh(todo)  # Now has updated data

# Merge for detached objects
todo = session.merge(detached_todo)
```

## Query Returns None

### Symptoms
- `None` when data exists
- Empty results

### Solutions

```python
# Check query syntax
# get() returns None if not found
todo = session.get(Todo, 999)  # Returns None

# Use first() with select
from sqlmodel import select

statement = select(Todo).where(Todo.id == 1)
todo = session.exec(statement).first()  # Returns None or Todo

# all() returns empty list
todos = session.exec(select(Todo)).all()  # Returns []

# Debug: print the query
statement = select(Todo).where(Todo.status == "active")
print(statement)  # See generated SQL
```

## N+1 Query Problem

### Symptoms
- Slow queries
- Many SQL statements for one request

### Solutions

```python
# Use eager loading
from sqlalchemy.orm import selectinload, joinedload

# Load related data in single query
statement = select(User).options(selectinload(User.todos))
users = session.exec(statement).all()

# Access without additional queries
for user in users:
    print(user.todos)  # Already loaded!
```

## Migration Issues

### Symptoms
- Schema mismatch
- `Column doesn't exist`

### Solutions

```bash
# Use Alembic for migrations
pip install alembic
alembic init alembic

# Generate migration
alembic revision --autogenerate -m "Add column"

# Apply migration
alembic upgrade head

# Check current schema
alembic current
```

## Type Errors

### Symptoms
- `Incompatible types`
- mypy errors

### Solutions

```python
# Use proper type hints
from typing import Optional, List
from datetime import datetime

class Todo(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    title: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    tags: List[str] = Field(default_factory=list)

# For JSON columns
from sqlmodel import Field, Column
from sqlalchemy import JSON

class Config(SQLModel, table=True):
    settings: dict = Field(default={}, sa_column=Column(JSON))
```

## Connection Pool Exhaustion

### Symptoms
- `TimeoutError`
- `Too many connections`

### Solutions

```python
# Configure pool size
engine = create_engine(
    DATABASE_URL,
    pool_size=5,
    max_overflow=10,
    pool_timeout=30,
    pool_pre_ping=True
)

# Always close sessions
with Session(engine) as session:
    # Use session
    pass  # Automatically closed

# Or use context manager in FastAPI
def get_session():
    with Session(engine) as session:
        yield session
```

## Quick Debugging

```python
# Enable SQL logging
engine = create_engine(DATABASE_URL, echo=True)

# Print model as dict
print(todo.model_dump())

# Check table columns
print(Todo.__table__.columns.keys())

# Check relationships
print(Todo.__sqlmodel_relationships__)

# Inspect metadata
from sqlmodel import SQLModel
print(SQLModel.metadata.tables.keys())
```
