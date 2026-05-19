# Project Context: Meeting Protocol Module

**Platform**: "Book of Good Deeds" (Книга добрых дел)  
**Module**: Meeting Protocol (Протокол совещания)  
**Repository**: [srilankabankg-oss/protokol](https://github.com/srilankabankg-oss/protokol)  
**Status**: All 7 development iterations complete — full-stack MVP

---

## 1. Business Domain

The Meeting Protocol module is the foundational component of the "Book of Good Deeds" ecosystem — an enterprise-grade platform for construction project management, knowledge management, and decision tracking. It replaces isolated text documents and manual data transfer with an intelligent, scalable environment integrating project management best practices, semantically linked nested notebooks, and LLM-powered automation.

### Core Problem
Traditional meeting documentation suffers from:
- **Context loss**: Decisions trapped in isolated files, no cross-referencing
- **Responsibility blur**: No formal accountability tracking beyond meeting minutes
- **Broken traceability**: Inability to track decision chains across organizational levels

### Core Solution
- **Structured protocols**: GOST-compliant three-section format (СЛУШАЛИ / ВЫСТУПИЛИ / ПОСТАНОВИЛИ)
- **RACI matrix**: Every task has formal responsibility assignments enforced at DB level
- **DAG escalation**: Tasks migrate between meeting hierarchies with full traceability
- **AI augmentation**: LLM-powered transcript structuring, task extraction, and risk detection

---

## 2. Meeting Taxonomy

The system enforces a strict 4-level meeting classification derived from construction industry best practices:

| Level | Russian Label | Focus | Typical Participants | Protocol Format |
|---|---|---|---|---|
| **Strategic** | Стратегический | Global vectors, budget approval, critical risk escalation, cross-project conflicts | Owners, sponsors, CEO, directors | Concise decisions, result-focused |
| **Coordination** | Координационный | Project status, resource sync, schedule & budget management | Project managers, chief engineers, stakeholders | Full protocol with detailed justifications |
| **Operational** | Оперативный | Regular standups, sprint planning, blocker resolution | Line managers, supervisors, specialists | Task-focused with concrete deadlines |
| **Situational** | Проблемный | Ad-hoc meetings for specific technical/organizational issues | Cross-functional teams, subject matter experts | Detailed argumentation capture |

Implementation: [`src/core/enums.py`](src/core/enums.py) — `MeetingLevel` enum

---

## 3. RACI Responsibility Matrix

Every task extracted from a protocol is assigned one of four responsibility levels:

| Role | Code | Description | DB Constraint |
|---|---|---|---|
| **Responsible** | R | Executor(s) — person(s) performing the work | Minimum 1 per task |
| **Accountable** | A | Owner — single person with final decision authority | **Exactly 1 per task** (UNIQUE CONSTRAINT + PostgreSQL trigger) |
| **Consulted** | C | Expert — two-way communication before decision | Optional |
| **Informed** | I | Stakeholder — receives status updates | Optional |

### Validation Rules
- **Application level**: `RaciService._validate()` in [`src/adapters/services/raci_service.py`](src/adapters/services/raci_service.py)
- **Database level**: PostgreSQL trigger `check_raci_single_accountable()` in [`alembic/versions/656a3c5ba51a_add_raci_accountable_constraint.py`](alembic/versions/656a3c5ba51a_add_raci_accountable_constraint.py)
- **Self-correction**: If 2+ Accountable roles are submitted, extra A's are auto-demoted to R (Responsible)

---

## 4. Protocol Lifecycle (State Machine)

```
PREPARATION → IN_PROGRESS → ON_APPROVAL → APPROVED (read-only)
```

| Phase | Who | What Happens |
|---|---|---|
| **Phase 1: Preparation** | Secretary + Responsible users | System auto-scans for unfinished tasks from past meetings ("tails") and imports them. Responsible users update statuses before the meeting. |
| **Phase 2: Live Recording** | Secretary | Active editing in the intelligent editor. AI assistant analyzes audio, suggests tasks and formulations. Markdown content autosaves every 3 seconds. |
| **Phase 3: Approval** | Chairman | Black-and-white comparison (original vs AI-edited). Final RACI matrix review. Escalation decisions. Protocol goes read-only and triggers PDF/XLSX export + notifications. |

Implementation: [`src/adapters/services/meeting_service.py`](src/adapters/services/meeting_service.py) — `finalize_meeting()`, `approve_meeting()`

---

## 5. Task Escalation (DAG Migration)

Tasks can migrate between meeting hierarchy levels via a Directed Acyclic Graph (DAG):

```
Operational meeting task → [ESCALATE] → Coordination meeting task → [ESCALATE] → Strategic meeting task
```

### Escalation Rules
1. Source task status changes to `ESCALATED`
2. Destination task created with `parent_task_id` linking back (DAG edge)
3. Former Accountable becomes Responsible on the new level
4. New Accountable is the decision-maker at the target meeting level

Implementation: [`src/adapters/services/task_service.py`](src/adapters/services/task_service.py) — `escalate_task()`

---

## 6. AI Integration

Two LLM agents operate on the meeting content pipeline:

| Agent | System Prompt Location | Function |
|---|---|---|
| **Summary Agent** | [`src/infrastructure/llm_gateway.py`](src/infrastructure/llm_gateway.py) — `SUMMARY_AGENT_PROMPT` | Raw transcript → Structured Markdown (СЛУШАЛИ / ВЫСТУПИЛИ / ПОСТАНОВИЛИ) + risk detection |
| **Task Extraction Agent** | [`src/infrastructure/llm_gateway.py`](src/infrastructure/llm_gateway.py) — `TASK_EXTRACTION_AGENT_PROMPT` | Markdown → Action items with RACI assignments + confidence scores |

### Fallback Strategy (4 levels, per specification)
1. **JSON Parsing**: Regex extraction if LLM wraps JSON in markdown fences
2. **Self-Correction Loop**: Up to 2 retries with `temperature=0.0` and error-aware prompts
3. **Programmatic Fix**: `RaciService._auto_correct_assignments()` for RACI violations
4. **Graceful Degradation**: Empty insights returned on total failure — system never crashes

Implementation: [`src/infrastructure/llm_gateway.py`](src/infrastructure/llm_gateway.py) — `structured_output()`

---

## 7. Authorization Model (RBAC)

| Role | Meeting Permissions | Task Permissions | Special Rights |
|---|---|---|---|
| **Secretary** | CRUD text content, finalize meeting | Create tasks | Cannot approve meetings |
| **Chairman** | Read workspace | Escalate tasks, edit RACI | Exclusive right to approve meetings |
| **Admin** | Full CRUD | All operations | LLM Gateway config, global references |
| **User** (Responsible) | Pre-meeting status updates only | View assigned tasks | Blocked from live editor during meetings |

Implementation: [`src/infrastructure/dependencies.py`](src/infrastructure/dependencies.py) — `require_role()`, `require_user()`

---

## 8. Development History

| Iteration | Scope | Key Deliverables |
|---|---|---|
| **1** | Foundation | FastAPI project, 10 SQLAlchemy models, Docker (PostgreSQL 16 + Redis 7), Alembic migrations, CI/CD pipeline |
| **2** | Backend API | 13 CRUD endpoints, state machine, task numbering (KDD-XXX-NNN), JWT auth with bcrypt |
| **3** | RACI Matrix | `RaciService` with validation, DB-level trigger, self-correction, 422 error responses |
| **4** | AI Infrastructure | LLM Gateway (StepFun/OpenRouter/Gemini), Summary + Task Extraction agents, JSON schema enforcement, fallback chain |
| **5** | Frontend | React 18 + Vite + Tailwind, Dashboard, Intelligent Editor (autosave), AI Panel, Zustand stores |
| **6** | RACI UI | Interactive RACI grid, Task detail modal, Escalation panel, DependencyChain DAG visualization |
| **7** | Finalize & Export | PDF (ReportLab) + XLSX (openpyxl) generation, download endpoints, Approval stepper, Read-only enforcement |

---

## 9. Key Architecture Decisions

- **Clean Architecture**: `core/` (domain) → `adapters/` (DB, API) → `infrastructure/` (config, auth)
- **Async PostgreSQL**: SQLAlchemy 2.0 async with asyncpg driver
- **JWT Authentication**: Access tokens (15 min) + Refresh tokens (7 days), HttpOnly cookies
- **Task Queue**: Celery with Redis broker for bulk notifications, PDF/XLSX export
- **Nested Notebooks**: Self-referential `notebooks` table supporting hierarchical organization structures (materialized paths)
- **Dual Validation**: Application-level (RaciService) + Database-level (PostgreSQL trigger) for data integrity

---

## 10. Related Documents

- [Architecture Stack](./ARCHITECTURE_STACK.md)
- [Database Schema](./DATABASE_SCHEMA.md)
- [API Contracts](./API_CONTRACTS.md)
- [AI Services](./AI_SERVICES.md)
- [UI Components](./UI_COMPONENTS.md)
- [Roadmap State](./ROADMAP_STATE.md)
- [AI Instructions](./AI_INSTRUCTIONS.md)
- [QA Test Plan](./QA_TEST_PLAN.md)