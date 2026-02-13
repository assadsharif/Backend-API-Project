# Error Handling Strategies

## Custom Exception Classes

```python
# exceptions.py
from fastapi import HTTPException, status

class TodoNotFoundError(HTTPException):
    def __init__(self, todo_id: int):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Todo with id {todo_id} not found"
        )

class TodoValidationError(HTTPException):
    def __init__(self, message: str):
        super().__init__(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=message
        )

class DatabaseError(HTTPException):
    def __init__(self, message: str = "Database operation failed"):
        super().__init__(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=message
        )
```

## Global Exception Handlers

```python
# main.py
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
import logging

logger = logging.getLogger(__name__)

app = FastAPI()

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Handle Pydantic validation errors"""
    logger.error(f"Validation error: {exc.errors()}")
    return JSONResponse(
        status_code=422,
        content={
            "detail": "Validation error",
            "errors": exc.errors()
        }
    )

@app.exception_handler(IntegrityError)
async def integrity_exception_handler(request: Request, exc: IntegrityError):
    """Handle database integrity errors"""
    logger.error(f"Database integrity error: {str(exc)}")
    return JSONResponse(
        status_code=409,
        content={"detail": "Database integrity constraint violated"}
    )

@app.exception_handler(SQLAlchemyError)
async def sqlalchemy_exception_handler(request: Request, exc: SQLAlchemyError):
    """Handle general database errors"""
    logger.error(f"Database error: {str(exc)}")
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"}
    )

@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Catch-all for unexpected errors"""
    logger.error(f"Unexpected error: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"}
    )
```

## Consistent Error Response Format

```python
# schemas.py
from pydantic import BaseModel
from typing import Optional, List, Dict, Any

class ErrorDetail(BaseModel):
    loc: List[str]
    msg: str
    type: str

class ErrorResponse(BaseModel):
    detail: str
    errors: Optional[List[ErrorDetail]] = None
    context: Optional[Dict[str, Any]] = None

# Usage in endpoints
from fastapi import HTTPException

@router.get("/{todo_id}")
async def get_todo(todo_id: int, session: Session = Depends(get_session)):
    todo = session.get(Todo, todo_id)
    if not todo:
        raise HTTPException(
            status_code=404,
            detail=f"Todo with id {todo_id} not found"
        )
    return todo
```

## Validation Error with Custom Messages

```python
from pydantic import BaseModel, Field, field_validator

class TodoCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    status: str = Field(default="active")

    @field_validator('title')
    @classmethod
    def title_must_not_be_empty(cls, v: str) -> str:
        if not v or v.isspace():
            raise ValueError('Title cannot be empty or whitespace')
        return v.strip()

    @field_validator('status')
    @classmethod
    def status_must_be_valid(cls, v: str) -> str:
        if v not in ['active', 'completed']:
            raise ValueError('Status must be either "active" or "completed"')
        return v
```

## Try-Except in Endpoints

```python
from sqlalchemy.exc import IntegrityError, SQLAlchemyError

@router.post("/", response_model=TodoResponse, status_code=201)
async def create_todo(
    todo_data: TodoCreate,
    session: Session = Depends(get_session)
):
    """Create a new todo with error handling"""
    try:
        todo = Todo(**todo_data.model_dump())
        session.add(todo)
        session.commit()
        session.refresh(todo)
        return todo
    except IntegrityError as e:
        session.rollback()
        raise HTTPException(
            status_code=409,
            detail="Todo with this data already exists"
        )
    except SQLAlchemyError as e:
        session.rollback()
        logger.error(f"Database error: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Database operation failed"
        )
```

## Context Manager for Database Sessions

```python
# database.py
from contextlib import contextmanager
from sqlmodel import Session

@contextmanager
def get_session_context():
    """Context manager for database sessions with automatic rollback"""
    session = Session(engine)
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()

# Usage in endpoint
@router.post("/", response_model=TodoResponse)
async def create_todo(todo_data: TodoCreate):
    """Create todo with context manager"""
    with get_session_context() as session:
        todo = Todo(**todo_data.model_dump())
        session.add(todo)
        # Commit happens automatically if no exception
    return todo
```

## Logging Strategy

```python
# logging_config.py
import logging
import sys

def setup_logging():
    """Configure logging for the application"""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler("app.log")
        ]
    )

# main.py
from logging_config import setup_logging

setup_logging()
logger = logging.getLogger(__name__)

@router.post("/")
async def create_todo(todo_data: TodoCreate, session: Session = Depends(get_session)):
    logger.info(f"Creating todo: {todo_data.title}")
    try:
        todo = Todo(**todo_data.model_dump())
        session.add(todo)
        session.commit()
        session.refresh(todo)
        logger.info(f"Todo created successfully: {todo.id}")
        return todo
    except Exception as e:
        logger.error(f"Failed to create todo: {str(e)}", exc_info=True)
        raise
```

## Dependency Error Handling

```python
from fastapi import Depends, HTTPException
from typing import Generator

def get_session() -> Generator[Session, None, None]:
    """Database session dependency with error handling"""
    session = Session(engine)
    try:
        yield session
    except SQLAlchemyError as e:
        session.rollback()
        logger.error(f"Session error: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Database session error"
        )
    finally:
        session.close()
```

## Request ID Tracking

```python
# middleware.py
import uuid
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware

class RequestIDMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        request_id = str(uuid.uuid4())
        request.state.request_id = request_id

        response = await call_next(request)
        response.headers["X-Request-ID"] = request_id
        return response

# main.py
app.add_middleware(RequestIDMiddleware)

# Usage in logging
@router.post("/")
async def create_todo(
    request: Request,
    todo_data: TodoCreate,
    session: Session = Depends(get_session)
):
    request_id = getattr(request.state, "request_id", "unknown")
    logger.info(f"[{request_id}] Creating todo: {todo_data.title}")
    # ... rest of the code
```

## HTTP Exception with Extra Context

```python
from typing import Dict, Any

def raise_http_exception(
    status_code: int,
    detail: str,
    context: Dict[str, Any] = None
):
    """Raise HTTP exception with additional context"""
    error_content = {"detail": detail}
    if context:
        error_content["context"] = context

    raise HTTPException(
        status_code=status_code,
        detail=error_content
    )

# Usage
@router.get("/{todo_id}")
async def get_todo(todo_id: int, session: Session = Depends(get_session)):
    todo = session.get(Todo, todo_id)
    if not todo:
        raise_http_exception(
            status_code=404,
            detail="Todo not found",
            context={"todo_id": todo_id, "available_ids": [1, 2, 3]}
        )
    return todo
```
