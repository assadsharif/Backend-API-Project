---
name: fastapi-backend
description: Expert guidance for FastAPI backend development with RESTful API best practices. Use when building FastAPI applications, creating REST endpoints, implementing CRUD operations, setting up Pydantic models, configuring CORS/middleware, or integrating with databases. Triggers include "FastAPI", "REST API", "backend", "endpoint", "Pydantic", "CORS", "middleware", "async API", or requests to build backend servers with FastAPI.
version: "1.0"
last_verified: "2025-01"
---

# FastAPI Backend

Expert guidance for FastAPI backend development with RESTful API best practices, providing implementation patterns for modern Python backends.

## What This Skill Does

- Project structure and file organization for FastAPI apps
- RESTful endpoint implementation (GET, POST, PUT, DELETE)
- Request/response models with Pydantic validation
- Database integration with SQLModel ORM
- CORS and middleware configuration
- Environment-based settings management
- Error handling and validation patterns

## What This Skill Does NOT Do

- Frontend development or UI components
- Authentication/authorization implementation (use dedicated auth skills)
- Database migrations (use Alembic directly)
- Deployment or CI/CD pipeline setup
- WebSocket or real-time features
- Background task queues (Celery, etc.)
- API versioning strategies

## Quick Start

### Initialize FastAPI Project

```bash
mkdir backend && cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install fastapi uvicorn sqlmodel psycopg2-binary python-dotenv
```

### Basic Project Structure

```
backend/
├── main.py              # FastAPI app entry point
├── database.py          # Database connection
├── models.py            # SQLModel models
├── schemas.py           # Pydantic schemas
├── routers/             # API routes
│   └── todos.py
├── .env                 # Environment variables
└── requirements.txt
```

### Minimal FastAPI App

```python
# main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Todo API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "Todo API"}

@app.get("/health")
async def health():
    return {"status": "healthy"}
```

Run: `uvicorn main:app --reload --host 0.0.0.0 --port 8000`

## Core Patterns

### 1. Request/Response Models with Pydantic

```python
# schemas.py
from pydantic import BaseModel, Field
from datetime import datetime
from typing import Literal

class TodoBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    status: Literal["active", "completed"] = "active"

class TodoCreate(TodoBase):
    pass

class TodoUpdate(BaseModel):
    title: str | None = Field(None, min_length=1, max_length=200)
    status: Literal["active", "completed"] | None = None

class TodoResponse(TodoBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
```

### 2. RESTful CRUD Endpoints

```python
# routers/todos.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select

router = APIRouter(prefix="/api/todos", tags=["todos"])

@router.get("/", response_model=list[TodoResponse])
async def list_todos(session: Session = Depends(get_session)):
    return session.exec(select(Todo)).all()

@router.get("/{todo_id}", response_model=TodoResponse)
async def get_todo(todo_id: int, session: Session = Depends(get_session)):
    todo = session.get(Todo, todo_id)
    if not todo:
        raise HTTPException(status_code=404, detail="Todo not found")
    return todo

@router.post("/", response_model=TodoResponse, status_code=status.HTTP_201_CREATED)
async def create_todo(todo_data: TodoCreate, session: Session = Depends(get_session)):
    todo = Todo(**todo_data.model_dump())
    session.add(todo)
    session.commit()
    session.refresh(todo)
    return todo

@router.put("/{todo_id}", response_model=TodoResponse)
async def update_todo(todo_id: int, todo_data: TodoUpdate, session: Session = Depends(get_session)):
    todo = session.get(Todo, todo_id)
    if not todo:
        raise HTTPException(status_code=404, detail="Todo not found")
    for key, value in todo_data.model_dump(exclude_unset=True).items():
        setattr(todo, key, value)
    session.add(todo)
    session.commit()
    session.refresh(todo)
    return todo

@router.delete("/{todo_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_todo(todo_id: int, session: Session = Depends(get_session)):
    todo = session.get(Todo, todo_id)
    if not todo:
        raise HTTPException(status_code=404, detail="Todo not found")
    session.delete(todo)
    session.commit()
```

### 3. Database Setup

```python
# database.py
from sqlmodel import SQLModel, Session, create_engine
import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise ValueError("DATABASE_URL environment variable not set")

engine = create_engine(DATABASE_URL, echo=True)

def create_db_and_tables():
    SQLModel.metadata.create_all(engine)

def get_session():
    with Session(engine) as session:
        yield session
```

## Output Specification

A properly configured FastAPI backend includes:

- [ ] `main.py` with FastAPI app, CORS, and lifespan handler
- [ ] `database.py` with engine and session dependency
- [ ] `models.py` with SQLModel table definitions
- [ ] `schemas.py` with Pydantic request/response models
- [ ] `routers/` directory with endpoint modules
- [ ] `.env` with DATABASE_URL (not committed)
- [ ] `.env.example` template (committed)
- [ ] OpenAPI docs accessible at `/docs`

## Quality Gate Checklist

Before marking API complete, verify:

- [ ] All endpoints return proper HTTP status codes
- [ ] Validation errors return 422 with details
- [ ] Not found errors return 404
- [ ] CORS configured for frontend origin
- [ ] No hardcoded credentials or secrets
- [ ] DATABASE_URL loaded from environment
- [ ] OpenAPI docs accurate and complete
- [ ] All CRUD operations tested

## HTTP Status Codes

| Code | Use Case |
|------|----------|
| 200 OK | Successful GET, PUT |
| 201 Created | Successful POST |
| 204 No Content | Successful DELETE |
| 404 Not Found | Resource doesn't exist |
| 422 Unprocessable Entity | Validation error |
| 500 Internal Server Error | Server error |

## Official Documentation

| Resource | URL | Use For |
|----------|-----|---------|
| FastAPI Docs | https://fastapi.tiangolo.com/ | Core API, dependencies, middleware |
| Pydantic Docs | https://docs.pydantic.dev/ | Model validation, Field options |
| Uvicorn | https://www.uvicorn.org/ | Server configuration |
| SQLModel | https://sqlmodel.tiangolo.com/ | ORM integration |
| Starlette | https://www.starlette.io/ | Middleware, background tasks |

For patterns not covered here, consult official docs above.

## Keeping Current

- **Last verified:** 2025-01
- **Check for updates:** https://github.com/tiangolo/fastapi/releases
- FastAPI follows semantic versioning
- Pydantic v2 is current; v1 patterns may differ

## Dependencies

```txt
fastapi==0.109.0
uvicorn[standard]==0.27.0
sqlmodel==0.0.14
psycopg2-binary==2.9.9
python-dotenv==1.0.0
```

## Reference Guides

| File | When to Read |
|------|--------------|
| `references/crud-patterns.md` | Filtering, pagination, bulk operations |
| `references/error-handling.md` | Exception handlers, custom errors |
| `references/database-integration.md` | Transactions, migrations |
| `references/anti-patterns.md` | Common mistakes and how to avoid them |
| `references/troubleshooting.md` | Common FastAPI issues and solutions |
| `../INTEGRATION.md` | How all 5 skills work together |

## Scripts

| Script | Purpose |
|--------|---------|
| `scripts/init_fastapi.py` | Initialize FastAPI project with best practices |
| `scripts/run_dev.sh` | Run development server with auto-reload |
