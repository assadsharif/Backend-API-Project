# Connection Pooling Guide

## Connection Pooling Configuration

### SQLAlchemy Engine with Pooling

```python
from sqlmodel import create_engine

DATABASE_URL = os.getenv("DATABASE_URL")

engine = create_engine(
    DATABASE_URL,
    echo=True,
    pool_size=5,              # Connections to maintain
    max_overflow=10,          # Additional connections when busy
    pool_timeout=30,          # Wait time for connection
    pool_recycle=3600,        # Recycle connections after 1 hour
    pool_pre_ping=True        # Verify connection before use
)
```

### Pool Size Recommendations

| Environment | pool_size | max_overflow |
|-------------|-----------|--------------|
| Development | 2 | 5 |
| Staging | 5 | 10 |
| Production | 10 | 20 |

### Connection String with Pooling

```python
# Standard connection string
DATABASE_URL = "postgresql://user:pass@host:5432/dbname?sslmode=require"

# With connection parameters
DATABASE_URL = "postgresql://user:pass@host:5432/dbname?sslmode=require&connect_timeout=10&pool_timeout=10"
```

## Monitoring Connection Pool

```python
from sqlalchemy import event

@event.listens_for(engine, "connect")
def receive_connect(dbapi_conn, connection_record):
    print(f"New connection: {id(dbapi_conn)}")

@event.listens_for(engine, "checkout")
def receive_checkout(dbapi_conn, connection_record, connection_proxy):
    print(f"Connection checked out from pool: {id(dbapi_conn)}")

@event.listens_for(engine, "checkin")
def receive_checkin(dbapi_conn, connection_record):
    print(f"Connection returned to pool: {id(dbapi_conn)}")
```

## Handling Pool Exhaustion

```python
from sqlalchemy.exc import TimeoutError

try:
    with Session(engine) as session:
        # Database operations
        pass
except TimeoutError:
    print("Connection pool exhausted - all connections in use")
    # Implement retry logic or queue request
```

## Neon-Specific Pooling

Neon provides built-in connection pooling via pgBouncer:

1. Use the pooled connection string from Neon Console
2. Format: `postgresql://user:pass@ep-XXX-pooler.region.aws.neon.tech/dbname`
3. Note the `-pooler` suffix in the hostname

### When to Use Neon's Pooler

- Serverless deployments (many short connections)
- High concurrency applications
- Lambda/Cloud Functions
