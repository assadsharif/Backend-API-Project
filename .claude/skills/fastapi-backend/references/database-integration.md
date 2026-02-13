# Database Integration with SQLModel

## Connection Management

### Basic Connection

```python
# database.py
from sqlmodel import SQLModel, create_engine, Session
from typing import Generator
import os

DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_engine(DATABASE_URL, echo=True)

def create_db_and_tables():
    """Create all database tables"""
    SQLModel.metadata.create_all(engine)

def get_session() -> Generator[Session, None, None]:
    """Get database session"""
    with Session(engine) as session:
        yield session
```

### Connection Pooling

```python
from sqlmodel import create_engine

engine = create_engine(
    DATABASE_URL,
    echo=True,
    pool_size=5,              # Number of persistent connections
    max_overflow=10,          # Max connections beyond pool_size
    pool_timeout=30,          # Timeout for getting connection
    pool_recycle=3600,        # Recycle connections after 1 hour
    pool_pre_ping=True        # Verify connections before using
)
```

## Model Patterns

### Basic Model with Timestamps

```python
from sqlmodel import SQLModel, Field
from datetime import datetime

class TimestampMixin(SQLModel):
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class Todo(TimestampMixin, table=True):
    __tablename__ = "todos"

    id: int | None = Field(default=None, primary_key=True)
    title: str = Field(max_length=200, index=True)
    status: str = Field(default="active", index=True)
```

### Model with Relationships

```python
from sqlmodel import Field, Relationship
from typing import List, Optional

class User(SQLModel, table=True):
    __tablename__ = "users"

    id: int | None = Field(default=None, primary_key=True)
    email: str = Field(unique=True, index=True)
    name: str

    # Relationship
    todos: List["Todo"] = Relationship(back_populates="owner")

class Todo(SQLModel, table=True):
    __tablename__ = "todos"

    id: int | None = Field(default=None, primary_key=True)
    title: str = Field(max_length=200)
    status: str = Field(default="active")

    # Foreign key
    owner_id: int | None = Field(default=None, foreign_key="users.id")

    # Relationship
    owner: Optional[User] = Relationship(back_populates="todos")
```

### Model with Constraints

```python
from sqlmodel import Field, Column
from sqlalchemy import UniqueConstraint, CheckConstraint

class Todo(SQLModel, table=True):
    __tablename__ = "todos"
    __table_args__ = (
        UniqueConstraint('title', 'owner_id', name='unique_title_per_owner'),
        CheckConstraint('length(title) > 0', name='title_not_empty'),
    )

    id: int | None = Field(default=None, primary_key=True)
    title: str = Field(max_length=200)
    status: str = Field(default="active")
    owner_id: int = Field(foreign_key="users.id")
```

## Query Patterns

### Basic Queries

```python
from sqlmodel import Session, select

# Get by ID
todo = session.get(Todo, todo_id)

# Get all
todos = session.exec(select(Todo)).all()

# Filter
query = select(Todo).where(Todo.status == "active")
todos = session.exec(query).all()

# Get first
todo = session.exec(select(Todo).where(Todo.id == 1)).first()

# Get one (raises if not found or multiple found)
todo = session.exec(select(Todo).where(Todo.id == 1)).one()
```

### Complex Queries

```python
from sqlmodel import select, and_, or_, func

# Multiple conditions (AND)
query = select(Todo).where(
    and_(
        Todo.status == "active",
        Todo.title.contains("important")
    )
)

# OR conditions
query = select(Todo).where(
    or_(
        Todo.status == "active",
        Todo.status == "in_progress"
    )
)

# Count
count = session.exec(select(func.count()).select_from(Todo)).one()

# Joins
query = select(Todo, User).join(User)
results = session.exec(query).all()

# Limit and offset
query = select(Todo).offset(10).limit(20)
todos = session.exec(query).all()

# Order by
query = select(Todo).order_by(Todo.created_at.desc())
todos = session.exec(query).all()
```

## Transaction Management

### Manual Transactions

```python
@router.post("/")
async def create_todo_with_transaction(
    todo_data: TodoCreate,
    session: Session = Depends(get_session)
):
    """Create todo with explicit transaction"""
    try:
        todo = Todo(**todo_data.model_dump())
        session.add(todo)
        session.commit()
        session.refresh(todo)
        return todo
    except Exception as e:
        session.rollback()
        raise
```

