#!/usr/bin/env python3
"""Initialize a FastAPI project with best practices structure.

This script sets up:
- Project directory structure
- Main application file with CORS
- Database configuration
- Router templates
- Environment files
- Requirements file
"""
import argparse
import os
from pathlib import Path


def create_directory_structure(project_root: Path) -> None:
    """Create standard FastAPI directory structure."""
    directories = [
        project_root / "routers",
        project_root / "models",
        project_root / "schemas",
        project_root / "services",
    ]

    for directory in directories:
        directory.mkdir(parents=True, exist_ok=True)
        init_file = directory / "__init__.py"
        if not init_file.exists():
            init_file.write_text("")
        print(f"✓ Created {directory}")


def create_main_py(project_root: Path) -> None:
    """Create main.py with FastAPI app."""
    main_py = project_root / "main.py"

    content = '''"""FastAPI application entry point."""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from database import create_db_and_tables
from routers import todos


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown events."""
    create_db_and_tables()
    yield


app = FastAPI(
    title="API",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(todos.router)


@app.get("/")
async def root():
    """Root endpoint."""
    return {"message": "API", "version": "1.0.0"}


@app.get("/health")
async def health():
    """Health check endpoint."""
    return {"status": "healthy"}
'''

    main_py.write_text(content)
    print(f"✓ Created {main_py}")


def create_database_py(project_root: Path) -> None:
    """Create database.py with SQLModel setup."""
    database_py = project_root / "database.py"

    content = '''"""Database configuration and session management."""
from sqlmodel import SQLModel, Session, create_engine
from typing import Generator
import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise ValueError("DATABASE_URL environment variable not set")

engine = create_engine(DATABASE_URL, echo=True)


def create_db_and_tables():
    """Create all database tables."""
    SQLModel.metadata.create_all(engine)


def get_session() -> Generator[Session, None, None]:
    """Dependency to get database session."""
    with Session(engine) as session:
        yield session
'''

    database_py.write_text(content)
    print(f"✓ Created {database_py}")


def create_todo_router(project_root: Path) -> None:
    """Create example todo router."""
    router_file = project_root / "routers" / "todos.py"

    content = '''"""Todo API endpoints."""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select
from typing import List

from database import get_session
# from models.todo import Todo
# from schemas.todo import TodoCreate, TodoUpdate, TodoResponse

router = APIRouter(prefix="/api/todos", tags=["todos"])


@router.get("/")
async def list_todos(session: Session = Depends(get_session)):
    """List all todos."""
    # statement = select(Todo)
    # return session.exec(statement).all()
    return []


@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_todo(session: Session = Depends(get_session)):
    """Create a new todo."""
    # Implement creation logic
    pass


@router.get("/{todo_id}")
async def get_todo(todo_id: int, session: Session = Depends(get_session)):
    """Get a single todo by ID."""
    # todo = session.get(Todo, todo_id)
    # if not todo:
    #     raise HTTPException(status_code=404, detail="Todo not found")
    # return todo
    raise HTTPException(status_code=404, detail="Todo not found")


@router.put("/{todo_id}")
async def update_todo(todo_id: int, session: Session = Depends(get_session)):
    """Update an existing todo."""
    # Implement update logic
    pass


@router.delete("/{todo_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_todo(todo_id: int, session: Session = Depends(get_session)):
    """Delete a todo."""
    # Implement delete logic
    pass
'''

    router_file.write_text(content)
    print(f"✓ Created {router_file}")


def create_env_files(project_root: Path) -> None:
    """Create environment files."""
    env_example = project_root / ".env.example"
    env_example.write_text("""# Database
DATABASE_URL=postgresql://user:password@localhost:5432/database

# Environment
ENVIRONMENT=development
""")
    print(f"✓ Created {env_example}")

    gitignore = project_root / ".gitignore"
    if not gitignore.exists():
        gitignore.write_text(""".env
.env.local
.env.production
__pycache__/
*.pyc
.venv/
venv/
""")
        print(f"✓ Created {gitignore}")


def create_requirements(project_root: Path) -> None:
    """Create requirements.txt."""
    requirements = project_root / "requirements.txt"

    content = """fastapi==0.109.0
uvicorn[standard]==0.27.0
sqlmodel==0.0.14
psycopg2-binary==2.9.9
python-dotenv==1.0.0
"""

    requirements.write_text(content)
    print(f"✓ Created {requirements}")


def print_next_steps():
    """Print next steps for the user."""
    print("\n" + "=" * 60)
    print("✅ FastAPI project initialized successfully!")
    print("=" * 60)
    print("\nNext steps:")
    print("1. Create virtual environment:")
    print("   python -m venv venv")
    print("   source venv/bin/activate  # Windows: venv\\Scripts\\activate")
    print("\n2. Install dependencies:")
    print("   pip install -r requirements.txt")
    print("\n3. Set up environment:")
    print("   cp .env.example .env")
    print("   # Edit .env with your DATABASE_URL")
    print("\n4. Run the server:")
    print("   uvicorn main:app --reload")
    print("\n5. View API docs:")
    print("   http://localhost:8000/docs")
    print("=" * 60)


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Initialize FastAPI project with best practices"
    )
    parser.add_argument(
        "project_root",
        nargs="?",
        default=".",
        help="Project root directory (default: current directory)"
    )

    args = parser.parse_args()
    project_root = Path(args.project_root).resolve()

    if not project_root.exists():
        project_root.mkdir(parents=True)

    print(f"Initializing FastAPI project in {project_root}\n")

    create_directory_structure(project_root)
    create_main_py(project_root)
    create_database_py(project_root)
    create_todo_router(project_root)
    create_env_files(project_root)
    create_requirements(project_root)

    print_next_steps()


if __name__ == "__main__":
    main()
