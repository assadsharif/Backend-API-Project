# FastAPI Anti-Patterns Guide

Common mistakes and how to avoid them in FastAPI development.

## 1. Blocking the Event Loop

**Problem:** Running synchronous/blocking code in async endpoints.

```python
# BAD: Blocking call in async function
@router.get("/users")
async def get_users():
    users = db.query(User).all()  # Blocks event loop!
    return users

# GOOD: Use sync function or run in thread
@router.get("/users")
def get_users():  # Note: no async
    users = db.query(User).all()
    return users

# GOOD: Or use async database driver
@router.get("/users")
async def get_users():
    users = await async_db.fetch_all(query)
    return users
```

## 2. Missing Dependency Cleanup

**Problem:** Not closing resources in dependencies.

```python
# BAD: Session leak
def get_session():
    session = Session(engine)
    return session  # Never closed!

# GOOD: Use yield for cleanup
def get_session():
    session = Session(engine)
    try:
        yield session
    finally:
        session.close()

# GOOD: Context manager (preferred)
def get_session():
    with Session(engine) as session:
        yield session
```

## 3. Hardcoding Configuration

**Problem:** Hardcoding secrets and configuration.

```python
# BAD: Hardcoded credentials
DATABASE_URL = "postgresql://user:password@localhost/db"
SECRET_KEY = "super-secret-key"

# GOOD: Environment variables
DATABASE_URL = os.getenv("DATABASE_URL")
SECRET_KEY = os.getenv("SECRET_KEY")

# GOOD: Pydantic settings
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    database_url: str
    secret_key: str

    class Config:
        env_file = ".env"

settings = Settings()
```

## 4. Incorrect Status Codes

**Problem:** Using wrong HTTP status codes.

```python
# BAD: 200 for creation
@router.post("/users")
async def create_user(user: UserCreate):
    return {"id": 1, "message": "Created"}  # Returns 200

# GOOD: 201 for creation
@router.post("/users", status_code=status.HTTP_201_CREATED)
async def create_user(user: UserCreate):
    return user

# BAD: Returning data on delete
@router.delete("/users/{id}")
async def delete_user(id: int):
    return {"deleted": True}  # Unnecessary

# GOOD: 204 No Content
@router.delete("/users/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(id: int):
    pass  # No return needed
```

## 5. Not Handling Exceptions

**Problem:** Letting exceptions bubble up unhandled.

```python
# BAD: Unhandled exception
@router.post("/users")
async def create_user(user: UserCreate, session: Session = Depends(get_session)):
    db_user = User(**user.model_dump())
    session.add(db_user)
    session.commit()  # IntegrityError if duplicate!
    return db_user

# GOOD: Handle specific exceptions
@router.post("/users")
async def create_user(user: UserCreate, session: Session = Depends(get_session)):
    try:
        db_user = User(**user.model_dump())
        session.add(db_user)
        session.commit()
        session.refresh(db_user)
        return db_user
    except IntegrityError:
        session.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="User already exists"
        )
```

## 6. N+1 Query Problem

**Problem:** Making separate queries for related data.

```python
# BAD: N+1 queries
@router.get("/users")
async def get_users(session: Session = Depends(get_session)):
    users = session.exec(select(User)).all()
    for user in users:
        _ = user.posts  # Separate query per user!
    return users

# GOOD: Eager loading
from sqlalchemy.orm import selectinload

@router.get("/users")
async def get_users(session: Session = Depends(get_session)):
    statement = select(User).options(selectinload(User.posts))
    users = session.exec(statement).all()
    return users
```

## 7. Missing Validation

**Problem:** Not validating input properly.

```python
# BAD: No validation
class UserCreate(BaseModel):
    email: str
    age: int

# GOOD: Proper validation
from pydantic import EmailStr, Field

class UserCreate(BaseModel):
    email: EmailStr
    age: int = Field(ge=0, le=150)
    name: str = Field(min_length=1, max_length=100)
```

## 8. Circular Imports

**Problem:** Importing between modules incorrectly.

```python
# BAD: Circular import
# models.py
from schemas import UserSchema  # Imports schemas

# schemas.py
from models import User  # Imports models -> circular!

# GOOD: Use TYPE_CHECKING
# models.py
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from schemas import UserSchema

# GOOD: Or use forward references
class User(SQLModel):
    def to_schema(self) -> "UserSchema":
        ...
```

## 9. Not Using Response Models

**Problem:** Returning raw database objects.

```python
# BAD: Exposes all fields including password
@router.get("/users/{id}")
async def get_user(id: int, session: Session = Depends(get_session)):
    return session.get(User, id)  # Includes password_hash!

# GOOD: Use response model to filter fields
class UserResponse(BaseModel):
    id: int
    email: str
    name: str

@router.get("/users/{id}", response_model=UserResponse)
async def get_user(id: int, session: Session = Depends(get_session)):
    return session.get(User, id)  # Only specified fields returned
```

## 10. Ignoring CORS

**Problem:** Not configuring CORS for frontend access.

```python
# BAD: Frontend can't access API
app = FastAPI()

# GOOD: Configure CORS
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

## Quick Checklist

Before deploying, verify:

- [ ] No hardcoded secrets
- [ ] All exceptions handled
- [ ] Correct HTTP status codes
- [ ] Response models hide sensitive data
- [ ] CORS configured
- [ ] Dependencies clean up resources
- [ ] No blocking calls in async functions
- [ ] Input validated with Pydantic
