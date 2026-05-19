# Architecture Stack: Meeting Protocol Module

## 1. Technology Stack

### Backend
| Layer | Technology | Version | Purpose |
|---|---|---|---|
| Framework | FastAPI | 0.115+ | Async REST API, OpenAPI docs |
| ASGI Server | Uvicorn | 0.34+ | Production server with hot reload |
| ORM | SQLAlchemy | 2.0+ (async) | Async PostgreSQL access |
| DB Driver | asyncpg | 0.30+ | High-performance PostgreSQL driver |
| Migrations | Alembic | 1.14+ | Schema versioning |
| Validation | Pydantic | 2.10+ | Request/response schemas |
| Config | pydantic-settings | 2.7+ | Environment-based configuration |
| Auth (JWT) | python-jose | 3.3+ | Token generation and verification |
| Auth (hash) | bcrypt | 4.2+ | Password hashing |
| Task Queue | Celery | 5.4+ | Async job processing |
| Message Broker | Redis | 7 | Celery backend + broker |
| HTTP Client | httpx | 0.28+ | Async LLM API calls |
| PDF Export | ReportLab | 4.2+ | PDF protocol generation |
| XLSX Export | openpyxl | 3.1+ | Excel report generation |
| Email Validation | email-validator | 2.2+ | Pydantic EmailStr support |

### Frontend
| Layer | Technology | Version | Purpose |
|---|---|---|---|
| UI Library | React | 18.3 | Component-based SPA |
| Build Tool | Vite | 5.4 | Fast dev server + production builds |
| Language | TypeScript | 5.5 | Static typing |
| Styling | Tailwind CSS | 3.4 | Utility-first CSS |
| Components | Headless UI | 2.2 | Accessible unstyled components |
| Icons | Heroicons | 2.2 | SVG icon library |
| HTTP Client | Axios | 1.7 | API calls with interceptors |
| State | Zustand | 4.5 | Lightweight state management |
| Routing | React Router DOM | 6.26 | Client-side navigation |
| Dates | date-fns | 3.6 | Date formatting (Russian locale) |

### Infrastructure
| Component | Technology | Purpose |
|---|---|---|
| Database | PostgreSQL 16 (Alpine) | Primary data store |
| Cache/Broker | Redis 7 (Alpine) | Celery message broker |
| Containerization | Docker + Docker Compose | Local development environment |
| CI/CD | GitHub Actions | Linting, type checking, testing |
| Python Env | venv / Poetry | Dependency management |

### Dev Tools
| Tool | Config | Purpose |
|---|---|---|
| ruff | `pyproject.toml` [tool.ruff] | Fast Python linter |
| black | `pyproject.toml` | Code formatter (line-length=100) |
| mypy | `pyproject.toml` [tool.mypy] | Static type checking (strict) |
| pytest | `pyproject.toml` [tool.pytest] | Test runner (asyncio_mode=auto) |
| pre-commit | `.pre-commit-config.yaml` | Git hooks (ruff, mypy) |

---

## 2. Project Structure

