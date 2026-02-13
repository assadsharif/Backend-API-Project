---
name: neon-db
description: Expert guidance for Neon serverless PostgreSQL database setup and configuration. Use when setting up Neon database, configuring database connections, managing connection strings, integrating with SQLModel/FastAPI, or setting up development/production databases. Triggers include "Neon", "Neon database", "Neon PostgreSQL", "serverless Postgres", "DATABASE_URL", "Neon project", or requests to set up PostgreSQL databases with Neon.
version: "1.0"
last_verified: "2025-01"
---

# Neon DB

Expert guidance for Neon - a serverless PostgreSQL database platform with automatic scaling, branching, and built-in connection pooling.

## What This Skill Does

- Neon project setup and configuration
- DATABASE_URL connection string management
- SQLModel/FastAPI database integration
- Environment-based configuration
- Database branching for dev/staging/prod
- Connection verification and health checks

## What This Skill Does NOT Do

- Database schema design (use sqlmodel-orm skill)
- ORM model definitions (use sqlmodel-orm skill)
- Query optimization
- Database administration or DBA tasks
- Backup/restore automation
- Multi-region deployment
- Database monitoring/alerting setup

## Quick Start

### 1. Create Neon Account

1. Visit https://neon.tech
2. Sign up with GitHub, Google, or email
3. Create a new project

### 2. Get Connection String

From Neon Console:
1. Select your project
2. Go to "Connection Details"
3. Copy the connection string

**Format:**
```
postgresql://username:password@ep-xxxxx.region.aws.neon.tech/neondb?sslmode=require
```

### 3. Configure Environment

```bash
# .env (do not commit)
DATABASE_URL=postgresql://username:password@hostname/database?sslmode=require

# .env.example (commit this)
DATABASE_URL=postgresql://user:password@host/database?sslmode=require
```

### 4. Connect with SQLModel

```python
# database.py
from sqlmodel import SQLModel, create_engine, Session
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

## Core Patterns

### FastAPI Integration

```python
# main.py
from fastapi import FastAPI
from contextlib import asynccontextmanager
from database import create_db_and_tables

@asynccontextmanager
async def lifespan(app: FastAPI):
    create_db_and_tables()
    yield

app = FastAPI(lifespan=lifespan)
```

### Verify Connection

```python
from sqlalchemy import text

def check_connection():
    try:
        with Session(engine) as session:
            session.exec(text("SELECT 1"))
            print("Database connection successful")
            return True
    except Exception as e:
        print(f"Database connection failed: {e}")
        return False
```

### Multiple Environments

```bash
# .env.development
DATABASE_URL=postgresql://dev_user:pass@ep-dev-branch.neon.tech/dev_db?sslmode=require

# .env.production
DATABASE_URL=postgresql://prod_user:pass@ep-main-branch.neon.tech/prod_db?sslmode=require
```

```python
import os
from dotenv import load_dotenv

env = os.getenv("ENVIRONMENT", "development")
load_dotenv(f".env.{env}")
```

## Output Specification

A properly configured Neon database setup includes:

- [ ] Neon project created with database
- [ ] DATABASE_URL stored in `.env` (not committed)
- [ ] `.env.example` template committed
- [ ] `.env` added to `.gitignore`
- [ ] `database.py` with engine and get_session
- [ ] Connection verification on startup
- [ ] SSL mode enabled (`?sslmode=require`)

## Quality Gate Checklist

Before marking database setup complete, verify:

- [ ] DATABASE_URL loads from environment (not hardcoded)
- [ ] Connection string includes `?sslmode=require`
- [ ] `.env` is in `.gitignore`
- [ ] Connection test passes (`SELECT 1`)
- [ ] Tables create successfully on startup
- [ ] FastAPI lifespan creates tables
- [ ] Separate dev/prod connection strings

## Security Best Practices

```python
# GOOD: Use environment variables
DATABASE_URL = os.getenv("DATABASE_URL")

# BAD: Hardcode credentials
DATABASE_URL = "postgresql://user:password@host/db"

# GOOD: Add to .gitignore
# .gitignore
.env
.env.local
.env.production

# GOOD: Commit template only
# .env.example
DATABASE_URL=postgresql://user:password@hostname/database?sslmode=require
```

## Local Development Options

### Option 1: Neon Development Branch

Use a separate Neon branch for development:
```bash
DATABASE_URL=postgresql://user:pass@ep-dev-branch.neon.tech/neondb?sslmode=require
```

### Option 2: Local PostgreSQL with Docker

```yaml
# docker-compose.yml
version: '3.8'
services:
  postgres:
    image: postgres:15
    environment:
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: postgres
      POSTGRES_DB: todos_dev
    ports:
      - "5432:5432"
```

```bash
# .env.local
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/todos_dev
```

## Official Documentation

| Resource | URL | Use For |
|----------|-----|---------|
| Neon Docs | https://neon.tech/docs | Getting started, concepts |
| Connection Guide | https://neon.tech/docs/connect/connect-from-any-app | Connection strings |
| Branching | https://neon.tech/docs/guides/branching | Dev/staging/prod setup |
| FastAPI Integration | https://neon.tech/docs/guides/fastapi | FastAPI patterns |
| SQLAlchemy/SQLModel | https://neon.tech/docs/guides/sqlalchemy | ORM setup |

For patterns not covered here, consult official docs above.

## Keeping Current

- **Last verified:** 2025-01
- **Check for updates:** https://neon.tech/blog
- Neon adds features frequently; check for new capabilities
- Free tier limits may change; verify current quotas

## Neon-Specific Features

### Autoscaling
Neon automatically scales compute resources. No configuration needed.

### Point-in-Time Restore
7 days of history maintained. Restore via Console:
1. Go to Branches → Select branch
2. Click "Restore" → Choose timestamp

### Compute Endpoints
Each branch has its own endpoint:
```
main:   ep-main-123456.us-east-2.aws.neon.tech
dev:    ep-dev-789012.us-east-2.aws.neon.tech
```

## Reference Guides

| File | When to Read |
|------|--------------|
| `references/connection-pooling.md` | Pool configuration, monitoring |
| `references/troubleshooting.md` | Connection errors, debugging |
| `references/branching.md` | Dev/staging/prod branch strategy |
| `references/anti-patterns.md` | Common mistakes and how to avoid them |
| `../INTEGRATION.md` | How all 5 skills work together |

## Scripts

| Script | Purpose |
|--------|---------|
| `scripts/check_connection.py` | Verify database connection and diagnose issues |
