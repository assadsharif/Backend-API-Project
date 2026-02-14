# Tasks: User Authentication

**Input**: Design documents from `/specs/002-user-authentication/`
**Prerequisites**: plan.md ✅, spec.md ✅, research.md ✅, data-model.md ✅, contracts/openapi.yaml ✅

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Configuration and directory structure for auth feature

- [x] T001 Create data/ directory at project root and add data/ to .gitignore (user data should not be committed)
- [x] T002 Update app/config.py to add auth settings: ADMIN_API_KEY (env var, default None), USER_DATA_FILE (default "data/users.json"), RATE_LIMIT_MAX_REQUESTS (default 100), RATE_LIMIT_WINDOW_SECONDS (default 3600)
- [x] T003 [P] Update .env.example to include ADMIN_API_KEY placeholder

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core auth infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [x] T004 Create app/models/user.py with Pydantic models: UserStatus enum, User model, UserRegistrationRequest, UserRegistrationResponse, UserDetailResponse, UserListResponse, AdminKeyRegenerateResponse per data-model.md
- [x] T005 Add auth error classes to app/api/errors.py: AuthenticationError (401), AccountDisabledError (403), RateLimitExceededError (429), EmailConflictError (409), AdminNotConfiguredError (503), and register their exception handlers
- [x] T006 Implement app/services/user_service.py with UserService class: load/save JSON file with threading.Lock, create_user (generate UUID + API key via secrets.token_hex(16), validate unique email), get_user_by_api_key, get_user_by_id, list_users, update_last_active, increment_request_count. Use atomic writes (temp file + os.replace). Handle corrupted JSON gracefully (log warning, start empty).
- [x] T007 Add auth dependencies to app/api/dependencies.py: get_user_service() singleton, get_current_user(x_api_key: str = Header()) that validates API key and checks user status (raise AuthenticationError for invalid key, AccountDisabledError for disabled user), require_admin(x_admin_key: str = Header()) that checks against settings.ADMIN_API_KEY (raise AdminNotConfiguredError if not set, AuthenticationError if invalid)

**Checkpoint**: Foundation ready - user story implementation can now begin

---

## Phase 3: User Story 1 - Register and Get API Key (Priority: P1) 🎯 MVP

**Goal**: Enable users to register, receive an API key, and use it to access protected endpoints

**Independent Test**: Register a new user with name and email, receive an API key, then use that key to successfully call `/signal/AAPL`. Verify that calling `/signal/AAPL` without the key returns 401.

### Implementation for User Story 1

- [x] T008 [US1] Create app/api/routes/auth.py with POST /auth/register endpoint: accept UserRegistrationRequest body, call user_service.create_user, return 201 with UserRegistrationResponse including api_key. Handle EmailConflictError (409) and validation errors (400).
- [x] T009 [US1] Register auth router in app/main.py with prefix="/auth" and tags=["Authentication"]
- [x] T010 [US1] Add get_current_user dependency to app/api/routes/signals.py GET /signal/{ticker} endpoint. Update the route function signature to include current_user parameter via Depends(get_current_user). Call user_service.update_last_active and increment_request_count on successful auth.
- [x] T011 [US1] Add get_current_user dependency to app/api/routes/indicators.py GET /indicators/{ticker} endpoint. Same pattern as T010.
- [x] T012 [US1] Verify /health, /docs, /openapi.json, /redoc, and / (root) endpoints remain unauthenticated — no changes needed to these routes
- [x] T013 [US1] Update existing tests in tests/integration/test_api.py to add FastAPI dependency_overrides for get_current_user so existing 101 tests continue to pass without API keys
- [x] T014 [US1] Verify POST /auth/register returns 201 with valid api_key, and duplicate email returns 409

**Checkpoint**: User Story 1 complete — users can register and access protected endpoints with API keys

---

## Phase 4: User Story 2 - Rate Limiting Per API Key (Priority: P2)

**Goal**: Enforce 100 requests/hour per API key with rate limit headers on all authenticated responses

**Independent Test**: Register a user, make 100 requests (all succeed with rate limit headers), make 101st request and verify 429 response with reset time.

### Implementation for User Story 2

