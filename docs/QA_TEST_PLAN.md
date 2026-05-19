# QA Test Plan: Meeting Protocol Module

**Last Updated**: 2026-05-19  
**Coverage**: Critical paths, screen-level user actions, regression suite

---

## 1. Critical Path Algorithms

### 1.1 Authentication Flow

**Files**: [`src/infrastructure/auth.py`](src/infrastructure/auth.py), [`src/adapters/api/routes/auth.py`](src/adapters/api/routes/auth.py)

| ID | Scenario | Input | Expected | Severity |
|---|---|---|---|---|
| AUTH-1 | Register new user | `POST /auth/register` with `{name, email, password, role}` | 201, `UserResponse` returned | CRITICAL |
| AUTH-2 | Register duplicate email | Same email as AUTH-1 | 409, "Email already registered" | CRITICAL |
| AUTH-3 | Login valid credentials | `POST /auth/login` with correct email/pw | 200, `TokenResponse` with valid JWT | CRITICAL |
| AUTH-4 | Login invalid password | Wrong password | 401, "Invalid credentials" | CRITICAL |
| AUTH-5 | Login deactivated account | `is_active=false` user | 403, "Account deactivated" | HIGH |
| AUTH-6 | Token verification | Use token from AUTH-3 on protected endpoint | 200, response returned | CRITICAL |
| AUTH-7 | Expired token | Wait 15+ min or use expired token | 401, redirected to `/login` (frontend) | HIGH |
| AUTH-8 | Password hashing | `hash_password("test")` → `verify_password("test", hash)` | `verify_password` returns `True` | CRITICAL |
| AUTH-9 | Wrong password rejection | `verify_password("wrong", hash)` | Returns `False` | HIGH |

### 1.2 Protocol Lifecycle (State Machine)

**Files**: [`src/adapters/services/meeting_service.py`](src/adapters/services/meeting_service.py), [`src/adapters/api/routes/meetings.py`](src/adapters/api/routes/meetings.py)

| ID | Scenario | Input | Expected | Severity |
|---|---|---|---|---|
| SM-1 | Create meeting (preparation) | `POST /meetings` by secretary | 201, status=`preparation` | CRITICAL |
| SM-2 | Import legacy tasks | Create meeting with `project_id` that has unfinished tasks | `imported_legacy_tasks_count > 0` | CRITICAL |
| SM-3 | Update content (in_progress) | `PATCH /meetings/{id}/content` | 200, version incremented | CRITICAL |
| SM-4 | Reject content edit (approved) | `PATCH /content` on approved meeting | 400, error message | CRITICAL |
| SM-5 | Finalize (in_progress → on_approval) | `POST /meetings/{id}/finalize` | 200, status=`on_approval` | CRITICAL |
| SM-6 | Reject finalize from wrong state | Finalize meeting that is `preparation` | 400, error | HIGH |
| SM-7 | Approve (on_approval → approved) | Chairman calls `POST /approve` | 200, status=`approved`, Celery tasks dispatched | CRITICAL |
| SM-8 | Reject approve from wrong state | Approve meeting that is `in_progress` | 400, error | HIGH |
| SM-9 | Export PDF after approval | `GET /meetings/{id}/export/pdf` | 200, Content-Type: `application/pdf` | HIGH |
| SM-10 | Export XLSX after approval | `GET /meetings/{id}/export/xlsx` | 200, Content-Type: `application/vnd.openxmlformats-officedocument.spreadsheetml.sheet` | HIGH |

### 1.3 RACI Validation

**Files**: [`src/adapters/services/raci_service.py`](src/adapters/services/raci_service.py), [`src/adapters/api/routes/tasks.py`](src/adapters/api/routes/tasks.py)

| ID | Scenario | Input | Expected | Severity |
|---|---|---|---|---|
| RACI-1 | Valid RACI (1A + 1R) | `PUT /tasks/{id}/raci` with `[{R}, {A}]` | 200, `is_valid=true` | CRITICAL |
| RACI-2 | Multiple Accountable | PUT with 2 A's | 422, `RACI_VALIDATION_FAILED` | CRITICAL |
| RACI-3 | Zero Accountable | PUT with 0 A's | 422, error message | CRITICAL |
| RACI-4 | Self-correction (auto) | `update_assignments(auto_correct=True)` with 2 A's | First A stays, extra A's → R | HIGH |
| RACI-5 | DB trigger enforcement | Attempt INSERT of 2nd A via raw SQL | PostgreSQL exception raised | CRITICAL |
| RACI-6 | GET returns user names | `GET /tasks/{id}/raci` | Assignments include `name` field | MEDIUM |

