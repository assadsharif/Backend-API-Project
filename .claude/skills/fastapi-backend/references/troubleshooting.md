# FastAPI Troubleshooting Guide

Common issues and solutions in FastAPI development.

## Server Won't Start

### Symptoms
- `Address already in use`
- `ModuleNotFoundError`

### Solutions

```bash
# Port already in use
lsof -i :8000
kill -9 <PID>

# Or use different port
uvicorn main:app --port 8001

# Module not found
pip install -e .
export PYTHONPATH="${PYTHONPATH}:${PWD}"

# Wrong app path
uvicorn main:app  # File is main.py, app is FastAPI instance
uvicorn src.main:app  # If in src directory
```

## 422 Validation Error

### Symptoms
- `{"detail":[{"loc":["body","field"],"msg":"..."}]}`

### Solutions

```python
# Check request body matches schema
class UserCreate(BaseModel):
    email: str  # Required!
    name: str   # Required!

# Send correct JSON
{
    "email": "user@example.com",
    "name": "John"
}

# Check field types
class Item(BaseModel):
    price: float  # Send number, not string "10.5"
    quantity: int

# Debug validation
@app.post("/users")
async def create_user(user: UserCreate):
    print(user.model_dump())  # See parsed data
```

## CORS Errors

### Symptoms
- `Access-Control-Allow-Origin` error in browser
- Preflight request fails

### Solutions

```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# For development, allow all (not for production!)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)
```

## Database Connection Failed

### Symptoms
- `OperationalError`
- `Connection refused`

### Solutions

```python
# Check DATABASE_URL
import os
print(os.getenv("DATABASE_URL"))

# Verify connection
from sqlalchemy import create_engine, text
engine = create_engine(DATABASE_URL, echo=True)
with engine.connect() as conn:
    conn.execute(text("SELECT 1"))

# Check .env is loaded
from dotenv import load_dotenv
load_dotenv()  # Must call before getenv!
```

## 500 Internal Server Error

### Symptoms
- Generic error with no details

### Solutions

```python
# Enable debug mode (development only!)
uvicorn main:app --reload

# Add logging
import logging
logging.basicConfig(level=logging.DEBUG)

# Add exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    import traceback
    traceback.print_exc()
    return JSONResponse(
        status_code=500,
        content={"detail": str(exc)}
    )
```

## Dependency Injection Issues

### Symptoms
- `TypeError: get_session() missing argument`
- Dependency not injected

### Solutions

```python
# Use Depends(), not direct call
# WRONG
@app.get("/users")
async def get_users(session = get_session()):  # Called immediately!
    ...

# CORRECT
@app.get("/users")
async def get_users(session: Session = Depends(get_session)):
    ...

# For class dependencies
class UserService:
    def __init__(self, session: Session = Depends(get_session)):
        self.session = session
```

## Async Issues

### Symptoms
- `RuntimeWarning: coroutine was never awaited`
- Blocking behavior

### Solutions

```python
# Await async functions
# WRONG
result = async_function()  # Returns coroutine, not result!

# CORRECT
result = await async_function()

# Don't use async for sync code
# WRONG (blocking)
@app.get("/data")
async def get_data():
    data = sync_database_call()  # Blocks event loop!

# CORRECT (sync endpoint for sync code)
@app.get("/data")
def get_data():
    data = sync_database_call()
```

## Response Model Mismatch

### Symptoms
- `ResponseValidationError`
- Fields missing in response

### Solutions

```python
# Ensure model matches response
class UserResponse(BaseModel):
    id: int
    email: str

    class Config:
        from_attributes = True  # For ORM objects

# Check all required fields are present
@app.get("/user", response_model=UserResponse)
async def get_user():
    return {"id": 1, "email": "test@test.com"}  # Must have both!
```

## Path Parameter Issues

### Symptoms
- `404 Not Found` for valid paths
- Wrong parameter value

### Solutions

```python
# Order matters - specific routes first!
# WRONG order
@app.get("/users/{user_id}")
@app.get("/users/me")  # Never reached!

# CORRECT order
@app.get("/users/me")  # Specific first
@app.get("/users/{user_id}")

# Type conversion
@app.get("/items/{item_id}")
async def get_item(item_id: int):  # Auto-converts string to int
    ...
```

## Quick Debugging

```bash
# Check OpenAPI docs
open http://localhost:8000/docs

# Test with curl
curl -X POST http://localhost:8000/users \
  -H "Content-Type: application/json" \
  -d '{"email":"test@test.com"}'

# Enable SQL logging
engine = create_engine(DATABASE_URL, echo=True)

# Check request details
@app.middleware("http")
async def log_requests(request, call_next):
    print(f"{request.method} {request.url}")
    response = await call_next(request)
    print(f"Status: {response.status_code}")
    return response
```
