# AGENTS.md — System Rules for AI Agents

> **MANDATORY READING** for any AI agent operating on this repository.

---

## RULE 1: Context Synchronization

**Every session/task MUST start with full context refresh.**

Read the following files in order before ANY action:
1. [`docs/README_CONTEXT.md`](docs/README_CONTEXT.md)
2. [`docs/DATABASE_SCHEMA.md`](docs/DATABASE_SCHEMA.md)
3. [`docs/API_CONTRACTS.md`](docs/API_CONTRACTS.md)
4. [`docs/AI_SERVICES.md`](docs/AI_SERVICES.md)
5. [`docs/UI_COMPONENTS.md`](docs/UI_COMPONENTS.md)
6. [`docs/ROADMAP_STATE.md`](docs/ROADMAP_STATE.md)
7. [`docs/AI_INSTRUCTIONS.md`](docs/AI_INSTRUCTIONS.md)
8. [`docs/QA_TEST_PLAN.md`](docs/QA_TEST_PLAN.md)

---

## RULE 2: QA Mandate

**Any code modification requires a QA report.**

After ANY code change:
1. Read [`docs/QA_TEST_PLAN.md`](docs/QA_TEST_PLAN.md)
2. Execute or emulate relevant tests
3. Generate report: `docs/qa/QA_REPORT_{YYYY-MM-DD}_{TASK_ID}.md`
4. Report must include: changes made, test results, errors (if any), verdict (PASSED/FAILED)

---

## RULE 3: Maintenance

**Any logic change triggers documentation updates.**

| Change | Must Update |
|---|---|
| New/changed endpoint | `docs/API_CONTRACTS.md` |
| New/changed DB model | `docs/DATABASE_SCHEMA.md` |
| New/changed AI agent | `docs/AI_SERVICES.md` |
| New/changed UI component | `docs/UI_COMPONENTS.md` |
| Feature completed | `docs/ROADMAP_STATE.md` |
| New test scenario | `docs/QA_TEST_PLAN.md` |

---

## RULE 4: Schema Synchronization

Pydantic schemas (`src/adapters/api/schemas/`), SQLAlchemy models (`src/adapters/db/models/`), and TypeScript types (`frontend/src/types/`) must ALWAYS match. Changing one requires updating the others.

---

## RULE 5: RACI Invariant

Every task MUST have **exactly 1 Accountable (A)**. Enforced at both application and database levels. NEVER bypass.

---

## RULE 6: State Machine

Meeting lifecycle: `PREPARATION → IN_PROGRESS → ON_APPROVAL → APPROVED`. Never skip or reverse transitions.

---

## RULE 7: Commit Convention

Use [Conventional Commits](https://www.conventionalcommits.org/): `feat:`, `fix:`, `chore:`, `docs:`, `refactor:`.

---

## RULE 8: Environment Variables

Never hardcode secrets or configuration. See [`.env.example`](.env.example) for all required variables.

---

## RULE 9: Clean Architecture

| Layer | Directory | Purpose |
|---|---|---|
| Domain | `src/core/` | Enums, types — no DB/HTTP deps |
| Adapters | `src/adapters/` | DB models, API routes, schemas, services |
| Infrastructure | `src/infrastructure/` | Config, auth, Celery, LLM client |
| Frontend | `frontend/src/` | React components, stores, API client |

Never put business logic in routes. Never put HTTP in services.

---

## RULE 10: Documentation Language

All documentation in `docs/` is in **English**. `README.md` overview is in **Russian** with an English AI section.
## RULE 11: Post-Task QA Mandate

**MANDATORY after every task completion:**
1. Write PyTests covering new/modified functionality
2. Add tester scenarios in the designated test file
3. Update the project changelog (`docs/CHANGELOG.md`)
4. Run the test suite and verify all tests pass