### 1.4 Task Escalation (DAG)

**Files**: [`src/adapters/services/task_service.py`](src/adapters/services/task_service.py)

| ID | Scenario | Input | Expected | Severity |
|---|---|---|---|---|
| ESC-1 | Escalate to coordination | `POST /tasks/{id}/escalate` with `target_meeting_type=coordination` | Source → `escalated`, Dest created with `parent_task_id` | CRITICAL |
| ESC-2 | Escalate to strategic | `target_meeting_type=strategic` | Dest meeting created at strategic level | HIGH |
| ESC-3 | DAG chain | GET dependencies on escalated task | `previous_task_id` and `next_task_id` populated | HIGH |
| ESC-4 | Escalate non-existent task | Escalate invalid task_id | 404 | MEDIUM |

---

## 2. Screen-Level Test Scenarios

### 2.1 Login Screen (`/login`)

| ID | User Action | Expected Behavior |
|---|---|---|
| UI-L1 | Enter valid email + password, click "Войти" | Redirect to Dashboard `/` |
| UI-L2 | Enter invalid credentials, click "Войти" | Red error message: "Неверный email или пароль" |
| UI-L3 | Leave fields empty, click "Войти" | HTML5 validation prevents submission |
| UI-L4 | Login, close tab, reopen `/` | Should redirect to `/login` if token expired |

**Component**: [`frontend/src/pages/Login.tsx`](frontend/src/pages/Login.tsx)

### 2.2 Dashboard (`/`)

| ID | User Action | Expected Behavior |
|---|---|---|
| UI-D1 | Page loads with meetings | Cards display: title, level badge (color-coded), status, date |
| UI-D2 | Select level filter "Оперативный" | Only operational meetings shown |
| UI-D3 | Select "Все уровни" | All meetings shown |
| UI-D4 | Page loads with 0 meetings | Empty state: "Нет совещаний" message |
| UI-D5 | API returns error | Red error bar with "Повторить" link |
| UI-D6 | Click on meeting card | Navigate to `/meetings/{id}` |
| UI-D7 | API slow, initial load | Skeleton cards shown with `animate-pulse` |

**Component**: [`frontend/src/pages/Dashboard.tsx`](frontend/src/pages/Dashboard.tsx)

### 2.3 Meeting Editor (`/meetings/:id`)

| ID | User Action | Expected Behavior |
|---|---|---|
| UI-E1 | Page loads with meeting data | Breadcrumbs, status badge, participants, agenda rendered |
| UI-E2 | Type in textarea | Content updates locally, status bar shows "● Не сохранено" |
| UI-E3 | Wait 3 seconds | Autosave fires, status shows "✓ Сохранено", version increments |
| UI-E4 | Click "Завершить" (secretary, in_progress) | Meeting moves to `on_approval`, button changes |
| UI-E5 | Click "Утвердить" (chairman, on_approval) | Meeting moves to `approved`, export buttons appear, textarea disables |
| UI-E6 | Try to edit approved meeting | Textarea is disabled (gray background) |
| UI-E7 | Click PDF export button | Browser downloads PDF file |
| UI-E8 | Click Excel export button | Browser downloads XLSX file |
| UI-E9 | Approval stepper display | Correct step highlighted: green for completed, blue for current |

**Component**: [`frontend/src/pages/MeetingEditor.tsx`](frontend/src/pages/MeetingEditor.tsx)

### 2.4 AI Panel (right sidebar)

| ID | User Action | Expected Behavior |
|---|---|---|
| UI-AI1 | Page loads, AI panel visible | Three sections: 💡 Tasks, ⚠️ Risks, 🎙 Transcript |
| UI-AI2 | Wait 10 seconds | AI insights polled automatically |
| UI-AI3 | Click [+Добавить] on suggested task | Task created via API, button shows "..." during request |
| UI-AI4 | Risk card severity colors | CRITICAL=red border, HIGH=orange, MEDIUM=yellow, LOW=gray |

