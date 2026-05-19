# AI Instructions: Rules for Future LLM Agents

This document is a **mandatory read** for any AI agent (LLM, coding assistant, or autonomous worker) operating on this repository. Violating these rules will cause integration failures.

---

## Rule 1: Context Synchronization (MANDATORY)

**Every session/task MUST start with a full context refresh.**

Before any code modification, analysis, or documentation update:

1. Read [`docs/README_CONTEXT.md`](docs/README_CONTEXT.md) — business domain, RACI rules, meeting levels
2. Read [`docs/ARCHITECTURE_STACK.md`](docs/ARCHITECTURE_STACK.md) — tech stack, dependencies, infrastructure
3. Read [`docs/DATABASE_SCHEMA.md`](docs/DATABASE_SCHEMA.md) — all 10 tables, constraints, enums
4. Read [`docs/API_CONTRACTS.md`](docs/API_CONTRACTS.md) — all 22 endpoints, RBAC matrix, JSON payloads
5. Read [`docs/AI_SERVICES.md`](docs/AI_SERVICES.md) — LLM gateway, agent prompts, JSON schemas
6. Read [`docs/UI_COMPONENTS.md`](docs/UI_COMPONENTS.md) — screen map, component tree, states
7. Read [`docs/ROADMAP_STATE.md`](docs/ROADMAP_STATE.md) — what's done, what's planned
8. Read [`docs/QA_TEST_PLAN.md`](docs/QA_TEST_PLAN.md) — test scenarios for the affected area

**Without this, your code will not match existing patterns and will be rejected.**

---

## Rule 2: QA Mandate (MANDATORY)

**Any code modification requires a QA report.**

After ANY code change (even a single line):

1. Read [`docs/QA_TEST_PLAN.md`](docs/QA_TEST_PLAN.md)
2. Identify the affected test scenarios
3. Execute or emulate the relevant tests
4. Generate a report: `docs/qa/QA_REPORT_{YYYY-MM-DD}_{TASK_ID}.md`

Report format:
```markdown
# QA Report — {date} — {task description}

## Changes Made
- File: {path}, Line: {range}, Change: {description}

## Affected Test Scenarios
- [ ] Scenario 1: {name} → Result: {PASSED/FAILED}
- [ ] Scenario 2: {name} → Result: {PASSED/FAILED}

## Errors (if any)
{error logs}

## Verdict
{PASSED / FAILED — if FAILED, what needs to be fixed}
```

---

## Rule 3: Schema Consistency (MANDATORY)

**Pydantic schemas, SQLAlchemy models, and TypeScript types must stay synchronized.**

If you modify any of these:
- `src/adapters/api/schemas/*.py` (Pydantic)
- `src/adapters/db/models/*.py` (SQLAlchemy)
- `frontend/src/types/index.ts` (TypeScript)

You MUST update the other two to match. A field added to the DB model needs a Pydantic schema update and a TypeScript type update.

---

## Rule 4: Documentation Updates (MANDATORY)

**Any logic change triggers documentation updates.**

| Change Type | Must Update |
|---|---|
| New endpoint or changed response schema | `docs/API_CONTRACTS.md` |
| New/changed DB model, column, constraint | `docs/DATABASE_SCHEMA.md` |
| New/changed AI agent or LLM config | `docs/AI_SERVICES.md` |
| New/changed UI component or screen | `docs/UI_COMPONENTS.md` |
| New feature completed | `docs/ROADMAP_STATE.md` (mark ✅) |
| New business rule or domain logic | `docs/README_CONTEXT.md` |
| New test scenario or regression case | `docs/QA_TEST_PLAN.md` |

---

## Rule 5: Enum-Driven Logic

All categorical values use Python `Enum` classes defined in [`src/core/enums.py`](src/core/enums.py):
- `UserRole`, `MeetingLevel`, `MeetingStatus`, `WorkflowStage`, `RaciRole`, `ParticipantRole`

When adding a new value to an enum, you MUST:
1. Add it to `src/core/enums.py`
2. Add the corresponding Alembic migration if it affects DB columns
3. Update all Pydantic Literal types in schemas
4. Update TypeScript union types in `frontend/src/types/index.ts`
5. Update UI constants (labels, colors) in relevant components

---

## Rule 6: State Machine Integrity

The meeting lifecycle follows a strict state machine:
```
PREPARATION → IN_PROGRESS → ON_APPROVAL → APPROVED
```

Never skip states. Never reverse transitions (APPROVED → IN_PROGRESS).  
Implementation: [`src/adapters/services/meeting_service.py`](src/adapters/services/meeting_service.py) — `finalize_meeting()`, `approve_meeting()`

---

## Rule 7: RACI Invariant (CRITICAL)

**Every task MUST have exactly 1 Accountable (A).**

This is enforced at two levels:
- **Application**: [`src/adapters/services/raci_service.py`](src/adapters/services/raci_service.py) — `_validate()`
- **Database**: [`alembic/versions/656a3c5ba51a_add_raci_accountable_constraint.py`](alembic/versions/656a3c5ba51a_add_raci_accountable_constraint.py) — PostgreSQL trigger

Never remove or bypass this constraint.

---

## Rule 8: Commit Convention

Use [Conventional Commits](https://www.conventionalcommits.org/):
- `feat:` — new feature
- `fix:` — bug fix
- `chore:` — maintenance, config
- `docs:` — documentation
- `refactor:` — code restructuring without behavior change

---

## Rule 9: Environment Variables

All secrets and configuration come from environment variables. Never hardcode:

| Variable | Used In |
|---|---|
| `DATABASE_URL` | `src/infrastructure/database.py` |
| `REDIS_URL` | `src/infrastructure/celery_app.py` |
| `SECRET_KEY` | `src/infrastructure/auth.py` |
| `STEPFUN_API_KEY` | `src/infrastructure/llm_gateway.py` |
| `LLM_BASE_URL`, `LLM_MODEL` | `src/infrastructure/llm_gateway.py` |

Template: [`.env.example`](.env.example)

---

## Rule 10: File Organization

| Directory | Purpose |
|---|---|
| `src/core/` | Domain enums, shared types — no DB or HTTP dependencies |
| `src/adapters/db/models/` | SQLAlchemy ORM models — DB schema only |
| `src/adapters/api/routes/` | FastAPI route handlers — HTTP layer only |
| `src/adapters/api/schemas/` | Pydantic request/response models — validation |
| `src/adapters/services/` | Business logic — independent of HTTP/DB details |
| `src/infrastructure/` | Config, auth, DB session, Celery, LLM client |
| `frontend/src/` | React components, stores, API client |
| `docs/` | All documentation (this file's siblings) |
| `docs/qa/` | QA reports — one per task |
| `alembic/` | Database migrations |
| `tests/` | Backend test suite |

Never put business logic in route handlers. Never put HTTP concerns in services. Follow Clean Architecture layering.