# Implementation Plan: Alerts & Notifications

**Branch**: `004-alerts-notifications` | **Date**: 2026-02-15 | **Spec**: [spec.md](spec.md)
**Input**: Feature specification from `/specs/004-alerts-notifications/spec.md`

## Summary

Add an alerts system to the Stock Signal API that allows authenticated users to create, manage, and check custom alert rules. Three alert types are supported: price threshold (stock price crosses above/below target), signal change (stock signal matches a target like BUY), and portfolio value change (portfolio value changes by a percentage). Alerts are stored per-user in a JSON file, evaluated on-demand when users request triggered alerts, and managed via REST endpoints. The implementation follows existing patterns established in features 001-003.

## Technical Context

**Language/Version**: Python 3.11+ (matches existing project)
**Primary Dependencies**: FastAPI 0.100+, Pydantic 2.0+, yfinance 0.2.40+, cachetools 5.3+
**Storage**: JSON file (`data/alerts.json`) with thread-safe atomic writes (same pattern as `portfolios.json` and `users.json`)
**Testing**: pytest with httpx (AsyncClient) — same as existing test suite
**Target Platform**: Linux server (same as existing deployment)
**Project Type**: Single project — extending existing FastAPI application
**Performance Goals**: Alert creation < 2s, triggered alert check < 5s for 10 alerts (per SC-001, SC-002)
**Constraints**: Maximum 10 active alerts per user; on-demand evaluation only (no background workers)
**Scale/Scope**: Same user base as existing API; alerts stored alongside existing user/portfolio data

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

Constitution is in template state (not customized for this project). Applying implicit project conventions from existing codebase:

| Gate | Status | Evidence |
|------|--------|----------|
| Follows existing patterns | PASS | Uses same service/router/model structure as features 001-003 |
| No unnecessary complexity | PASS | Reuses existing auth, signal generation, portfolio services |
| File-based storage consistency | PASS | Same JSON + RLock + atomic write pattern as portfolio_service |
| Test coverage | PASS | Unit + integration tests planned following existing test structure |
| No hardcoded secrets | PASS | Config via Settings (pydantic-settings) + .env |

## Project Structure

### Documentation (this feature)

```text
specs/004-alerts-notifications/
├── spec.md              # Feature specification
├── plan.md              # This file
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output
├── quickstart.md        # Phase 1 output
├── contracts/           # Phase 1 output
│   └── alerts-api.md    # REST API contracts
├── checklists/
│   └── requirements.md  # Spec quality checklist
└── tasks.md             # Phase 2 output (via /sp.tasks)
```

### Source Code (repository root)

```text
app/
├── models/
│   └── alert.py              # Alert, AlertType, AlertCreate, AlertResponse, TriggeredAlert
├── services/
│   └── alert_service.py      # AlertService (CRUD + evaluation logic)
├── api/
│   ├── routes/
│   │   └── alerts.py         # /alerts endpoints (list, create, delete, triggered)
│   ├── dependencies.py       # Add get_alert_service() dependency
│   └── errors.py             # Add AlertLimitExceededError, AlertNotFoundError
├── config.py                 # Add ALERTS_DATA_FILE, ALERTS_MAX_PER_USER settings
└── main.py                   # Register alerts_router

data/
└── alerts.json               # Runtime alert storage (auto-created)

tests/
├── unit/
│   └── test_alert_service.py # AlertService unit tests
└── integration/
    └── test_alerts_api.py    # Alerts endpoint integration tests
```

**Structure Decision**: Extends the existing single-project structure. One new model file, one new service file, one new router file. Follows the exact same organization as the portfolio feature (feature 003).

## Complexity Tracking

No constitution violations. No complexity justification needed.
