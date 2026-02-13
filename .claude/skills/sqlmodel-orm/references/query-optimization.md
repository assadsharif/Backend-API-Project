# Query Optimization Patterns

## N+1 Query Problem

### Problem Example

```python
# BAD: N+1 queries
todos = session.exec(select(Todo)).all()  # 1 query

for todo in todos:
    print(todo.owner.name)  # N queries (one per todo)
# Total: 1 + N queries
```

### Solution: Eager Loading

```python
# GOOD: 2 queries total
from sqlalchemy.orm import selectinload

statement = select(Todo).options(selectinload(Todo.owner))
todos = session.exec(statement).all()  # 2 queries

for todo in todos:
    print(todo.owner.name)  # No additional query
# Total: 2 queries
```

## Join Strategies

### Inner Join

```python
from sqlmodel import select
from sqlalchemy import join

# Explicit join
statement = select(Todo, User).join(User, Todo.owner_id == User.id)
results = session.exec(statement).all()

for todo, user in results:
    print(f"{todo.title} - {user.name}")
```

### Left Outer Join

```python
from sqlalchemy import outerjoin

# Include todos without owners
statement = select(Todo, User).select_from(
    outerjoin(Todo, User, Todo.owner_id == User.id)
)
results = session.exec(statement).all()
```

### Join with Filter

```python
# Join and filter
statement = (
    select(Todo)
    .join(User)
    .where(User.email.like("%@example.com"))
)
todos = session.exec(statement).all()
```

## Pagination Optimization

### Offset/Limit Pagination

```python
def get_paginated_todos(
    session: Session,
    page: int = 1,
    page_size: int = 10
) -> List[Todo]:
    offset = (page - 1) * page_size
    statement = select(Todo).offset(offset).limit(page_size)
    return session.exec(statement).all()
```

### Cursor-Based Pagination (Better for Large Datasets)

```python
def get_todos_after_cursor(
    session: Session,
    cursor_id: Optional[int] = None,
    limit: int = 10
) -> List[Todo]:
    statement = select(Todo).order_by(Todo.id)

    if cursor_id:
        statement = statement.where(Todo.id > cursor_id)

    statement = statement.limit(limit)
    return session.exec(statement).all()
```

### Pagination with Total Count

```python
from sqlalchemy import func

def get_paginated_with_count(
    session: Session,
    page: int = 1,
    page_size: int = 10
) -> tuple[List[Todo], int]:
    # Get total count
    count_statement = select(func.count()).select_from(Todo)
    total = session.exec(count_statement).one()

    # Get page
    offset = (page - 1) * page_size
    statement = select(Todo).offset(offset).limit(page_size)
    todos = session.exec(statement).all()

    return todos, total
```

## Index Usage

### Single Column Index

```python
class Todo(SQLModel, table=True):
    __tablename__ = "todos"

    id: Optional[int] = Field(default=None, primary_key=True)
    status: str = Field(index=True)  # Single column index
    owner_id: int = Field(foreign_key="users.id", index=True)
```

### Composite Index

```python
from sqlalchemy import Index

class Todo(SQLModel, table=True):
    __tablename__ = "todos"
    __table_args__ = (
        Index('idx_owner_status', 'owner_id', 'status'),
        Index('idx_status_created', 'status', 'created_at'),
    )

    id: Optional[int] = Field(default=None, primary_key=True)
    title: str
    status: str
    owner_id: int
    created_at: datetime
```

### Partial Index (PostgreSQL)

```python
from sqlalchemy import Index

class Todo(SQLModel, table=True):
    __tablename__ = "todos"
    __table_args__ = (
        Index(
            'idx_active_todos',
            'owner_id',
            'created_at',
            postgresql_where=text("status = 'active'")
        ),
    )

    id: Optional[int] = Field(default=None, primary_key=True)
    status: str
    owner_id: int
    created_at: datetime
```

## Query Result Caching

### Session-Level Caching

```python
# SQLModel/SQLAlchemy automatically caches within a session
session = Session(engine)

# First query - hits database
todo1 = session.get(Todo, 1)

# Second query - returns cached object
todo2 = session.get(Todo, 1)

assert todo1 is todo2  # Same object instance
```

### Application-Level Caching

```python
from functools import lru_cache
from typing import List

@lru_cache(maxsize=128)
def get_active_todos_cached(session_id: int) -> List[dict]:
    """Cache active todos for 5 minutes"""
    session = Session(engine)
    todos = session.exec(select(Todo).where(Todo.status == "active")).all()
    return [todo.model_dump() for todo in todos]
```

## Bulk Operations Performance

### Bulk Insert

