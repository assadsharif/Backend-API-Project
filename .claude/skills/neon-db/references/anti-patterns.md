# Neon Database Anti-Patterns Guide

Common mistakes and how to avoid them when using Neon PostgreSQL.

## 1. Hardcoding Connection Strings

**Problem:** Credentials in code.

```python
# BAD: Hardcoded credentials
DATABASE_URL = "postgresql://user:password123@ep-cool-darkness.neon.tech/mydb"

# GOOD: Environment variables
import os
DATABASE_URL = os.getenv("DATABASE_URL")

# GOOD: Pydantic settings
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    database_url: str

    class Config:
        env_file = ".env"
```

## 2. Missing SSL Mode

**Problem:** Connection fails without SSL.

```python
# BAD: No sslmode (will fail with Neon)
DATABASE_URL = "postgresql://user:pass@host/db"

# GOOD: Always include sslmode=require
DATABASE_URL = "postgresql://user:pass@host/db?sslmode=require"
```

## 3. Committing .env Files

**Problem:** Secrets pushed to git.

```bash
# BAD: .env committed
git add .env
git commit -m "Add config"  # Secrets exposed!

# GOOD: Add to .gitignore
# .gitignore
.env
.env.local
.env.production
.env.*.local

# GOOD: Commit only example
# .env.example
DATABASE_URL=postgresql://user:password@host/database?sslmode=require
```

## 4. Not Handling Cold Starts

**Problem:** First request fails after idle period.

```python
# BAD: No retry on cold start
def get_data():
    with Session(engine) as session:
        return session.exec(select(Todo)).all()  # May timeout!

# GOOD: Retry logic for cold starts
import time
from sqlalchemy.exc import OperationalError

def get_data(max_retries=3):
    for attempt in range(max_retries):
        try:
            with Session(engine) as session:
                return session.exec(select(Todo)).all()
        except OperationalError:
            if attempt < max_retries - 1:
                time.sleep(2 ** attempt)  # Exponential backoff
            else:
                raise
```

## 5. Connection Pool Exhaustion

**Problem:** Too many connections.

```python
# BAD: Default pool may be too large for Neon free tier
engine = create_engine(DATABASE_URL)

# GOOD: Configure pool for Neon
engine = create_engine(
    DATABASE_URL,
    pool_size=5,        # Reasonable for free tier
    max_overflow=10,
    pool_timeout=30,
    pool_recycle=3600,
    pool_pre_ping=True  # Verify connection before use
)
```

## 6. Session Leaks

**Problem:** Sessions not closed properly.

```python
# BAD: Session never closed
session = Session(engine)
users = session.exec(select(User)).all()
# Session stays open forever!

# GOOD: Context manager
with Session(engine) as session:
    users = session.exec(select(User)).all()
# Automatically closed

# GOOD: FastAPI dependency
def get_session():
    with Session(engine) as session:
        yield session
```

## 7. Using Same Branch for Dev and Prod

**Problem:** Development affects production data.

```bash
# BAD: Same database for everything
DATABASE_URL=postgresql://...@ep-main.neon.tech/db

# GOOD: Separate branches
# .env.development
DATABASE_URL=postgresql://...@ep-dev-branch.neon.tech/db

# .env.production
DATABASE_URL=postgresql://...@ep-main.neon.tech/db
```

## 8. Not Testing Connection on Startup

**Problem:** App starts but can't reach database.

```python
# BAD: No connection verification
app = FastAPI()

# GOOD: Verify connection on startup
from contextlib import asynccontextmanager
from sqlalchemy import text

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Verify connection
    try:
        with Session(engine) as session:
            session.exec(text("SELECT 1"))
        print("✓ Database connection verified")
    except Exception as e:
        print(f"✗ Database connection failed: {e}")
        raise

    yield

app = FastAPI(lifespan=lifespan)
```

## 9. Ignoring Connection Timeouts

**Problem:** Hanging requests on network issues.

```python
# BAD: No timeout configuration
engine = create_engine(DATABASE_URL)

# GOOD: Set connect timeout
DATABASE_URL = "postgresql://...?sslmode=require&connect_timeout=10"

# Or in engine
engine = create_engine(
    DATABASE_URL,
    connect_args={"connect_timeout": 10}
)
```

## 10. Not Using Connection Pooler

**Problem:** Too many direct connections in serverless.

```bash
# BAD: Direct connection in serverless (Lambda, Vercel)
DATABASE_URL=postgresql://user:pass@ep-xxx.neon.tech/db

# GOOD: Use Neon's pooler endpoint
DATABASE_URL=postgresql://user:pass@ep-xxx-pooler.neon.tech/db
#                                         ^^^^^^^ Note: -pooler suffix
```

## 11. Storing Large Blobs

**Problem:** Storing files in database.

```python
# BAD: Large files in database
class Document(SQLModel, table=True):
    id: int
    content: bytes  # 10MB PDF stored here!

# GOOD: Store file reference only
class Document(SQLModel, table=True):
    id: int
    file_url: str  # Store in S3/Cloudflare R2
    file_size: int
```

## 12. No Backup Strategy

**Problem:** Relying only on Neon's backups.

```python
# Neon provides:
# - 7 days point-in-time recovery (free tier)
# - 30 days (paid tiers)

# GOOD: Also export critical data periodically
# Use pg_dump for additional backups
# Document recovery procedures
```

## Quick Checklist

Before deploying, verify:

- [ ] DATABASE_URL from environment
- [ ] `?sslmode=require` in connection string
- [ ] `.env` in `.gitignore`
- [ ] Separate dev and prod branches
- [ ] Connection pool configured
- [ ] Connection verified on startup
- [ ] Retry logic for cold starts
- [ ] Timeout settings configured
- [ ] Using pooler for serverless
