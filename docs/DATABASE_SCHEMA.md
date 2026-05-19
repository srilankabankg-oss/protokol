# Database Schema: Meeting Protocol Module

**Engine**: PostgreSQL 16 + SQLAlchemy 2.0 (async via asyncpg)  
**Migrations**: Alembic — [`alembic/`](alembic/)  
**Models**: [`src/adapters/db/models/`](src/adapters/db/models/)

---

## 1. Entity-Relationship Overview

```
users ──┐                     organizations ──┐
        │                                     │
        ├── meeting_participants               ├── task_organizations
        │                                     │
meetings ──┬── agenda_items                  │
           │                                  │
           ├── tasks ──┬── raci_assignments ──┘
           │           │
           │           ├── parent_task (self-ref FK → DAG)
           │           │
           └── meeting_notebooks              │
                       │                     │
                  notebooks (self-ref FK → hierarchy)
```

---

## 2. Core Enums

Defined in [`src/core/enums.py`](src/core/enums.py):

| Enum | Values | Used In |
|---|---|---|
| `UserRole` | `admin`, `secretary`, `chairman`, `user` | `users.role` |
| `MeetingLevel` | `strategic`, `coordination`, `operational`, `situational` | `meetings.level` |
| `MeetingStatus` | `preparation`, `in_progress`, `on_approval`, `approved` | `meetings.status` |
| `WorkflowStage` | `to_do`, `in_progress`, `escalated`, `completed` | `tasks.workflow_stage` |
| `RaciRole` | `R`, `A`, `C`, `I` | `raci_assignments.role` |
| `ParticipantRole` | `chairman`, `secretary`, `participant` | `meeting_participants.role_in_meeting` |

---

## 3. Table Definitions

### 3.1 `users`

**File**: [`src/adapters/db/models/user.py`](src/adapters/db/models/user.py)

| Column | Type | Constraints |
|---|---|---|
| `id` | `UUID` (PK) | `default=uuid4` |
| `name` | `VARCHAR(255)` | `NOT NULL` |
| `email` | `VARCHAR(255)` | `UNIQUE`, `NOT NULL`, `INDEX` |
| `hashed_password` | `VARCHAR(255)` | `NOT NULL` |
| `role` | `ENUM(UserRole)` | `DEFAULT 'user'`, `NOT NULL` |
| `org_id` | `UUID` | `NULLABLE` |
| `is_active` | `BOOLEAN` | `DEFAULT TRUE` |
| `created_at` | `TIMESTAMPTZ` | `server_default=now()` |
| `updated_at` | `TIMESTAMPTZ` | `server_default=now()`, `onupdate=now()` |

**Relationships**: `raci_assignments` → `RaciAssignment.user`

---

### 3.2 `meetings`

**File**: [`src/adapters/db/models/meeting.py`](src/adapters/db/models/meeting.py)

| Column | Type | Constraints |
|---|---|---|
| `id` | `UUID` (PK) | `default=uuid4` |
| `title` | `VARCHAR(500)` | `NOT NULL` |
| `template_id` | `UUID` | `NULLABLE` |
| `project_id` | `UUID` | `NULLABLE` |
| `level` | `ENUM(MeetingLevel)` | `DEFAULT 'operational'`, `NOT NULL` |
| `status` | `ENUM(MeetingStatus)` | `DEFAULT 'preparation'`, `NOT NULL` |
| `content_markdown` | `TEXT` | `NULLABLE` |
| `date` | `TIMESTAMPTZ` | `NULLABLE` |
| `version` | `INTEGER` | `DEFAULT 1` |
| `created_at` | `TIMESTAMPTZ` | `server_default=now()` |
| `updated_at` | `TIMESTAMPTZ` | `server_default=now()`, `onupdate=now()` |

**Relationships**:
- `tasks` → `Task.meeting` (cascade delete)
- `participants` → `Participant.meeting` (cascade delete)
- `agenda_items` → `AgendaItem.meeting` (cascade delete)
- `notebook_links` → `MeetingNotebook.meeting` (cascade delete)