```python
# SLOW: Individual inserts
for i in range(1000):
    todo = Todo(title=f"Todo {i}", status="active")
    session.add(todo)
    session.commit()  # 1000 commits

# FAST: Bulk insert
todos = [Todo(title=f"Todo {i}", status="active") for i in range(1000)]
session.add_all(todos)
session.commit()  # 1 commit
```

### Bulk Update

```python
# SLOW: Individual updates
todos = session.exec(select(Todo).where(Todo.status == "active")).all()
for todo in todos:
    todo.status = "completed"
    session.add(todo)
session.commit()

# FAST: Bulk update
from sqlalchemy import update

statement = (
    update(Todo)
    .where(Todo.status == "active")
    .values(status="completed")
)
session.exec(statement)
session.commit()
```

### Bulk Delete

```python
# SLOW: Individual deletes
todos = session.exec(select(Todo).where(Todo.status == "completed")).all()
for todo in todos:
    session.delete(todo)
session.commit()

# FAST: Bulk delete
from sqlalchemy import delete

statement = delete(Todo).where(Todo.status == "completed")
session.exec(statement)
session.commit()
```

## Selective Column Loading

### Load Only Specific Columns

```python
from sqlalchemy import select as sa_select

# Load only id and title (not all columns)
statement = sa_select(Todo.id, Todo.title).where(Todo.status == "active")
results = session.exec(statement).all()

for todo_id, title in results:
    print(f"{todo_id}: {title}")
```

### Deferred Loading

```python
from sqlalchemy.orm import defer

# Defer loading large columns
statement = select(Todo).options(defer(Todo.description))
todos = session.exec(statement).all()

# Description loaded only when accessed
for todo in todos:
    print(todo.title)  # No query
    if needed:
        print(todo.description)  # Query executed here
```

## Query Optimization with explain()

### Analyze Query Performance (PostgreSQL)

```python
from sqlalchemy import text

def explain_query(session: Session, statement):
    """Show query execution plan"""
    compiled = statement.compile(
        compile_kwargs={"literal_binds": True}
    )

    explain_statement = text(f"EXPLAIN ANALYZE {compiled}")
    result = session.exec(explain_statement).all()

    for row in result:
        print(row)

# Usage
statement = select(Todo).where(Todo.status == "active")
explain_query(session, statement)
```

## Connection Pooling Optimization

### Configure Pool Size

```python
from sqlmodel import create_engine

engine = create_engine(
    DATABASE_URL,
    pool_size=10,          # Number of persistent connections
    max_overflow=20,       # Additional connections when pool full
    pool_timeout=30,       # Wait time for connection
    pool_recycle=3600,     # Recycle connections after 1 hour
    pool_pre_ping=True,    # Verify connections before use
    echo_pool=True         # Log pool activity
)
```

## Subqueries

### Subquery in WHERE Clause

```python
from sqlalchemy import select as sa_select

# Find todos where owner has more than 5 todos
subquery = (
    sa_select(Todo.owner_id)
    .group_by(Todo.owner_id)
    .having(func.count(Todo.id) > 5)
)

statement = select(Todo).where(Todo.owner_id.in_(subquery))
todos = session.exec(statement).all()
```

### Correlated Subquery

```python
# Find users with their todo count
from sqlalchemy.orm import aliased

TodoCount = aliased(Todo)

subquery = (
    select(func.count(TodoCount.id))
    .where(TodoCount.owner_id == User.id)
    .correlate(User)
    .scalar_subquery()
)

statement = select(User, subquery.label("todo_count"))
results = session.exec(statement).all()
```

## Query Hints

### Use Index Hint (Database-Specific)

```python
from sqlalchemy import text

# PostgreSQL specific
statement = select(Todo).prefix_with(
    text("/*+ INDEX(todos idx_status_created) */")
)
```

## Batch Processing

### Process Large Result Sets in Batches

```python
def process_todos_in_batches(session: Session, batch_size: int = 1000):
    """Process todos in batches to avoid memory issues"""
    offset = 0

    while True:
        statement = select(Todo).offset(offset).limit(batch_size)
        todos = session.exec(statement).all()

        if not todos:
            break

        for todo in todos:
            # Process each todo
            process_todo(todo)

        offset += batch_size
        session.expire_all()  # Clear session cache
```

## Read-Only Queries

### Optimize for Read-Only Operations

```python
def get_todos_readonly(session: Session) -> List[Todo]:
    """Read-only query - no tracking changes"""
    statement = select(Todo).execution_options(
        populate_existing=False,
        autoflush=False
    )
    return session.exec(statement).all()
```