```
protokol/
├── src/
│   ├── core/                          # Domain layer — no infrastructure deps
│   │   ├── enums.py                   # UserRole, MeetingLevel, MeetingStatus,
│   │   │                              #   WorkflowStage, RaciRole, ParticipantRole
│   │   └── entities/                  # (reserved for domain entities)
│   │
│   ├── adapters/                      # Interface adapters (Clean Architecture)
│   │   ├── db/
│   │   │   └── models/                # SQLAlchemy 2.0 ORM models
│   │   │       ├── base.py            # DeclarativeBase + TimestampMixin
│   │   │       ├── user.py            # User (6 fields + RACI rel)
│   │   │       ├── meeting.py         # Meeting (11 fields)
│   │   │       ├── participant.py     # MeetingParticipant (junction)
│   │   │       ├── agenda.py          # AgendaItem
│   │   │       ├── task.py            # Task (DAG via parent_task_id)
│   │   │       ├── raci.py            # RaciAssignment (R/A/C/I)
│   │   │       ├── task_organization.py  # Task↔Org (junction)
│   │   │       ├── organization.py    # Organization (self-ref tree)
│   │   │       ├── notebook.py        # Notebook (self-ref tree + materialized path)
│   │   │       └── meeting_notebook.py   # Meeting↔Notebook (junction)
│   │   │
│   │   ├── api/
│   │   │   ├── routes/                # FastAPI route handlers
│   │   │   │   ├── auth.py            # POST register, login
│   │   │   │   ├── meetings.py        # 8 meeting endpoints
│   │   │   │   ├── tasks.py           # 5 task endpoints
│   │   │   │   └── ai.py              # 2 AI endpoints
│   │   │   └── schemas/               # Pydantic v2 request/response models
│   │   │       ├── common.py          # ErrorResponse, PaginatedResponse
│   │   │       ├── user.py            # UserCreate, LoginRequest, TokenResponse
│   │   │       ├── meeting.py         # MeetingCreate, Workspace, Approve
│   │   │       ├── task.py            # TaskCreate, RaciUpdate, Escalate
│   │   │       ├── ai.py              # AudioChunk, AIInsights
│   │   │       └── notebook.py        # NotebookCreate/Response
│   │   │
│   │   └── services/                  # Business logic layer
│   │       ├── meeting_service.py     # CRUD, state machine, tail import
│   │       ├── task_service.py        # Task numbering, escalation, deps
│   │       ├── raci_service.py        # Validation, self-correction, update
│   │       ├── ai_service.py          # LLM agent orchestration
│   │       └── export_service.py      # PDF + XLSX generation
│   │
│   ├── infrastructure/                # Cross-cutting concerns
│   │   ├── config.py                  # Settings (pydantic-settings, .env)
│   │   ├── database.py                # Async engine, session factory
│   │   ├── auth.py                    # bcrypt hash, JWT create/decode
│   │   ├── dependencies.py            # RBAC: require_user, require_role
│   │   ├── celery_app.py              # Celery instance + export/notify tasks
│   │   └── llm_gateway.py             # LLM provider client + system prompts
│   │
│   └── main.py                        # FastAPI app, routers, CORS, health
│
├── frontend/                          # React SPA (separate Vite project)
│   └── src/
│       ├── api/client.ts              # Axios + JWT interceptor
│       ├── types/index.ts             # TS interfaces matching Pydantic
│       ├── store/
│       │   ├── meetingStore.ts        # Zustand: autosave, content
│       │   └── authStore.ts           # Zustand: login, token
│       ├── pages/
│       │   ├── Dashboard.tsx          # Meeting list + filters
│       │   ├── MeetingEditor.tsx      # 3-column editor + AI panel
│       │   └── Login.tsx              # Auth form
│       └── components/
│           ├── ai/AIPanel.tsx         # AI insights (tasks, risks)
│           ├── raci/RACIGrid.tsx      # Interactive RACI table
│           ├── tasks/
│           │   ├── TaskDetailModal.tsx # RACI + escalate panel
│           │   └── DependencyChain.tsx # DAG visualization
│           └── ui/
│               ├── ApprovalStepper.tsx # 4-step progress
│               └── ExportButtons.tsx   # PDF/XLSX download
│
├── alembic/                           # Database migrations
│   ├── env.py                         # Async migration runner
│   └── versions/
│       ├── cd9db7ed15ea_initial_schema.py     # All 10 tables
│       └── 656a3c5ba51a_add_raci_constraint.py # RACI DB trigger
│
├── docs/                              # Technical documentation
│   ├── README_CONTEXT.md
│   ├── ARCHITECTURE_STACK.md          # (this file)
│   ├── DATABASE_SCHEMA.md
│   ├── API_CONTRACTS.md
│   ├── AI_SERVICES.md
│   ├── UI_COMPONENTS.md
│   ├── ROADMAP_STATE.md
│   ├── AI_INSTRUCTIONS.md
│   ├── QA_TEST_PLAN.md
│   └── qa/                            # QA reports directory
│
├── tests/                             # Backend test suite
│   ├── conftest.py                    # pytest-asyncio fixtures
│   └── __init__.py
│
├── AGENTS.md                          # Rules for AI agents
├── README.md                          # Project overview (RU + EN)
├── pyproject.toml                     # Poetry config + tool settings
├── requirements.txt                   # Pip dependencies
├── docker-compose.yml                 # PostgreSQL 16 + Redis 7 + app
├── Dockerfile                         # Python 3.12-slim
├── .env.example                       # Environment template
├── .gitignore
├── .pre-commit-config.yaml
└── .github/workflows/ci.yml           # CI pipeline (lint → type → test)
```

