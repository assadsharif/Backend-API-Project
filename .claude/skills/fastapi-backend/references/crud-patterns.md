# Advanced CRUD Patterns

## Filtering and Query Parameters

### Multiple Filter Parameters

```python
from typing import Optional
from fastapi import Query

@router.get("/", response_model=List[TodoResponse])
async def list_todos(
    status: Optional[str] = Query(None, regex="^(active|completed)$"),
    title: Optional[str] = Query(None, min_length=1),
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0),
    session: Session = Depends(get_session)
):
    """List todos with filtering and pagination"""
    query = select(Todo)

    if status:
        query = query.where(Todo.status == status)

    if title:
        query = query.where(Todo.title.contains(title))

    query = query.offset(offset).limit(limit)
    todos = session.exec(query).all()

    return todos
```

### Pagination with Total Count

```python
from pydantic import BaseModel

class PaginatedResponse(BaseModel):
    items: List[TodoResponse]
    total: int
    page: int
    page_size: int
    pages: int

@router.get("/paginated", response_model=PaginatedResponse)
async def list_todos_paginated(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    session: Session = Depends(get_session)
):
    """List todos with pagination metadata"""
    # Get total count
    count_query = select(func.count()).select_from(Todo)
    total = session.exec(count_query).one()

    # Get paginated results
    query = select(Todo).offset((page - 1) * page_size).limit(page_size)
    todos = session.exec(query).all()

    return PaginatedResponse(
        items=todos,
        total=total,
        page=page,
        page_size=page_size,
        pages=(total + page_size - 1) // page_size
    )
```

### Sorting

```python
from sqlmodel import asc, desc

@router.get("/", response_model=List[TodoResponse])
async def list_todos(
    sort_by: str = Query("created_at", regex="^(id|title|status|created_at|updated_at)$"),
    sort_order: str = Query("asc", regex="^(asc|desc)$"),
    session: Session = Depends(get_session)
):
    """List todos with sorting"""
    query = select(Todo)

    # Apply sorting
    column = getattr(Todo, sort_by)
    if sort_order == "desc":
        query = query.order_by(desc(column))
    else:
        query = query.order_by(asc(column))

    todos = session.exec(query).all()
    return todos
```

## Bulk Operations

### Bulk Create

```python
@router.post("/bulk", response_model=List[TodoResponse], status_code=status.HTTP_201_CREATED)
async def bulk_create_todos(
    todos_data: List[TodoCreate],
    session: Session = Depends(get_session)
):
    """Create multiple todos at once"""
    if len(todos_data) > 100:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot create more than 100 todos at once"
        )

    todos = [Todo(**todo.model_dump()) for todo in todos_data]
    session.add_all(todos)
    session.commit()

    for todo in todos:
        session.refresh(todo)

    return todos
```

### Bulk Update

```python
@router.patch("/bulk", response_model=dict)
async def bulk_update_todos(
    todo_ids: List[int],
    update_data: TodoUpdate,
    session: Session = Depends(get_session)
):
    """Update multiple todos at once"""
    if len(todo_ids) > 100:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot update more than 100 todos at once"
        )

    query = select(Todo).where(Todo.id.in_(todo_ids))
    todos = session.exec(query).all()

    if not todos:
        raise HTTPException(status_code=404, detail="No todos found")

    update_dict = update_data.model_dump(exclude_unset=True)
    for todo in todos:
        for key, value in update_dict.items():
            setattr(todo, key, value)

    session.add_all(todos)
    session.commit()

    return {"updated": len(todos)}
```

### Bulk Delete

```python
@router.delete("/bulk", status_code=status.HTTP_204_NO_CONTENT)
async def bulk_delete_todos(
    todo_ids: List[int],
    session: Session = Depends(get_session)
):
    """Delete multiple todos at once"""
    if len(todo_ids) > 100:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete more than 100 todos at once"
        )

    query = select(Todo).where(Todo.id.in_(todo_ids))
    todos = session.exec(query).all()

    if not todos:
        raise HTTPException(status_code=404, detail="No todos found")

    for todo in todos:
        session.delete(todo)

    session.commit()
```

## Partial Updates (PATCH)

```python
@router.patch("/{todo_id}", response_model=TodoResponse)
async def partial_update_todo(
    todo_id: int,
    todo_data: TodoUpdate,
    session: Session = Depends(get_session)
):
    """Partially update a todo (only provided fields)"""
    todo = session.get(Todo, todo_id)
    if not todo:
        raise HTTPException(status_code=404, detail="Todo not found")

    # Update only provided fields
    update_data = todo_data.model_dump(exclude_unset=True)

    if not update_data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No fields to update"
        )

    for key, value in update_data.items():
        setattr(todo, key, value)

    # Update timestamp
    todo.updated_at = datetime.utcnow()

    session.add(todo)
    session.commit()
    session.refresh(todo)

    return todo
```

## Upsert Pattern

```python
@router.put("/upsert/{todo_id}", response_model=TodoResponse)
async def upsert_todo(
    todo_id: int,
    todo_data: TodoCreate,
    session: Session = Depends(get_session)
):
    """Create or update a todo (upsert pattern)"""
    todo = session.get(Todo, todo_id)

    if todo:
        # Update existing
        for key, value in todo_data.model_dump().items():
            setattr(todo, key, value)
        todo.updated_at = datetime.utcnow()
    else:
        # Create new
        todo = Todo(id=todo_id, **todo_data.model_dump())

    session.add(todo)
    session.commit()
    session.refresh(todo)

    return todo
```

## Search with Full-Text

```python
@router.get("/search", response_model=List[TodoResponse])
async def search_todos(
    q: str = Query(..., min_length=1),
    session: Session = Depends(get_session)
):
    """Search todos by title (case-insensitive)"""
    query = select(Todo).where(Todo.title.ilike(f"%{q}%"))
    todos = session.exec(query).all()
    return todos
```

## Soft Delete Pattern

```python
# models.py
class Todo(SQLModel, table=True):
    __tablename__ = "todos"

    id: int | None = Field(default=None, primary_key=True)
    title: str = Field(max_length=200)
    status: str = Field(default="active")
    deleted_at: datetime | None = Field(default=None)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

# routers/todos.py
@router.delete("/{todo_id}", status_code=status.HTTP_204_NO_CONTENT)
async def soft_delete_todo(
    todo_id: int,
    session: Session = Depends(get_session)
):
    """Soft delete a todo"""
    todo = session.get(Todo, todo_id)
    if not todo or todo.deleted_at:
        raise HTTPException(status_code=404, detail="Todo not found")

    todo.deleted_at = datetime.utcnow()
    session.add(todo)
    session.commit()

@router.get("/", response_model=List[TodoResponse])
async def list_todos(
    include_deleted: bool = False,
    session: Session = Depends(get_session)
):
    """List todos (excluding soft-deleted by default)"""
    query = select(Todo)

    if not include_deleted:
        query = query.where(Todo.deleted_at == None)

    todos = session.exec(query).all()
    return todos
```

## Related Resources

```python
# Get todo with related data count
@router.get("/{todo_id}/summary", response_model=dict)
async def get_todo_summary(
    todo_id: int,
    session: Session = Depends(get_session)
):
    """Get todo with summary statistics"""
    todo = session.get(Todo, todo_id)
    if not todo:
        raise HTTPException(status_code=404, detail="Todo not found")

    return {
        "todo": todo,
        "created_days_ago": (datetime.utcnow() - todo.created_at).days,
        "last_updated": todo.updated_at
    }
```
