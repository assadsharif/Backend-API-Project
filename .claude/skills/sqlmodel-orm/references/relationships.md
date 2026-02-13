# Advanced Relationship Patterns

## Many-to-Many Relationships

### Using Link Table

```python
from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, List

# Link table (association table)
class TodoTag(SQLModel, table=True):
    __tablename__ = "todo_tags"

    todo_id: int = Field(foreign_key="todos.id", primary_key=True)
    tag_id: int = Field(foreign_key="tags.id", primary_key=True)

# Models with many-to-many relationship
class Todo(SQLModel, table=True):
    __tablename__ = "todos"

    id: Optional[int] = Field(default=None, primary_key=True)
    title: str

    # Many-to-many relationship
    tags: List["Tag"] = Relationship(back_populates="todos", link_model=TodoTag)

class Tag(SQLModel, table=True):
    __tablename__ = "tags"

    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(unique=True)

    # Many-to-many relationship
    todos: List[Todo] = Relationship(back_populates="tags", link_model=TodoTag)

# Usage
def add_tag_to_todo(session: Session, todo_id: int, tag_name: str):
    todo = session.get(Todo, todo_id)
    tag = session.exec(select(Tag).where(Tag.name == tag_name)).first()

    if not tag:
        tag = Tag(name=tag_name)
        session.add(tag)

    if tag not in todo.tags:
        todo.tags.append(tag)

    session.commit()
```

### Many-to-Many with Extra Fields

```python
from datetime import datetime

# Link table with extra fields
class TodoTag(SQLModel, table=True):
    __tablename__ = "todo_tags"

    todo_id: int = Field(foreign_key="todos.id", primary_key=True)
    tag_id: int = Field(foreign_key="tags.id", primary_key=True)

    # Extra fields
    created_at: datetime = Field(default_factory=datetime.utcnow)
    created_by: Optional[int] = Field(default=None, foreign_key="users.id")

    # Relationships to access the link table directly
    todo: "Todo" = Relationship()
    tag: "Tag" = Relationship()
```

## Cascade Operations

### Delete Cascade

```python
from sqlmodel import Relationship

class User(SQLModel, table=True):
    __tablename__ = "users"

    id: Optional[int] = Field(default=None, primary_key=True)
    email: str

    # When user is deleted, all their todos are deleted
    todos: List["Todo"] = Relationship(
        back_populates="owner",
        sa_relationship_kwargs={"cascade": "all, delete-orphan"}
    )

class Todo(SQLModel, table=True):
    __tablename__ = "todos"

    id: Optional[int] = Field(default=None, primary_key=True)
    title: str
    owner_id: int = Field(foreign_key="users.id")

    owner: User = Relationship(back_populates="todos")

# When you delete a user, all their todos are automatically deleted
def delete_user_and_todos(session: Session, user_id: int):
    user = session.get(User, user_id)
    session.delete(user)  # Todos are automatically deleted
    session.commit()
```

### Update Cascade

```python
class User(SQLModel, table=True):
    __tablename__ = "users"

    id: Optional[int] = Field(default=None, primary_key=True)
    email: str

    todos: List["Todo"] = Relationship(
        back_populates="owner",
        sa_relationship_kwargs={
            "cascade": "all",
            "passive_deletes": False
        }
    )
```

### Prevent Delete (Restrict)

```python
from sqlalchemy import ForeignKey

class Todo(SQLModel, table=True):
    __tablename__ = "todos"

    id: Optional[int] = Field(default=None, primary_key=True)
    title: str

    # Prevent deleting user if they have todos
    owner_id: int = Field(
        sa_column=Column(
            Integer,
            ForeignKey("users.id", ondelete="RESTRICT")
        )
    )
```

## Lazy Loading vs Eager Loading

### Lazy Loading (Default)

```python
# Relationship data loaded only when accessed
todo = session.get(Todo, 1)
# No query for owner yet

owner_name = todo.owner.name  # Query executed here
```

### Eager Loading with selectinload

