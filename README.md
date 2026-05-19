# Протокол — Модуль «Протокол совещания»

**Платформа**: Книга добрых дел  
**Статус**: MVP — 7 итераций завершены  
**Стек**: FastAPI + React 18 + PostgreSQL 16 + Redis 7

---

## О проекте

Интеллектуальный модуль протоколирования совещаний для платформы управления строительными проектами «Книга добрых дел». Обеспечивает структурированное ведение протоколов по ГОСТ (СЛУШАЛИ / ВЫСТУПИЛИ / ПОСТАНОВИЛИ), матрицу ответственности RACI, эскалацию задач между уровнями управления и ИИ-помощника для автоматического структурирования текста и извлечения поручений.

### Ключевые возможности

- **4 уровня совещаний**: Стратегический, Координационный, Оперативный, Проблемный
- **RACI матрица**: Строгая валидация (ровно 1 Accountable) на уровне приложения и БД
- **DAG эскалация**: Миграция задач между уровнями с полной отслеживаемостью
- **ИИ-агенты**: Суммаризация транскриптов и извлечение задач с RACI
- **Автосохранение**: Текст протокола сохраняется каждые 3 секунды
- **Экспорт**: PDF (ReportLab) и Excel (openpyxl)
- **RBAC**: 4 роли (admin, secretary, chairman, user) с разделением прав

---

## Документация

| Документ | Описание |
|---|---|
| [README_CONTEXT.md](./docs/README_CONTEXT.md) | Бизнес-логика, RACI, уровни совещаний |
| [ARCHITECTURE_STACK.md](./docs/ARCHITECTURE_STACK.md) | Технический стек и инфраструктура |
| [DATABASE_SCHEMA.md](./docs/DATABASE_SCHEMA.md) | 10 таблиц, связи, ограничения |
| [API_CONTRACTS.md](./docs/API_CONTRACTS.md) | 22 эндпоинта, RBAC матрица, JSON схемы |
| [AI_SERVICES.md](./docs/AI_SERVICES.md) | LLM Gateway, агенты, промпты |
| [UI_COMPONENTS.md](./docs/UI_COMPONENTS.md) | Карта экранов, дерево компонентов |
| [ROADMAP_STATE.md](./docs/ROADMAP_STATE.md) | Прогресс разработки, планы |
| [AI_INSTRUCTIONS.md](./docs/AI_INSTRUCTIONS.md) | Правила для будущих AI-агентов |
| [QA_TEST_PLAN.md](./docs/QA_TEST_PLAN.md) | Критические пути, сценарии, регресс |

---

## Быстрый старт

### Бэкенд
```bash
cp .env.example .env          # Настроить переменные окружения
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
docker-compose up -d postgres redis  # Поднять БД и Redis
alembic upgrade head           # Применить миграции
uvicorn src.main:app --reload  # Запустить API на :8000
```

### Фронтенд
```bash
cd frontend
npm install
npm run dev                    # Запустить на :5173
```

---

## Структура проекта

```
protokol/
├── src/
│   ├── core/                  # Доменные enum'ы
│   ├── adapters/
│   │   ├── db/models/         # SQLAlchemy модели (10 таблиц)
│   │   ├── api/routes/        # FastAPI эндпоинты (22 шт.)
│   │   ├── api/schemas/       # Pydantic v2 схемы
│   │   └── services/          # Бизнес-логика
│   └── infrastructure/        # Конфиг, auth, Celery, LLM
├── frontend/                  # React 18 + Vite + Tailwind
│   └── src/
│       ├── pages/             # Dashboard, Editor, Login
│       ├── components/        # AI, RACI, Tasks, UI
│       ├── store/             # Zustand (meeting, auth)
│       ├── api/               # Axios клиент
│       └── types/             # TypeScript типы
├── alembic/                   # Миграции БД
├── docs/                      # Документация
│   └── qa/                    # QA отчёты
├── tests/                     # Тесты
├── docker-compose.yml         # PostgreSQL 16 + Redis 7
└── .github/workflows/ci.yml   # CI/CD пайплайн
```

---

## FOR AI DEVELOPERS (AI AGENTS)

- **MANDATORY**: Read all files in [`docs/`](docs/) before any code modification. Start with [`AI_INSTRUCTIONS.md`](docs/AI_INSTRUCTIONS.md).
- **QA PROTOCOL**: Every code modification MUST be accompanied by a generated `QA_REPORT` saved in [`docs/qa/`](docs/qa/). Use the naming pattern `QA_REPORT_{YYYY-MM-DD}_{TASK_ID}.md`.
- **DOCUMENTATION**: All technical specs must be kept updated. If you change logic, update the corresponding doc file.
- **RACI INVARIANT**: Every task MUST have exactly 1 Accountable (A). This is enforced at DB level via PostgreSQL trigger.
- **STATE MACHINE**: Meeting lifecycle is `PREPARATION → IN_PROGRESS → ON_APPROVAL → APPROVED`. Never skip or reverse.
- **COMMITS**: Use [Conventional Commits](https://www.conventionalcommits.org/) format.
- **ENV**: Never hardcode secrets. See [`.env.example`](.env.example).

---

**Repository**: [srilankabankg-oss/protokol](https://github.com/srilankabankg-oss/protokol)  
**License**: Proprietary