**Component**: [`frontend/src/components/ai/AIPanel.tsx`](frontend/src/components/ai/AIPanel.tsx)

### 2.5 RACI Grid

| ID | User Action | Expected Behavior |
|---|---|---|
| UI-R1 | Open RACI grid from task | Table shows current assignments with role badges |
| UI-R2 | Click "Редактировать" | Role dropdowns appear on each row |
| UI-R3 | Change role, click "Сохранить" | PUT /raci called, grid refreshes |
| UI-R4 | Set 2 Accountable roles, save | 422 error displayed: "Более одной роли Accountable" |

**Component**: [`frontend/src/components/raci/RACIGrid.tsx`](frontend/src/components/raci/RACIGrid.tsx)

### 2.6 Escalation

| ID | User Action | Expected Behavior |
|---|---|---|
| UI-ESC1 | Open task modal, click "Эскалировать" | Escalation panel expands with level selector + reason field |
| UI-ESC2 | Select "Координационный", fill reason, submit | Escalation API called, modal closes |
| UI-ESC3 | Dependency chain render | Previous → Current → Next nodes visible with arrows |

**Component**: [`frontend/src/components/tasks/TaskDetailModal.tsx`](frontend/src/components/tasks/TaskDetailModal.tsx)

---

## 3. Regression Test Suite

Run after every pull request, merge, or deployment.

### Backend (pytest)

| # | Test | Command | Expected |
|---|---|---|---|
| R1 | Import all modules | `python -c "from src.main import app"` | No errors |
| R2 | All routes registered | Check all 22 routes present | See API_CONTRACTS.md |
| R3 | Auth hash/verify | `hash_password()` → `verify_password()` | Round-trip works |
| R4 | JWT encode/decode | `create_access_token()` → `decode_token()` | Payload preserved |
| R5 | Alembic upgrade head | `alembic upgrade head` | No errors, 10 tables created |
| R6 | Settings load | `get_settings()` with `.env` | All defaults load |

### Frontend (manual checklist)

| # | Test | Steps | Expected |
|---|---|---|---|
| R7 | TypeScript compile | `npx tsc --noEmit` in `frontend/` | Zero errors |
| R8 | Vite dev server | `npm run dev` | Starts on port 5173, no console errors |
| R9 | Dashboard loads | Navigate to `/` | Cards render (or empty state) |
| R10 | Editor loads | Navigate to `/meetings/:id` | 3-column layout renders |
| R11 | Login works | Login with valid creds | Redirects to `/` |

### API (curl / HTTP client)

| # | Test | Request | Expected Status |
|---|---|---|---|
| R12 | Health check | `GET /api/health` | 200 |
| R13 | Register | `POST /api/v1/auth/register` | 201 |
| R14 | Login | `POST /api/v1/auth/login` | 200 |
| R15 | List meetings (auth) | `GET /api/v1/meetings` with Bearer | 200 |
| R16 | List meetings (no auth) | `GET /api/v1/meetings` without Bearer | 401 |
| R17 | Create meeting (secretary) | `POST /api/v1/meetings` as secretary | 201 |
| R18 | Create meeting (user) | `POST /api/v1/meetings` as regular user | 403 |
| R19 | Approve meeting (chairman) | `POST /api/v1/meetings/{id}/approve` as chairman | 200 |
| R20 | Approve meeting (secretary) | Same as above as secretary | 403 |

---

## 4. QA Report Template

Every code change must generate a report saved to `docs/qa/QA_REPORT_{YYYY-MM-DD}_{TASK_ID}.md`:

```markdown
# QA Report — {date} — {task description}

## Changes Made
- File: {path}, Lines: {range}, Change: {description}

## Test Execution

### Backend
| ID | Scenario | Result |
|---|---|---|
| R1 | Import all modules | PASSED |
| R2 | All routes registered | PASSED |
| ... | ... | ... |

### Critical Path
| ID | Scenario | Result |
|---|---|---|
| SM-1 | Create meeting | PASSED |
| SM-6 | Reject finalize from wrong state | PASSED |
| ... | ... | ... |

### Frontend
| ID | Scenario | Result |
|---|---|---|
| R7 | TypeScript compile | PASSED |
| R9 | Dashboard loads | PASSED |
| ... | ... | ... |

## Errors
{N/A or paste error logs}

## Verdict
{PASSED / FAILED — explanation}
```