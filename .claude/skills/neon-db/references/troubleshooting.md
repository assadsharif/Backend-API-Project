# Troubleshooting Guide

## Connection Issues

### Test Connection with Detailed Error

```python
from sqlalchemy import create_engine, text
from sqlalchemy.exc import OperationalError

try:
    engine = create_engine(DATABASE_URL, echo=True)
    with engine.connect() as conn:
        result = conn.execute(text("SELECT version()"))
        print(f"Connected to: {result.fetchone()[0]}")
except OperationalError as e:
    print(f"Connection failed: {e}")
    print("\nCheck:")
    print("1. DATABASE_URL is correct")
    print("2. Network connectivity to Neon")
    print("3. SSL mode is enabled (?sslmode=require)")
    print("4. Credentials are valid")
```

### Common Connection Errors

| Error | Cause | Solution |
|-------|-------|----------|
| `connection refused` | Wrong host/port | Verify endpoint URL |
| `authentication failed` | Bad credentials | Check username/password |
| `SSL required` | Missing sslmode | Add `?sslmode=require` |
| `database does not exist` | Wrong DB name | Check database name |
| `timeout` | Network issue | Check firewall/VPN |

## SSL Certificate Issues

```python
import urllib.parse

# Parse existing URL
parts = urllib.parse.urlparse(DATABASE_URL)

# Add sslmode parameter
query = urllib.parse.parse_qs(parts.query)
query['sslmode'] = ['require']
new_query = urllib.parse.urlencode(query, doseq=True)

# Reconstruct URL
DATABASE_URL = urllib.parse.urlunparse((
    parts.scheme,
    parts.netloc,
    parts.path,
    parts.params,
    new_query,
    parts.fragment
))
```

## Connection Pool Exhaustion

### Symptoms
- Requests timing out
- "Too many connections" errors
- Slow application response

### Diagnosis

```python
from sqlalchemy import event

connection_count = 0

@event.listens_for(engine, "checkout")
def receive_checkout(dbapi_conn, connection_record, connection_proxy):
    global connection_count
    connection_count += 1
    print(f"Active connections: {connection_count}")

@event.listens_for(engine, "checkin")
def receive_checkin(dbapi_conn, connection_record):
    global connection_count
    connection_count -= 1
    print(f"Active connections: {connection_count}")
```

### Solutions
1. Increase pool_size
2. Reduce connection hold time
3. Use connection pooler (Neon's pgBouncer)
4. Check for connection leaks

## Session Not Closing

### Problem
```python
# BAD: Session leak
session = Session(engine)
result = session.exec(select(Todo)).all()
# Session never closed!
```

### Solution
```python
# GOOD: Context manager
with Session(engine) as session:
    result = session.exec(select(Todo)).all()
# Session automatically closed

# GOOD: FastAPI dependency
def get_session():
    with Session(engine) as session:
        yield session
```

## Query Timeout

### Set Statement Timeout

```python
from sqlalchemy import event

@event.listens_for(engine, "connect")
def set_statement_timeout(dbapi_conn, connection_record):
    cursor = dbapi_conn.cursor()
    cursor.execute("SET statement_timeout = '30s'")
    cursor.close()
```

## Neon Compute Cold Start

Neon suspends idle compute after 5 minutes (free tier).

### Handle Cold Start

```python
import time
from sqlalchemy.exc import OperationalError

def get_connection_with_retry(max_retries=3):
    for attempt in range(max_retries):
        try:
            with Session(engine) as session:
                session.exec(text("SELECT 1"))  # Wake up compute
                return session
        except OperationalError:
            if attempt < max_retries - 1:
                time.sleep(2 ** attempt)  # Exponential backoff
            else:
                raise
```

## Health Check Endpoint

```python
from fastapi import APIRouter, status
from sqlalchemy import text

router = APIRouter()

@router.get("/health/db", status_code=status.HTTP_200_OK)
def database_health_check(session: Session = Depends(get_session)):
    try:
        session.exec(text("SELECT 1"))
        return {"status": "healthy", "database": "connected"}
    except Exception as e:
        return {"status": "unhealthy", "error": str(e)}
```

## Debug Logging

```python
import logging

# Enable SQLAlchemy logging
logging.basicConfig()
logging.getLogger('sqlalchemy.engine').setLevel(logging.INFO)
logging.getLogger('sqlalchemy.pool').setLevel(logging.DEBUG)
```
