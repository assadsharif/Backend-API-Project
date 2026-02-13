---
name: pytest-tdd
description: >
  Comprehensive pytest and Test-Driven Development (TDD) toolkit. Use when:
  (1) Setting up pytest in a Python project, (2) Following TDD Red-Green-Refactor
  workflow, (3) Writing tests with fixtures, parametrization, or mocking,
  (4) Organizing test suites, (5) Running tests in watch mode, or
  (6) Any pytest-related testing task requiring TDD best practices.
  Triggers include "TDD", "pytest", "test first", "Red Green Refactor",
  "write tests", "test driven", "property based testing", or requests
  to add test coverage.
---

# Python TDD Skill

Senior Python Engineer executing strict Test-Driven Development.
Generate production-grade code via TDD — no tutorials, no theory dumps.

## What This Skill Does

- Execute Red-Green-Refactor TDD cycles
- Generate failing tests BEFORE implementation
- Write pytest suites (fixtures, parametrize, mocking, property-based)
- Apply TDD to APIs (FastAPI/Flask), databases (SQLModel/SQLAlchemy), and architecture
- Refactor legacy code safely via characterization tests

## What This Skill Does NOT Do

- Teach TDD theory or philosophy
- Generate implementation without tests first
- Write unittest-style tests (unless legacy/interview context requires it)
- Create UI/browser tests (use Playwright/Selenium skills instead)
- Perform load testing or benchmarking

## Required Clarifications

Before generating, ask:

1. **Project context**: "What framework/stack? (FastAPI, Flask, Django, plain Python)"
2. **Test scope**: "Unit tests, integration tests, or both?"
3. **Existing code?**: "Is this greenfield or adding tests to existing code?"

## Optional Clarifications

4. **CI requirements**: "Any CI constraints (timeout, coverage threshold)?" (ask if mentioned)
5. **Mocking boundaries**: "Which external services need mocking?" (ask if integration-heavy)

## Before Asking

Check existing context first:
- Review conversation for framework/stack mentions
- Infer from file names (e.g., `main.py` with FastAPI imports)
- Check pyproject.toml/requirements.txt if available
- Only ask what cannot be determined from context

---

## Core TDD Rules

1. ALWAYS write tests BEFORE implementation (RED -> GREEN -> REFACTOR)
2. Start with error paths, NOT happy path
3. Tests must be: Fast (ms), Deterministic (no flakiness), Isolated (no shared state)
4. Use pytest as primary framework
5. Follow AAA (Arrange-Act-Assert) or Given-When-Then structure
6. Use parametrized tests instead of loops
7. Prefer fewer high-signal tests over many weak tests
8. If a test is slow, flaky, or unclear — refactor the TEST first

## Output Format

1. Start with FAILING TESTS only (RED)
2. Write MINIMAL implementation to pass (GREEN)
3. Refactor code AND tests if needed (REFACTOR)
4. Brief decision notes ONLY if non-obvious
5. Never dump theory or long explanations

---

## Must Follow

- [ ] Tests written before implementation
- [ ] Error paths tested before happy path
- [ ] Clear test naming (`test_<unit>_<scenario>_<expected>`)
- [ ] Dependency injection for testable design
- [ ] No hidden side effects in modules
- [ ] Property-based testing (hypothesis) for non-trivial logic
- [ ] Mocking only at boundaries (external APIs, time, randomness)
- [ ] Each test runs in isolation (no shared mutable state)

## Must Avoid

- Writing implementation before tests
- Testing implementation details instead of behavior
- Over-mocking (mocking your own code)
- Shared state between tests
- Flaky tests (time-dependent, order-dependent, network-dependent)
- God-objects and tight coupling
- `sleep()` in tests
- Ignoring test smells (duplicate setup, assertion-free tests, commented tests)

---

## Output Checklist

Before delivering, verify ALL items:

### Functional
- [ ] All tests fail before implementation (RED confirmed)
- [ ] All tests pass after implementation (GREEN confirmed)
- [ ] Refactoring preserves passing tests
- [ ] Edge cases covered (empty inputs, None, boundaries)

### Quality
- [ ] Test names describe behavior, not implementation
- [ ] No hardcoded test data (use factories/fixtures)
- [ ] Parametrized tests for similar scenarios
- [ ] Coverage of error paths matches or exceeds happy paths

### Standards
- [ ] pytest conventions followed (conftest.py, fixtures, markers)
- [ ] No print() debugging left in tests
- [ ] Tests run in <5 seconds total (unit tests)
- [ ] No external dependencies in unit tests

---

## Error Handling Guidance

| Scenario | Action |
|----------|--------|
| Existing code has no tests | Write characterization tests first, then refactor |
| Test is flaky | Identify source (time, ordering, network), fix or mark `@pytest.mark.flaky` |
| Legacy unittest code | Keep as-is unless migration requested; add new tests in pytest |
| CI timeout | Split slow tests with `@pytest.mark.slow`, run separately |
| Coverage gaps | Prioritize untested error paths over more happy-path tests |

## Dependencies

### Required
- Python 3.10+
- pytest >= 7.0

### Recommended
- pytest-cov (coverage reporting)
- pytest-mock (mocker fixture)
- hypothesis (property-based testing)
- factory-boy (test data factories)
- faker (realistic test data)

### Framework-Specific
- httpx / fastapi.testclient (FastAPI testing)
- pytest-django (Django testing)
- pytest-asyncio (async code testing)

---

## Official Documentation

| Resource | URL | Use For |
|----------|-----|---------|
| pytest docs | https://docs.pytest.org/en/stable/ | Core API, fixtures, plugins |
| pytest-mock | https://pytest-mock.readthedocs.io/ | Mocker fixture patterns |
| hypothesis | https://hypothesis.readthedocs.io/ | Property-based testing |
| factory-boy | https://factoryboy.readthedocs.io/ | Test data factories |
| coverage.py | https://coverage.readthedocs.io/ | Coverage configuration |
| FastAPI testing | https://fastapi.tiangolo.com/tutorial/testing/ | TestClient patterns |
| SQLModel testing | https://sqlmodel.tiangolo.com/tutorial/ | DB test patterns |

For patterns not covered here, fetch from the official pytest docs.

## Reference Files

| File | When to Read |
|------|--------------|
| `references/backend-api-tdd.md` | Testing FastAPI/Flask endpoints |
| `references/database-tdd.md` | SQLModel/SQLAlchemy test patterns |
| `references/mocking-isolation.md` | Mock boundaries and techniques |
| `references/architecture-via-tdd.md` | Using TDD to drive clean architecture |

---

## Keeping Current

- pytest releases: https://docs.pytest.org/en/stable/changelog.html
- Last verified: 2026-01
- When pytest updates: check for deprecated fixtures, new assertion patterns
