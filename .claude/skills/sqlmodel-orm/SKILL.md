---
name: sqlmodel-orm
description: Expert guidance for SQLModel ORM with Python. Use when defining database models, creating table schemas, setting up relationships between models, writing database queries, or integrating with FastAPI. Triggers include "SQLModel", "ORM", "database model", "table definition", "relationships", "foreign key", "select()", "SQLModel Field", or requests to create database schemas with Python.
version: "1.0"
last_verified: "2025-01"
---

# SQLModel ORM

Expert guidance for SQLModel - a library combining SQLAlchemy and Pydantic for type-safe database models with validation.

## What This Skill Does

- Table definitions with type-safe models
- Field constraints, indexes, and validation
- Relationships (one-to-many, many-to-many)
- Type-safe queries with select()
- Pydantic integration for validation
- FastAPI request/response model patterns
- CRUD operation patterns

## What This Skill Does NOT Do

- Database migrations (use Alembic)
- Connection pooling configuration (use database skill)
- Raw SQL optimization
- Database administration
- Async database operations (use encode/databases)
- Multi-database routing
- Database backup/restore

## Quick Start

### Installation

```bash
pip install sqlmodel psycopg2-binary
```

### Basic Table Definition

```python
from sqlmodel import SQLModel, Field
from datetime import datetime
from typing import Optional

class Todo(SQLModel, table=True):
    __tablename__ = "todos"

    id: Optional[int] = Field(default=None, primary_key=True)
    title: str = Field(max_length=200)
    status: str = Field(default="active")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
```

### Database Connection

```python
from sqlmodel import create_engine, SQLModel

DATABASE_URL = "postgresql://user:password@localhost:5432/todos"
engine = create_engine(DATABASE_URL, echo=True)

SQLModel.metadata.create_all(engine)
```

## Core Patterns

### 1. Field Types and Constraints

```python
from sqlmodel import SQLModel, Field, Column
from sqlalchemy import Text

class Todo(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    title: str = Field(max_length=200, min_length=1)
    description: Optional[str] = Field(default=None, sa_column=Column(Text))
    status: str = Field(default="active")
    priority: int = Field(default=0, ge=0, le=10)
    slug: str = Field(unique=True, index=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
```

### 2. Relationships

```python
from sqlmodel import Relationship

class User(SQLModel, table=True):
    __tablename__ = "users"

    id: Optional[int] = Field(default=None, primary_key=True)
    email: str = Field(unique=True, index=True)
    todos: list["Todo"] = Relationship(back_populates="owner")

class Todo(SQLModel, table=True):
    __tablename__ = "todos"

    id: Optional[int] = Field(default=None, primary_key=True)
    title: str
    owner_id: Optional[int] = Field(default=None, foreign_key="users.id")
    owner: Optional[User] = Relationship(back_populates="todos")
```

### 3. Query Patterns

```python
from sqlmodel import Session, select

def get_todo(session: Session, todo_id: int) -> Optional[Todo]:
    return session.get(Todo, todo_id)

def get_all_todos(session: Session) -> list[Todo]:
    return session.exec(select(Todo)).all()

def get_active_todos(session: Session) -> list[Todo]:
    statement = select(Todo).where(Todo.status == "active")
    return session.exec(statement).all()

def get_todos_paginated(session: Session, skip: int = 0, limit: int = 10) -> list[Todo]:
    statement = select(Todo).offset(skip).limit(limit)
    return session.exec(statement).all()
```

### 4. CRUD Operations

```python
def create_todo(session: Session, title: str) -> Todo:
    todo = Todo(title=title)
    session.add(todo)
    session.commit()
    session.refresh(todo)
    return todo

def update_todo(session: Session, todo_id: int, title: str = None) -> Optional[Todo]:
    todo = session.get(Todo, todo_id)
    if not todo:
        return None
    if title:
        todo.title = title
    todo.updated_at = datetime.utcnow()
    session.add(todo)
    session.commit()
    session.refresh(todo)
    return todo

def delete_todo(session: Session, todo_id: int) -> bool:
    todo = session.get(Todo, todo_id)
    if not todo:
        return False
    session.delete(todo)
    session.commit()
    return True
```

