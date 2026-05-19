# API Contracts: Meeting Protocol Module

**Base URL**: `/api/v1`  
**Auth**: JWT Bearer token (access: 15 min, refresh: 7 days)  
**Routes**: [`src/adapters/api/routes/`](src/adapters/api/routes/)  
**Schemas**: [`src/adapters/api/schemas/`](src/adapters/api/schemas/)

---

## 1. Authentication

| Method | Endpoint | Auth | Request Body | Response |
|---|---|---|---|---|
| `POST` | `/auth/register` | Public | `UserCreate` | `UserResponse` (201) |
| `POST` | `/auth/login` | Public | `LoginRequest` | `TokenResponse` |

**Route**: [`src/adapters/api/routes/auth.py`](src/adapters/api/routes/auth.py)

### Request Schemas

**UserCreate** → [`src/adapters/api/schemas/user.py`](src/adapters/api/schemas/user.py)
```json
{
  "name": "string (max 255)",
  "email": "email",
  "password": "string (min 8, max 128)",
  "role": "admin | secretary | chairman | user (default: user)"
}
```

**LoginRequest**
```json
{
  "email": "email",
  "password": "string"
}
```

**TokenResponse**
```json
{
  "access_token": "string",
  "refresh_token": "string",
  "token_type": "bearer"
}
```

---

## 2. Meetings

**Route**: [`src/adapters/api/routes/meetings.py`](src/adapters/api/routes/meetings.py)

### 2.1 GET /meetings

List meetings with optional filters.

| Method | Endpoint | Auth | Query Params | Response |
|---|---|---|---|---|
| `GET` | `/meetings` | Any authenticated | `project_id`, `organization_id`, `level`, `limit`, `offset` | `list[MeetingListItem]` |

### 2.2 POST /meetings

Create a new meeting from template. Auto-imports unfinished tasks from previous meetings.

| Method | Endpoint | Auth | Request Body | Response |
|---|---|---|---|---|
| `POST` | `/meetings` | secretary, admin | `MeetingCreate` | `MeetingCreateResponse` (201) |

**MeetingCreate**
```json
{
  "title": "string (max 500)",
  "template_id": "UUID?",
  "project_id": "UUID?",
  "level": "strategic | coordination | operational | situational",
  "agenda_items": [{"position": 1, "title": "string"}]
}
```

**MeetingCreateResponse**
```json
{
  "meeting_id": "UUID",
  "status": "preparation | in_progress | on_approval | approved",
  "imported_legacy_tasks_count": 0,
  "celery_task_id": "string?"
}
```

### 2.3 GET /meetings/{id}/workspace

Full meeting context: breadcrumbs, participants, agenda, markdown content.

| Method | Endpoint | Auth | Response |
|---|---|---|---|
| `GET` | `/meetings/{id}/workspace` | Any authenticated | `MeetingWorkspaceResponse` |

### 2.4 PATCH /meetings/{id}/content

Autosave markdown content. **Blocked when status is `approved` (read-only).**

| Method | Endpoint | Auth | Request Body | Response |
|---|---|---|---|---|
| `PATCH` | `/meetings/{id}/content` | secretary, admin | `ContentUpdateRequest` | `ContentUpdateResponse` |

**ContentUpdateRequest**: `{"content_markdown": "string"}`  
**ContentUpdateResponse**: `{"status": "success", "version": 12, "updated_at": "datetime"}`

### 2.5 POST /meetings/{id}/finalize

Transition meeting from `in_progress` → `on_approval`. Only Secretary can invoke.

| Method | Endpoint | Auth | Response |
|---|---|---|---|
| `POST` | `/meetings/{id}/finalize` | secretary, admin | `StatusTransitionResponse` |

### 2.6 POST /meetings/{id}/approve

Final approval by Chairman. Transitions to `approved` (read-only). Triggers Celery tasks for PDF/XLSX export and bulk notifications.

| Method | Endpoint | Auth | Response |
|---|---|---|---|
| `POST` | `/meetings/{id}/approve` | chairman, admin | `ApproveResponse` |

**ApproveResponse** extends `StatusTransitionResponse`:
```json
{
  "meeting_id": "UUID",
  "status": "approved",
  "transition_timestamp": "datetime",
  "pdf_export_job_id": "string",
  "xlsx_export_job_id": "string"
}
```

### 2.7 Export Downloads

| Method | Endpoint | Auth | Response |
|---|---|---|---|
| `GET` | `/meetings/{id}/export/pdf` | Any authenticated | `FileResponse` (application/pdf) |
| `GET` | `/meetings/{id}/export/xlsx` | Any authenticated | `FileResponse` (application/vnd.openxmlformats-officedocument.spreadsheetml.sheet) |

---

## 3. Tasks

**Route**: [`src/adapters/api/routes/tasks.py`](src/adapters/api/routes/tasks.py)

### 3.1 POST /tasks

Create a new task with automatic hierarchical numbering (KDD-XXX-NNN).

| Method | Endpoint | Auth | Request Body | Response |
|---|---|---|---|---|
| `POST` | `/tasks` | secretary, chairman, admin | `TaskCreate` | `TaskResponse` (201) |

**TaskCreate** → [`src/adapters/api/schemas/task.py`](src/adapters/api/schemas/task.py)
```json
{
  "meeting_id": "UUID",
  "description": "string (max 2000)",
  "organization_links": ["UUID", ...]
}
```

### 3.2 GET /tasks/{id}/raci

Get current RACI assignments with validation status.

| Method | Endpoint | Auth | Response |
|---|---|---|---|
| `GET` | `/tasks/{id}/raci` | Any authenticated | `RaciResponse` |

