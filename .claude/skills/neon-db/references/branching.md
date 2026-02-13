# Database Branching Guide

## What is Branching?

Neon supports Git-like database branches:
- Create isolated copies of your database
- Test schema changes without affecting production
- Develop features with real data
- Preview deployments with separate databases

## Creating Branches

### Via Neon Console

1. Go to Neon Console → Branches
2. Click "Create Branch"
3. Name it (e.g., `development`, `staging`, `feature-auth`)
4. Select parent branch (usually `main`)
5. Copy the new connection string

### Branch Connection Strings

```bash
# Main branch (production)
DATABASE_URL=postgresql://user:pass@ep-main-123456.us-east-2.aws.neon.tech/neondb?sslmode=require

# Development branch
DATABASE_URL=postgresql://user:pass@ep-dev-789012.us-east-2.aws.neon.tech/neondb?sslmode=require

# Feature branch
DATABASE_URL=postgresql://user:pass@ep-feature-auth-345678.us-east-2.aws.neon.tech/neondb?sslmode=require
```

## Branch Strategy

### Recommended Structure

```
main (production)
├── staging
│   └── feature-auth
│   └── feature-todos
└── development
```

### Environment Configuration

```python
# config.py
import os

ENVIRONMENT = os.getenv("ENVIRONMENT", "development")

# Map environments to branches
BRANCH_MAP = {
    "production": "ep-main-123456",
    "staging": "ep-staging-789012",
    "development": "ep-dev-345678",
}

def get_database_url():
    branch = BRANCH_MAP.get(ENVIRONMENT, BRANCH_MAP["development"])
    return f"postgresql://user:pass@{branch}.us-east-2.aws.neon.tech/neondb?sslmode=require"
```

### Environment Files

```bash
# .env.production
ENVIRONMENT=production
DATABASE_URL=postgresql://user:pass@ep-main-123456.us-east-2.aws.neon.tech/neondb?sslmode=require

# .env.staging
ENVIRONMENT=staging
DATABASE_URL=postgresql://user:pass@ep-staging-789012.us-east-2.aws.neon.tech/neondb?sslmode=require

# .env.development
ENVIRONMENT=development
DATABASE_URL=postgresql://user:pass@ep-dev-345678.us-east-2.aws.neon.tech/neondb?sslmode=require
```

## Testing Migrations

### Workflow

1. Create feature branch from staging
2. Run migration on feature branch
3. Test thoroughly
4. Merge to staging branch
5. Test in staging
6. Apply to production

### Migration Safety

```python
# Always backup before migration
# Neon provides point-in-time restore

def run_migration_safely():
    print("Creating branch snapshot...")
    # Neon automatically maintains history

    print("Running migration...")
    alembic.command.upgrade(alembic_cfg, "head")

    print("Testing migration...")
    # Run tests

    print("Migration complete")
```

## Branch Lifecycle

### Delete Unused Branches

- Feature branches: Delete after merge
- Staging: Keep persistent
- Development: Keep persistent

### Cost Considerations

- Each branch has separate compute
- Free tier: Limited branches
- Pro tier: Unlimited branches
- Idle branches suspend automatically

## CI/CD Integration

### GitHub Actions Example

```yaml
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - name: Create test branch
        run: |
          # Use Neon CLI or API to create branch
          neon branches create --name test-${{ github.sha }}

      - name: Run tests
        env:
          DATABASE_URL: ${{ secrets.TEST_DATABASE_URL }}
        run: pytest

      - name: Cleanup branch
        if: always()
        run: |
          neon branches delete test-${{ github.sha }}
```

## Branch Best Practices

1. **Name branches descriptively**: `feature-user-auth`, `bugfix-todo-delete`
2. **Set branch expiration**: Auto-delete after PR merge
3. **Use production data carefully**: Anonymize sensitive data
4. **Monitor branch usage**: Delete unused branches
5. **Document branch purposes**: Track in project docs
