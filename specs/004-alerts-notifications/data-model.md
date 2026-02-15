# Data Model: Alerts & Notifications

**Feature**: 004-alerts-notifications
**Date**: 2026-02-15

## Entities

### AlertType (Enum)

Defines the three types of alerts supported.

| Value | Description |
|-------|-------------|
| `price_threshold` | Triggers when stock price crosses above/below a target price |
| `signal_change` | Triggers when stock's trading signal matches a target signal |
| `portfolio_value` | Triggers when portfolio value changes by a percentage threshold |

### PriceDirection (Enum)

Direction for price threshold alerts.

| Value | Description |
|-------|-------------|
| `above` | Alert triggers when current price is above target price |
| `below` | Alert triggers when current price is below target price |

### SignalTarget (Enum)

Target signal for signal change alerts. Reuses existing `SignalAction` values.

| Value | Description |
|-------|-------------|
| `BUY` | Alert triggers when stock signal is BUY |
| `SELL` | Alert triggers when stock signal is SELL |
| `HOLD` | Alert triggers when stock signal is HOLD |

### Alert (Persisted Entity)

The core alert entity stored in `data/alerts.json`.

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `id` | string (UUID4) | Yes | Unique alert identifier |
| `user_id` | string | Yes | Owner's user ID (from authentication) |
| `alert_type` | AlertType | Yes | One of: price_threshold, signal_change, portfolio_value |
| `ticker` | string | Conditional | Stock ticker symbol (required for price_threshold and signal_change) |
| `target_price` | float | Conditional | Target price (required for price_threshold) |
| `price_direction` | PriceDirection | Conditional | above/below (required for price_threshold) |
| `target_signal` | SignalTarget | Conditional | Target signal (required for signal_change) |
| `percentage_threshold` | float | Conditional | Percentage change threshold (required for portfolio_value) |
| `baseline_value` | float | Conditional | Portfolio value at alert creation time (set for portfolio_value) |
| `created_at` | datetime (ISO 8601) | Yes | Timestamp of alert creation |

**Validation Rules**:
- `ticker` must be a valid, uppercase stock symbol (validated via existing `validate_ticker()`)
- `target_price` must be positive (> 0)
- `percentage_threshold` must be positive (> 0, representing a percentage like 5.0 for 5%)
- `baseline_value` is computed at creation time, not user-supplied
- Conditional fields must be present based on `alert_type`:
  - `price_threshold` requires: `ticker`, `target_price`, `price_direction`
  - `signal_change` requires: `ticker`, `target_signal`
  - `portfolio_value` requires: `percentage_threshold` (baseline_value auto-set)

### TriggeredAlert (Transient — Not Persisted)

Computed on-demand when evaluating alerts. Returned in `GET /alerts/triggered` response.

| Field | Type | Description |
|-------|------|-------------|
| `alert` | Alert | The original alert rule |
| `triggered` | boolean | Whether the condition is currently met |
| `current_value` | string | Current price, signal, or portfolio value (as display string) |
| `details` | string | Human-readable description of the evaluation result |
| `error` | string or null | Error message if evaluation failed for this alert |
| `evaluated_at` | datetime (ISO 8601) | Timestamp of evaluation |

## Relationships

```text
User (1) ──────── (0..10) Alert
  │                         │
  └── Portfolio (0..1)      └── TriggeredAlert (computed, 0..1 per check)
       │
       └── Holdings (0..20)
```

- Each **User** can have 0 to 10 **Alerts** (enforced limit)
- Each **Alert** belongs to exactly one **User** (isolated by user_id)
- **TriggeredAlert** is computed per alert during evaluation — not stored
- **Portfolio Value alerts** require the user to have a **Portfolio** with holdings

## Storage Format

File: `data/alerts.json`

```json
{
  "user-id-abc123": [
    {
      "id": "alert-uuid-1",
      "user_id": "user-id-abc123",
      "alert_type": "price_threshold",
      "ticker": "AAPL",
      "target_price": 200.0,
      "price_direction": "above",
      "target_signal": null,
      "percentage_threshold": null,
      "baseline_value": null,
      "created_at": "2026-02-15T10:30:00+00:00"
    },
    {
      "id": "alert-uuid-2",
      "user_id": "user-id-abc123",
      "alert_type": "signal_change",
      "ticker": "TSLA",
      "target_price": null,
      "price_direction": null,
      "target_signal": "BUY",
      "percentage_threshold": null,
      "baseline_value": null,
      "created_at": "2026-02-15T11:00:00+00:00"
    },
    {
      "id": "alert-uuid-3",
      "user_id": "user-id-abc123",
      "alert_type": "portfolio_value",
      "ticker": null,
      "target_price": null,
      "price_direction": null,
      "target_signal": null,
      "percentage_threshold": 5.0,
      "baseline_value": 15000.50,
      "created_at": "2026-02-15T12:00:00+00:00"
    }
  ]
}
```

## State Transitions

Alerts have a simple lifecycle — no state machine:

1. **Created** → Alert is persisted with all fields validated
2. **Active** → Alert exists and is evaluated on each triggered-alerts check
3. **Deleted** → Alert is removed from storage permanently

There is no paused, snoozed, or expired state (per spec: out of scope).