```python
from sqlalchemy.orm import selectinload

# Load todos with their owners in one go
statement = select(Todo).options(selectinload(Todo.owner))
todos = session.exec(statement).all()

# Access owner without additional query
for todo in todos:
    print(todo.owner.name)  # No additional query
```

### Eager Loading with joinedload

```python
from sqlalchemy.orm import joinedload

# Load with JOIN
statement = select(Todo).options(joinedload(Todo.owner))
todos = session.exec(statement).all()

for todo in todos:
    print(todo.owner.name)  # Already loaded
```

## Self-Referential Relationships

### Tree Structure (Parent-Child)

```python
class Category(SQLModel, table=True):
    __tablename__ = "categories"

    id: Optional[int] = Field(default=None, primary_key=True)
    name: str

    # Self-referential foreign key
    parent_id: Optional[int] = Field(default=None, foreign_key="categories.id")

    # Relationships
    parent: Optional["Category"] = Relationship(
        back_populates="children",
        sa_relationship_kwargs={"remote_side": "Category.id"}
    )
    children: List["Category"] = Relationship(back_populates="parent")

# Usage
def get_category_tree(session: Session, category_id: int):
    category = session.get(Category, category_id)

    def print_tree(cat, indent=0):
        print("  " * indent + cat.name)
        for child in cat.children:
            print_tree(child, indent + 1)

    print_tree(category)
```

## Bi-directional Relationships

### Proper Back Population

```python
class User(SQLModel, table=True):
    __tablename__ = "users"

    id: Optional[int] = Field(default=None, primary_key=True)
    email: str

    # back_populates must match the attribute name in Todo
    todos: List["Todo"] = Relationship(back_populates="owner")

class Todo(SQLModel, table=True):
    __tablename__ = "todos"

    id: Optional[int] = Field(default=None, primary_key=True)
    title: str
    owner_id: int = Field(foreign_key="users.id")

    # back_populates must match the attribute name in User
    owner: User = Relationship(back_populates="todos")

# Both sides stay in sync
user = User(email="user@example.com")
todo = Todo(title="Task", owner=user)
session.add(todo)
session.commit()

# user.todos automatically contains the todo
assert todo in user.todos
```

## Composite Foreign Keys

```python
class OrderItem(SQLModel, table=True):
    __tablename__ = "order_items"

    order_id: int = Field(foreign_key="orders.id", primary_key=True)
    product_id: int = Field(foreign_key="products.id", primary_key=True)
    quantity: int

    # Composite primary key is automatically created
```

## Polymorphic Relationships

### Single Table Inheritance

```python
from sqlmodel import Field

class Employee(SQLModel, table=True):
    __tablename__ = "employees"

    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    type: str  # Discriminator column

    # Type-specific fields (nullable for other types)
    salary: Optional[float] = None
    hourly_rate: Optional[float] = None

# In application code
class Manager(Employee):
    type: str = Field(default="manager", sa_column_kwargs={"name": "type"})
    salary: float

class Contractor(Employee):
    type: str = Field(default="contractor", sa_column_kwargs={"name": "type"})
    hourly_rate: float
```

## Circular Dependencies

### Forward References

```python
from typing import TYPE_CHECKING, List, Optional

if TYPE_CHECKING:
    from .user import User

class Todo(SQLModel, table=True):
    __tablename__ = "todos"

    id: Optional[int] = Field(default=None, primary_key=True)
    title: str
    owner_id: int = Field(foreign_key="users.id")

    # Use string for forward reference
    owner: Optional["User"] = Relationship(back_populates="todos")
```

## Relationship Loading Strategies

### Subquery Load

```python
from sqlalchemy.orm import subqueryload

# Load related data with subquery
statement = select(User).options(subqueryload(User.todos))
users = session.exec(statement).all()
```

### Immediate Load

```python
from sqlalchemy.orm import immediateload

# Load relationship immediately
statement = select(Todo).options(immediateload(Todo.owner))
todos = session.exec(statement).all()
```

### No Load

```python
from sqlalchemy.orm import noload

# Don't load relationship at all
statement = select(Todo).options(noload(Todo.owner))
todos = session.exec(statement).all()
# Accessing todo.owner will raise an error
```