### Nested Transactions (Savepoints)

```python
from sqlalchemy.exc import SQLAlchemyError

@router.post("/complex")
async def complex_operation(session: Session = Depends(get_session)):
    """Complex operation with savepoints"""
    try:
        # Main transaction
        todo1 = Todo(title="Main todo", status="active")
        session.add(todo1)
        session.flush()

        # Nested transaction (savepoint)
        savepoint = session.begin_nested()
        try:
            todo2 = Todo(title="Nested todo", status="active")
            session.add(todo2)
            session.flush()
        except SQLAlchemyError:
            savepoint.rollback()
            # Continue with main transaction

        session.commit()
        return {"status": "success"}
    except Exception:
        session.rollback()
        raise
```

## Migrations with Alembic

### Setup Alembic

```bash
pip install alembic
alembic init alembic
```

### Configure Alembic

```python
# alembic/env.py
from sqlmodel import SQLModel
from your_app.models import Todo  # Import all models
from your_app.database import DATABASE_URL

target_metadata = SQLModel.metadata

config.set_main_option("sqlalchemy.url", DATABASE_URL)
```

### Create Migration

```bash
# Auto-generate migration
alembic revision --autogenerate -m "Create todos table"

# Apply migration
alembic upgrade head

# Downgrade
alembic downgrade -1
```

## Session Patterns

### Async Session (for async endpoints)

```python
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlalchemy.ext.asyncio import create_async_engine, AsyncEngine

async_engine: AsyncEngine = create_async_engine(
    DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://"),
    echo=True
)

async def get_async_session() -> AsyncSession:
    async with AsyncSession(async_engine) as session:
        yield session

@router.get("/async")
async def async_endpoint(session: AsyncSession = Depends(get_async_session)):
    """Async endpoint with async session"""
    from sqlalchemy import select
    result = await session.execute(select(Todo))
    todos = result.scalars().all()
    return todos
```

### Session with Auto-commit

```python
from contextlib import contextmanager

@contextmanager
def get_auto_commit_session():
    """Session that auto-commits on success"""
    session = Session(engine)
    try:
        yield session
        session.commit()
    except:
        session.rollback()
        raise
    finally:
        session.close()
```

## Performance Optimization

### Eager Loading (Avoid N+1 Queries)

```python
from sqlmodel import select
from sqlalchemy.orm import selectinload

# Load todos with their owners in one query
query = select(Todo).options(selectinload(Todo.owner))
todos = session.exec(query).all()

# Access owner without additional query
for todo in todos:
    print(todo.owner.name)  # No additional DB query
```

### Bulk Operations

```python
# Bulk insert
todos = [Todo(title=f"Todo {i}", status="active") for i in range(100)]
session.bulk_save_objects(todos)
session.commit()

# Bulk update
session.query(Todo).filter(Todo.status == "active").update(
    {"status": "completed"},
    synchronize_session=False
)
session.commit()
```

### Index Optimization

```python
from sqlmodel import Field

class Todo(SQLModel, table=True):
    __tablename__ = "todos"

    id: int | None = Field(default=None, primary_key=True)
    title: str = Field(max_length=200, index=True)  # Single column index
    status: str = Field(default="active", index=True)
    owner_id: int = Field(foreign_key="users.id", index=True)

    # Composite index via __table_args__
    __table_args__ = (
        Index('idx_status_created', 'status', 'created_at'),
    )
```

## Database Utilities

### Check Connection

```python
from sqlalchemy import text

def check_database_connection() -> bool:
    """Check if database is accessible"""
    try:
        with Session(engine) as session:
            session.exec(text("SELECT 1"))
        return True
    except Exception as e:
        logger.error(f"Database connection failed: {e}")
        return False
```

### Reset Database (Development Only)

```python
def reset_database():
    """Drop all tables and recreate (DEVELOPMENT ONLY)"""
    SQLModel.metadata.drop_all(engine)
    SQLModel.metadata.create_all(engine)
```

### Seed Database

```python
def seed_database():
    """Populate database with initial data"""
    with Session(engine) as session:
        if not session.exec(select(Todo)).first():
            todos = [
                Todo(title="Sample Todo 1", status="active"),
                Todo(title="Sample Todo 2", status="completed"),
            ]
            session.add_all(todos)
            session.commit()
```