- [x] T015 [US2] Implement app/services/rate_limiter.py with RateLimiter class: in-memory dict[str, list[float]] tracking request timestamps per API key, check_rate_limit(api_key) method that prunes expired timestamps (older than 1 hour), counts requests in current window, returns RateLimitInfo (limit, remaining, reset_at). Raise RateLimitExceededError if count >= 100.
- [x] T016 [US2] Add get_rate_limiter() singleton and check_rate_limit dependency to app/api/dependencies.py. The check_rate_limit dependency should call rate_limiter.check_rate_limit(current_user.api_key) and return RateLimitInfo.
- [x] T017 [US2] Add rate limit dependency to app/api/routes/signals.py: add Depends(check_rate_limit) and inject X-RateLimit-Limit, X-RateLimit-Remaining, X-RateLimit-Reset headers into the response.
- [x] T018 [US2] Add rate limit dependency to app/api/routes/indicators.py: same pattern as T017.
- [x] T019 [US2] Verify rate limit headers appear on all authenticated responses and 429 is returned when limit exceeded

**Checkpoint**: User Stories 1 AND 2 complete — users are rate-limited to 100 req/hour with clear feedback

---

## Phase 5: User Story 3 - Admin User Management (Priority: P3)

**Goal**: Enable administrators to list users, view details, disable/enable accounts, and regenerate API keys

**Independent Test**: Using the admin key, list all users, disable a user (verify their key returns 403), re-enable (verify key works), regenerate key (verify old key fails, new key works).

### Implementation for User Story 3

- [x] T020 [US3] Add disable_user, enable_user, regenerate_api_key methods to app/services/user_service.py. disable_user sets status to "disabled" and persists. enable_user sets status to "active" and persists. regenerate_api_key generates new key via secrets.token_hex(16), invalidates old key, persists, returns new key.
- [x] T021 [US3] Create app/api/routes/admin.py with admin endpoints per openapi.yaml: GET /admin/users (list all users as UserListResponse), GET /admin/users/{user_id} (get user detail as UserDetailResponse), POST /admin/users/{user_id}/disable (disable user), POST /admin/users/{user_id}/enable (enable user), POST /admin/users/{user_id}/regenerate-key (return AdminKeyRegenerateResponse). All endpoints use Depends(require_admin).
- [x] T022 [US3] Register admin router in app/main.py with prefix="/admin" and tags=["Admin"]
- [x] T023 [US3] Add structured logging for all admin actions in app/api/routes/admin.py: log admin user list, disable, enable, regenerate events with user_id
- [x] T024 [US3] Verify admin endpoints return 401 without admin key, 503 when ADMIN_API_KEY not configured, and 404 for non-existent user_id

**Checkpoint**: All user stories complete — full auth, rate limiting, and admin management operational

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories

- [x] T025 [P] Add structured logging for auth events in app/api/dependencies.py: log successful auth, failed auth (invalid key), disabled user access, rate limit exceeded
- [x] T026 [P] Verify OpenAPI documentation at /docs includes all new endpoints (auth, admin) with correct schemas
- [x] T027 [P] Update README.md with authentication section: how to register, how to use API key, rate limits, admin operations
- [x] T028 Run quickstart.md manual test checklist (14 items) and verify all pass
- [x] T029 Validate all endpoints against contracts/openapi.yaml schema compliance
- [x] T030 Performance validation: verify auth overhead adds <50ms per request (SC-002)
- [x] T031 Verify user data persists across server restart (SC-005): register user, stop server, start server, use same API key

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies — can start immediately
- **Foundational (Phase 2)**: Depends on Phase 1 completion — BLOCKS all user stories
- **User Story 1 (Phase 3)**: Depends on Foundational phase completion
- **User Story 2 (Phase 4)**: Depends on User Story 1 (needs auth working to add rate limiting on top)
- **User Story 3 (Phase 5)**: Depends on Foundational phase (uses user_service, but independently testable after Phase 2)
- **Polish (Phase 6)**: Depends on all user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational (Phase 2) — **THIS IS THE MVP**
- **User Story 2 (P2)**: Depends on User Story 1 — adds rate limiting to already-protected endpoints
- **User Story 3 (P3)**: Can start after Foundational (Phase 2) — admin operates on user_service independently. However, recommended after US1 to validate full auth flow.

### Within Each User Story

**User Story 1 Pattern**:
1. Auth endpoint first (registration)
2. Protect existing endpoints (add dependency)
3. Fix existing tests (dependency overrides)
4. Validate end-to-end

**User Story 2 Pattern**:
1. Rate limiter service first
2. Add rate limit dependency
3. Apply to protected endpoints
4. Validate headers and 429 responses