---

## 3. Clean Architecture Layers

```
┌─────────────────────────────────────┐
│         API Routes (FastAPI)        │  ← HTTP concerns only
├─────────────────────────────────────┤
│      Pydantic Schemas               │  ← Validation, serialization
├─────────────────────────────────────┤
│      Services (Business Logic)      │  ← No HTTP/DB framework deps
├─────────────────────────────────────┤
│   Adapters (SQLAlchemy Models)      │  ← DB schema mapping
├─────────────────────────────────────┤
│   Infrastructure (Config, Auth)     │  ← Cross-cutting
└─────────────────────────────────────┘
```

**Rule**: Dependencies point inward. Routes depend on services. Services depend on models. Models depend on enums (core). No layer depends on a higher layer.

---

## 4. Data Flow

### Create Meeting Flow
```
Frontend (Dashboard.tsx)
  → POST /api/v1/meetings (MeetingCreate payload)
  → meetings.py: create_meeting()
  → meeting_service.create_meeting()
    → Creates Meeting + AgendaItem records
    → _import_legacy_tasks() scans for unfinished tasks
    → Returns (meeting, imported_count)
  → Celery: send_notifications_task.delay()
  → 201 {meeting_id, status, imported_legacy_tasks_count}
```

### Autosave Flow
```
Frontend (MeetingEditor.tsx)
  → User types in textarea
  → meetingStore.setContent() → isDirty = true
  → Timer: every 3 seconds
  → meetingStore.saveContent()
  → PATCH /api/v1/meetings/{id}/content
  → meeting_service.update_meeting_content()
    → Updates content_markdown, increments version
  → 200 {status: "success", version: N}
  → meetingStore.isDirty = false
```

### AI Insights Flow
```
Frontend (AIPanel.tsx)
  → Timer: every 10 seconds
  → GET /api/v1/meetings/{id}/ai-insights
  → ai.py: get_ai_insights()
  → AIService.generate_insights()
    → Summary Agent: transcript → structured Markdown + risks
    → Task Extraction Agent: Markdown → tasks with RACI
  → 200 {suggested_action_items, detected_risks}
```

### Approval Flow
```
Chairman clicks "Утвердить"
  → POST /api/v1/meetings/{id}/approve
  → meetings.py: approve()
  → meeting_service.approve_meeting()
    → Validates status == on_approval
    → Changes status → approved
  → Celery: export_pdf_task.delay() + export_xlsx_task.delay()
  → Celery: send_notifications_task.delay()
  → 200 {status: "approved", pdf_export_job_id, xlsx_export_job_id}
```

---

## 5. Network & Ports

| Service | Port | Access |
|---|---|---|
| FastAPI Backend | 8000 | Internal (Vite proxy) + Docker |
| Vite Dev Server | 5173 | Localhost only |
| PostgreSQL | 5432 | Docker internal + localhost |
| Redis | 6379 | Docker internal + localhost |
| LLM API (StepFun) | 443 | Outbound HTTPS |

---

## 6. Configuration

All settings via environment variables, loaded by [`src/infrastructure/config.py`](src/infrastructure/config.py) using `pydantic-settings.BaseSettings`:

| Setting | Default | Purpose |
|---|---|---|
| `DATABASE_URL` | `postgresql+asyncpg://protokol:protokol_secret@localhost:5432/protokol` | Async DB connection |
| `DATABASE_URL_SYNC` | `postgresql://...` | Sync DB (Alembic) |
| `REDIS_URL` | `redis://localhost:6379/0` | Celery broker |
| `SECRET_KEY` | `dev-secret-key-change-in-production` | JWT signing key |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | 15 | JWT access token TTL |
| `REFRESH_TOKEN_EXPIRE_DAYS` | 7 | JWT refresh token TTL |
| `LLM_BASE_URL` | `https://api.stepfun.com/step_plan/v1` | LLM API endpoint |
| `LLM_MODEL` | `step-router-v1` | Default model |
| `LLM_API_KEY` | (from env) | API key (never committed) |
| `LLM_TIMEOUT` | 180 | Request timeout (seconds) |