**RaciResponse**
```json
{
  "task_id": "UUID",
  "assignments": [{"user_id": "UUID", "role": "R|A|C|I", "name": "string?"}],
  "is_valid": true,
  "errors": []
}
```

### 3.3 PUT /tasks/{id}/raci

Update RACI assignments with **strict single-Accountable validation**. Returns **422** `RACI_VALIDATION_FAILED` if 0 or 2+ Accountable roles.

| Method | Endpoint | Auth | Request Body | Response |
|---|---|---|---|---|
| `PUT` | `/tasks/{id}/raci` | chairman, admin | `RaciUpdateRequest` | `RaciResponse` or `422` |

**422 Error Response**
```json
{
  "error": "RACI_VALIDATION_FAILED",
  "message": "Критическая ошибка: Обнаружено более одной роли Accountable (A)...",
  "is_valid": false
}
```

### 3.4 POST /tasks/{id}/escalate

Escalate a task to a higher meeting level. Creates destination task with DAG link.

| Method | Endpoint | Auth | Request Body | Response |
|---|---|---|---|---|
| `POST` | `/tasks/{id}/escalate` | chairman, admin | `EscalateRequest` | `EscalateResponse` |

**EscalateRequest**: `{"target_meeting_type": "Координационное | Стратегическое | coordination | strategic", "reason": "string"}`

### 3.5 GET /tasks/{id}/dependencies

Get DAG graph edges (previous and next task in escalation chain).

| Method | Endpoint | Auth | Response |
|---|---|---|---|
| `GET` | `/tasks/{id}/dependencies` | Any authenticated | `DependencyResponse` |

**DependencyResponse**
```json
{
  "task_id": "UUID",
  "graph_edges": {
    "previous_task_id": "UUID?",
    "next_task_id": "UUID?"
  }
}
```

---

## 4. AI

**Route**: [`src/adapters/api/routes/ai.py`](src/adapters/api/routes/ai.py)

### 4.1 POST /ai/stream-audio

Upload audio chunk for STT processing (placeholder — returns recognized text stub).

| Method | Endpoint | Auth | Request | Response |
|---|---|---|---|---|
| `POST` | `/ai/stream-audio` | secretary, admin | `multipart/form-data` (audio binary) | `AudioChunkResponse` |

### 4.2 GET /meetings/{id}/ai-insights

Poll AI-generated insights: suggested action items and detected risks.

| Method | Endpoint | Auth | Response |
|---|---|---|---|
| `GET` | `/meetings/{id}/ai-insights` | Any authenticated | `AIInsightsResponse` |

**AIInsightsResponse** → [`src/adapters/api/schemas/ai.py`](src/adapters/api/schemas/ai.py)
```json
{
  "suggested_action_items": [
    {
      "temporary_id": "string",
      "extracted_description": "string",
      "confidence_score": 0.94,
      "json_schema_matched": true
    }
  ],
  "detected_risks": [
    {
      "risk_id": "string",
      "severity": "LOW | MEDIUM | HIGH | CRITICAL",
      "text_anchor": "string",
      "message": "string"
    }
  ]
}
```

---

## 5. RBAC Matrix

Implementation: [`src/infrastructure/dependencies.py`](src/infrastructure/dependencies.py)

| Endpoint | User | Secretary | Chairman | Admin |
|---|---|---|---|---|
| `GET /meetings` | ✅ | ✅ | ✅ | ✅ |
| `POST /meetings` | ❌ | ✅ | ❌ | ✅ |
| `GET /meetings/{id}/workspace` | ✅ | ✅ | ✅ | ✅ |
| `PATCH /meetings/{id}/content` | ❌ | ✅ | ❌ | ✅ |
| `POST /meetings/{id}/finalize` | ❌ | ✅ | ❌ | ✅ |
| `POST /meetings/{id}/approve` | ❌ | ❌ | ✅ | ✅ |
| `GET /meetings/{id}/export/*` | ✅ | ✅ | ✅ | ✅ |
| `POST /tasks` | ❌ | ✅ | ✅ | ✅ |
| `GET /tasks/{id}/raci` | ✅ | ✅ | ✅ | ✅ |
| `PUT /tasks/{id}/raci` | ❌ | ❌ | ✅ | ✅ |
| `POST /tasks/{id}/escalate` | ❌ | ❌ | ✅ | ✅ |
| `GET /tasks/{id}/dependencies` | ✅ | ✅ | ✅ | ✅ |
| `POST /ai/stream-audio` | ❌ | ✅ | ❌ | ✅ |
| `GET /meetings/{id}/ai-insights` | ✅ | ✅ | ✅ | ✅ |

---

## 6. Schemas Reference

All Pydantic v2 schemas in [`src/adapters/api/schemas/`](src/adapters/api/schemas/):

| File | Models |
|---|---|
| `common.py` | `ErrorResponse`, `PaginatedResponse[T]`, `SuccessResponse` |
| `user.py` | `UserBase`, `UserCreate`, `UserResponse`, `UserBrief`, `LoginRequest`, `TokenResponse` |
| `meeting.py` | `MeetingCreate`, `MeetingCreateResponse`, `MeetingListItem`, `MeetingWorkspaceResponse`, `ContentUpdateRequest/Response`, `StatusTransitionResponse`, `ApproveResponse`, `AgendaItemCreate/Response`, `ParticipantCreate/Response` |
| `task.py` | `TaskCreate`, `TaskResponse`, `TaskDetailResponse`, `RaciUpdateRequest`, `RaciResponse`, `RaciValidationErrorResponse`, `EscalateRequest/Response`, `DependencyResponse`, `RaciAssignmentCreate/Response` |
| `ai.py` | `AudioChunkResponse`, `SuggestedActionItem`, `DetectedRisk`, `AIInsightsResponse` |
| `notebook.py` | `NotebookCreate`, `NotebookResponse` |