**User Story 3 Pattern**:
1. Extend user_service with admin methods
2. Create admin endpoints
3. Register router
4. Add logging and validate

### Parallel Opportunities

**Phase 1 (Setup)**: T001, T002, T003 — T002 and T003 can run in parallel after T001
**Phase 2 (Foundational)**: T004 and T005 can run in parallel (different files); T006 depends on T004; T007 depends on T005 and T006
**User Story 1**: T010 and T011 can run in parallel (different files, same pattern)
**User Story 2**: T017 and T018 can run in parallel (different files, same pattern)
**User Story 3**: T020 before T021; T023 in parallel with T024
**Phase 6 (Polish)**: T025, T026, T027 can all run in parallel

---

## Parallel Example: User Story 1

```bash
# After T008 and T009 complete (auth endpoint ready):
T010: "Add auth dependency to app/api/routes/signals.py"
T011: "Add auth dependency to app/api/routes/indicators.py"
# These modify different files with the same pattern — safe to parallelize
```

## Parallel Example: User Story 2

```bash
# After T015 and T016 complete (rate limiter ready):
T017: "Add rate limit to app/api/routes/signals.py"
T018: "Add rate limit to app/api/routes/indicators.py"
# These modify different files with the same pattern — safe to parallelize
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup (T001-T003)
2. Complete Phase 2: Foundational (T004-T007) — CRITICAL, blocks all stories
3. Complete Phase 3: User Story 1 (T008-T014)
4. **STOP and VALIDATE**: Register user, use API key on /signal/AAPL, verify 401 without key
5. Deploy MVP — API is now secured with API key authentication!

**MVP Scope**: Setup + Foundational + User Story 1 = 14 tasks
**MVP Value**: Core API key authentication operational

### Incremental Delivery

1. **Foundation** (Phases 1-2): Complete T001-T007 → Auth infrastructure ready
2. **MVP Release** (Phase 3): Add T008-T014 → Users can register and authenticate → DEPLOY
3. **Rate Limiting** (Phase 4): Add T015-T019 → Users are rate-limited → DEPLOY
4. **Admin Control** (Phase 5): Add T020-T024 → Admins can manage users → DEPLOY
5. **Production Ready** (Phase 6): Add T025-T031 → Logging, docs, validation → DEPLOY

Each phase adds value without breaking previous functionality.

---

## Task Count Summary

- **Phase 1 (Setup)**: 3 tasks
- **Phase 2 (Foundational)**: 4 tasks
- **Phase 3 (User Story 1)**: 7 tasks ← **MVP ends here (14 total tasks)**
- **Phase 4 (User Story 2)**: 5 tasks
- **Phase 5 (User Story 3)**: 5 tasks
- **Phase 6 (Polish)**: 7 tasks

**Total**: 31 tasks

**MVP Path**: T001-T014 (14 tasks) delivers User Story 1 (P1) — API key authentication
**Full Feature**: All 31 tasks deliver complete auth, rate limiting, and admin management

---

## Success Criteria Validation

After completing all tasks, verify:

- [ ] **SC-001**: Users can register and receive an API key in under 2 seconds
- [ ] **SC-002**: Authenticated requests add less than 50 milliseconds of overhead
- [ ] **SC-003**: 100% of requests to protected endpoints without a valid key are rejected
- [ ] **SC-004**: Rate limiting correctly enforces the 100 requests/hour limit
- [ ] **SC-005**: User data persists across server restarts with zero data loss
- [ ] **SC-006**: All authentication and authorization events are logged
- [ ] **SC-007**: Admin operations complete in under 1 second each
- [ ] **SC-008**: The system handles at least 50 concurrent authenticated users

---

## Notes

- **[P] marker**: Tasks that can run in parallel (different files, no blocking dependencies)
- **[Story] label**: Maps task to specific user story (US1, US2, US3) for traceability
- **File paths**: All tasks include exact file paths for implementation
- **No tests in spec**: Feature specification does not explicitly request TDD, so standalone test file tasks are not included. Test validation is included within story tasks and polish phase.
- **Existing tests**: T013 is critical — existing 101 tests must continue to pass by adding dependency overrides
- **Incremental delivery**: Each user story can be deployed independently after completion
- **MVP focus**: User Story 1 (P1) is the minimum viable product — prioritize completing T001-T014 first

---

**Tasks generated**: 2026-02-14
**Ready for**: `/sp.implement` command to execute tasks in dependency order
