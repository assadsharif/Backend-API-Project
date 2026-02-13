#!/usr/bin/env python3
"""Initialize SQLModel models with best practices.

This script generates:
- Base model with timestamps
- Example Todo model
- Separate schema models (Create, Update, Read)
"""
import argparse
from pathlib import Path


def create_base_model(models_dir: Path) -> None:
    """Create base.py with timestamp mixin."""
    base_py = models_dir / "base.py"

    content = '''"""Base models and mixins."""
from sqlmodel import SQLModel, Field
from datetime import datetime


class TimestampMixin(SQLModel):
    """Mixin for created_at and updated_at timestamps."""
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
'''

    base_py.write_text(content)
    print(f"✓ Created {base_py}")


def create_todo_model(models_dir: Path) -> None:
    """Create todo.py with Todo model."""
    todo_py = models_dir / "todo.py"

    content = '''"""Todo model."""
from sqlmodel import SQLModel, Field, Relationship
from typing import Optional
from datetime import datetime

from .base import TimestampMixin


class Todo(TimestampMixin, table=True):
    """Todo database model."""
    __tablename__ = "todos"

    id: Optional[int] = Field(default=None, primary_key=True)
    title: str = Field(max_length=200, min_length=1)
    status: str = Field(default="active")  # "active" or "completed"

    # Optional: Foreign key to user
    # user_id: Optional[int] = Field(default=None, foreign_key="users.id")
    # user: Optional["User"] = Relationship(back_populates="todos")
'''

    todo_py.write_text(content)
    print(f"✓ Created {todo_py}")


def create_models_init(models_dir: Path) -> None:
    """Create __init__.py for models."""
    init_py = models_dir / "__init__.py"

    content = '''"""SQLModel models."""
from .base import TimestampMixin
from .todo import Todo

__all__ = ["TimestampMixin", "Todo"]
'''

    init_py.write_text(content)
    print(f"✓ Created {init_py}")


def create_todo_schemas(schemas_dir: Path) -> None:
    """Create todo.py with Pydantic schemas."""
    todo_py = schemas_dir / "todo.py"

    content = '''"""Todo schemas for API requests/responses."""
from pydantic import BaseModel, Field
from datetime import datetime
from typing import Literal, Optional


class TodoBase(BaseModel):
    """Base todo schema."""
    title: str = Field(..., min_length=1, max_length=200)
    status: Literal["active", "completed"] = "active"


class TodoCreate(TodoBase):
    """Schema for creating a todo."""
    pass


class TodoUpdate(BaseModel):
    """Schema for updating a todo."""
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    status: Optional[Literal["active", "completed"]] = None


class TodoRead(TodoBase):
    """Schema for reading a todo."""
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
'''

    todo_py.write_text(content)
    print(f"✓ Created {todo_py}")


def create_schemas_init(schemas_dir: Path) -> None:
    """Create __init__.py for schemas."""
    init_py = schemas_dir / "__init__.py"

    content = '''"""Pydantic schemas."""
from .todo import TodoBase, TodoCreate, TodoUpdate, TodoRead

__all__ = ["TodoBase", "TodoCreate", "TodoUpdate", "TodoRead"]
'''

    init_py.write_text(content)
    print(f"✓ Created {init_py}")


def print_next_steps():
    """Print next steps."""
    print("\n" + "=" * 60)
    print("✅ SQLModel models initialized successfully!")
    print("=" * 60)
    print("\nCreated:")
    print("  models/")
    print("    ├── __init__.py")
    print("    ├── base.py      (TimestampMixin)")
    print("    └── todo.py      (Todo model)")
    print("  schemas/")
    print("    ├── __init__.py")
    print("    └── todo.py      (TodoCreate, TodoUpdate, TodoRead)")
    print("\nNext steps:")
    print("1. Import models in your database.py")
    print("2. Run create_db_and_tables() to create tables")
    print("3. Use schemas in your API endpoints")
    print("=" * 60)


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Initialize SQLModel models"
    )
    parser.add_argument(
        "project_root",
        nargs="?",
        default=".",
        help="Project root directory (default: current directory)"
    )

    args = parser.parse_args()
    project_root = Path(args.project_root).resolve()

    models_dir = project_root / "models"
    schemas_dir = project_root / "schemas"

    models_dir.mkdir(parents=True, exist_ok=True)
    schemas_dir.mkdir(parents=True, exist_ok=True)

    print(f"Initializing SQLModel models in {project_root}\n")

    create_base_model(models_dir)
    create_todo_model(models_dir)
    create_models_init(models_dir)
    create_todo_schemas(schemas_dir)
    create_schemas_init(schemas_dir)

    print_next_steps()


if __name__ == "__main__":
    main()