---

### 3.3 `meeting_participants`

**File**: [`src/adapters/db/models/participant.py`](src/adapters/db/models/participant.py)

| Column | Type | Constraints |
|---|---|---|
| `id` | `UUID` (PK) | `default=uuid4` |
| `meeting_id` | `UUID` (FK → meetings.id) | `NOT NULL`, `ON DELETE CASCADE` |
| `user_id` | `UUID` (FK → users.id) | `NOT NULL`, `ON DELETE CASCADE` |
| `role_in_meeting` | `ENUM(ParticipantRole)` | `DEFAULT 'participant'` |
| `is_present` | `BOOLEAN` | `DEFAULT TRUE` |

**Constraints**: `UNIQUE(meeting_id, user_id)`

---

### 3.4 `agenda_items`

**File**: [`src/adapters/db/models/agenda.py`](src/adapters/db/models/agenda.py)

| Column | Type | Constraints |
|---|---|---|
| `id` | `UUID` (PK) | `default=uuid4` |
| `meeting_id` | `UUID` (FK → meetings.id) | `NOT NULL`, `INDEX`, `ON DELETE CASCADE` |
| `position` | `INTEGER` | `NOT NULL` |
| `title` | `VARCHAR(500)` | `NOT NULL` |
| `is_completed` | `BOOLEAN` | `DEFAULT FALSE` |

---

### 3.5 `tasks`

**File**: [`src/adapters/db/models/task.py`](src/adapters/db/models/task.py)

| Column | Type | Constraints |
|---|---|---|
| `id` | `UUID` (PK) | `default=uuid4` |
| `meeting_id` | `UUID` (FK → meetings.id) | `NOT NULL`, `INDEX`, `ON DELETE CASCADE` |
| `task_number` | `VARCHAR(50)` | `UNIQUE`, `NOT NULL` (KDD-XXX-NNN format) |
| `description` | `TEXT` | `NOT NULL` |
| `workflow_stage` | `ENUM(WorkflowStage)` | `DEFAULT 'to_do'` |
| `is_ai_processed` | `BOOLEAN` | `DEFAULT TRUE` |
| `planned_start` | `TIMESTAMPTZ` | `NULLABLE` |
| `deadline` | `TIMESTAMPTZ` | `NULLABLE` |
| `completed_at` | `TIMESTAMPTZ` | `NULLABLE` |
| `parent_task_id` | `UUID` (FK → tasks.id) | `NULLABLE`, `INDEX`, `ON DELETE SET NULL` |
| `created_at` | `TIMESTAMPTZ` | `server_default=now()` |
| `updated_at` | `TIMESTAMPTZ` | `server_default=now()`, `onupdate=now()` |

**DAG Chain**: `parent_task_id` forms a linked list for escalation tracking.

**Relationships**:
- `raci_assignments` → `RaciAssignment.task` (cascade delete)
- `organization_links` → `TaskOrganization.task` (cascade delete)
- `parent_task` → self-referential (remote_side=[id])

---

### 3.6 `raci_assignments`

**File**: [`src/adapters/db/models/raci.py`](src/adapters/db/models/raci.py)

| Column | Type | Constraints |
|---|---|---|
| `id` | `UUID` (PK) | `default=uuid4` |
| `task_id` | `UUID` (FK → tasks.id) | `NOT NULL`, `INDEX`, `ON DELETE CASCADE` |
| `user_id` | `UUID` (FK → users.id) | `NOT NULL`, `INDEX`, `ON DELETE CASCADE` |
| `role` | `ENUM(RaciRole)` | `NOT NULL` |
| `note` | `VARCHAR(500)` | `NULLABLE` |

**Constraints**:
- `UNIQUE(task_id, user_id, role)` — one user can hold only one role per task
- PostgreSQL TRIGGER: `check_raci_single_accountable()` — enforces exactly 1 `A` role per task at DB level. See migration [`alembic/versions/656a3c5ba51a_add_raci_accountable_constraint.py`](alembic/versions/656a3c5ba51a_add_raci_accountable_constraint.py)