### 5. FastAPI Integration

```python
# Separate table and schema models
class Todo(SQLModel, table=True):
    __tablename__ = "todos"
    id: Optional[int] = Field(default=None, primary_key=True)
    title: str = Field(max_length=200)
    status: str = Field(default="active")

class TodoCreate(SQLModel):
    title: str = Field(min_length=1, max_length=200)
    status: str = Field(default="active")

class TodoUpdate(SQLModel):
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    status: Optional[str] = None

class TodoRead(SQLModel):
    id: int
    title: str
    status: str
```

## Output Specification

A properly configured SQLModel setup includes:

- [ ] Table models with `table=True` in models.py
- [ ] Separate schema models for Create/Update/Read
- [ ] Primary keys as `Optional[int]` with `default=None`
- [ ] Timestamps with `default_factory=datetime.utcnow`
- [ ] Foreign keys with `foreign_key="table.column"`
- [ ] Relationships with `back_populates`
- [ ] Indexes on frequently queried columns

## Quality Gate Checklist

Before marking models complete, verify:

- [ ] All tables have primary keys
- [ ] Foreign keys reference existing tables
- [ ] Relationships have matching back_populates
- [ ] Field constraints (max_length, ge, le) are appropriate
- [ ] Unique constraints where business logic requires
- [ ] Indexes on foreign keys and filter columns
- [ ] Separate Create/Read/Update schemas for API
- [ ] No circular import issues

## Naming Conventions

| Element | Convention | Example |
|---------|------------|---------|
| Table names | Plural, snake_case | `todos`, `user_profiles` |
| Model classes | Singular, PascalCase | `Todo`, `UserProfile` |
| Columns | snake_case | `created_at`, `owner_id` |
| Relationships | Plural (one-to-many) | `todos` |
| Relationships | Singular (many-to-one) | `owner` |

## Official Documentation

| Resource | URL | Use For |
|----------|-----|---------|
| SQLModel Docs | https://sqlmodel.tiangolo.com/ | Core concepts, tutorials |
| SQLAlchemy | https://docs.sqlalchemy.org/ | Advanced queries, events |
| Pydantic | https://docs.pydantic.dev/ | Field validation, types |
| Alembic | https://alembic.sqlalchemy.org/ | Database migrations |

For patterns not covered here, consult official docs above.

## Keeping Current

- **Last verified:** 2025-01
- **Check for updates:** https://github.com/tiangolo/sqlmodel/releases
- SQLModel is actively developed; check for new patterns
- Built on SQLAlchemy 2.0+ and Pydantic v2

## Common Anti-Patterns

### Avoid These Mistakes

```python
# BAD: Mutable default
class Todo(SQLModel, table=True):
    tags: list = []  # Shared between instances!

# GOOD: Use default_factory
class Todo(SQLModel, table=True):
    tags: list = Field(default_factory=list)

# BAD: Missing Optional for nullable FK
class Todo(SQLModel, table=True):
    owner_id: int = Field(foreign_key="users.id")  # Can't be NULL

# GOOD: Optional for nullable FK
class Todo(SQLModel, table=True):
    owner_id: Optional[int] = Field(default=None, foreign_key="users.id")
```

## Reference Guides

| File | When to Read |
|------|--------------|
| `references/relationships.md` | Many-to-many, cascade, lazy loading |
| `references/query-optimization.md` | Joins, eager loading, N+1 prevention |
| `references/troubleshooting.md` | Common SQLModel issues and solutions |
| `../INTEGRATION.md` | How all 5 skills work together |

## Scripts

| Script | Purpose |
|--------|---------|
| `scripts/init_models.py` | Generate SQLModel table from schema |