---

### 3.7 `organizations`

**File**: [`src/adapters/db/models/organization.py`](src/adapters/db/models/organization.py)

| Column | Type | Constraints |
|---|---|---|
| `id` | `UUID` (PK) | `default=uuid4` |
| `name` | `VARCHAR(255)` | `NOT NULL` |
| `parent_id` | `UUID` (FK → organizations.id) | `NULLABLE`, `ON DELETE SET NULL` |
| `is_active` | `BOOLEAN` | `DEFAULT TRUE` |
| `created_at` | `TIMESTAMPTZ` | `server_default=now()` |
| `updated_at` | `TIMESTAMPTZ` | `server_default=now()`, `onupdate=now()` |

**Self-referential hierarchy**: `parent_id` enables organizational tree structures.

---

### 3.8 `task_organizations` (Junction)

**File**: [`src/adapters/db/models/task_organization.py`](src/adapters/db/models/task_organization.py)

| Column | Type | Constraints |
|---|---|---|
| `id` | `UUID` (PK) | — |
| `task_id` | `UUID` (FK → tasks.id) | `NOT NULL`, `ON DELETE CASCADE` |
| `organization_id` | `UUID` (FK → organizations.id) | `NOT NULL`, `ON DELETE CASCADE` |

**Constraints**: `UNIQUE(task_id, organization_id)` — many-to-many link

---

### 3.9 `notebooks`

**File**: [`src/adapters/db/models/notebook.py`](src/adapters/db/models/notebook.py)

| Column | Type | Constraints |
|---|---|---|
| `id` | `UUID` (PK) | `default=uuid4` |
| `parent_id` | `UUID` (FK → notebooks.id) | `NULLABLE`, `ON DELETE SET NULL` |
| `name` | `VARCHAR(255)` | `NOT NULL` |
| `path` | `VARCHAR(1000)` | `NOT NULL` (materialized path) |
| `created_at` | `TIMESTAMPTZ` | `server_default=now()` |
| `updated_at` | `TIMESTAMPTZ` | `server_default=now()`, `onupdate=now()` |

**Self-referential hierarchy**: Nested notebook structure with denormalized materialized path (e.g., "Root > Child > Grandchild").

---

### 3.10 `meeting_notebooks` (Junction)

**File**: [`src/adapters/db/models/meeting_notebook.py`](src/adapters/db/models/meeting_notebook.py)

| Column | Type | Constraints |
|---|---|---|
| `meeting_id` | `UUID` (FK → meetings.id) | `NOT NULL`, `ON DELETE CASCADE`, part of composite PK |
| `notebook_id` | `UUID` (FK → notebooks.id) | `NOT NULL`, `ON DELETE CASCADE`, part of composite PK |

**Constraints**: `PRIMARY KEY(meeting_id, notebook_id)`

---

## 4. Base Mixin

**File**: [`src/adapters/db/models/base.py`](src/adapters/db/models/base.py)

`TimestampMixin` adds `created_at` and `updated_at` columns with `server_default=func.now()` to all inheriting models.

---

## 5. Migration History

| Revision ID | Description | File |
|---|---|---|
| `cd9db7ed15ea` | Initial schema — all 10 tables | [`alembic/versions/cd9db7ed15ea_initial_schema.py`](alembic/versions/cd9db7ed15ea_initial_schema.py) |
| `656a3c5ba51a` | RACI single-accountable DB trigger | [`alembic/versions/656a3c5ba51a_add_raci_accountable_constraint.py`](alembic/versions/656a3c5ba51a_add_raci_accountable_constraint.py) |

---

## 6. Async Session

**File**: [`src/infrastructure/database.py`](src/infrastructure/database.py)

- `create_async_engine()` with asyncpg driver, pool_size=20, max_overflow=10
- `async_session_factory` with `expire_on_commit=False`
- `get_async_session()` — FastAPI dependency yielding sessions with commit/rollback