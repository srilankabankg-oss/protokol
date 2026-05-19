# UI Components: Meeting Protocol Module

**Framework**: React 18 + TypeScript + Vite  
**Styling**: Tailwind CSS 3 + Headless UI  
**State**: Zustand stores  
**Source**: [`frontend/src/`](frontend/src/)

---

## 1. Screen Map

```
/login ───► / (Dashboard) ───► /meetings/:id (Editor)
```

| Screen | Route | Component | Description |
|---|---|---|---|
| Login | `/login` | [`pages/Login.tsx`](frontend/src/pages/Login.tsx) | Email + password form, JWT auth, error display |
| Dashboard | `/` | [`pages/Dashboard.tsx`](frontend/src/pages/Dashboard.tsx) | Meeting card grid, level filter, create button |
| Editor | `/meetings/:id` | [`pages/MeetingEditor.tsx`](frontend/src/pages/MeetingEditor.tsx) | 3-column intelligent editor with AI panel |

---

## 2. Dashboard (`/`)

**Component**: [`frontend/src/pages/Dashboard.tsx`](frontend/src/pages/Dashboard.tsx)

```
┌──────────────────────────────────────────────────────┐
│ Центр управления совещаниями                          │
│ Книга добрых дел                                     │
├──────────────────────────────────────────────────────┤
│ [Все уровни ▼]                    [+ Создать]        │
├──────────────────────────────────────────────────────┤
│ ┌──────────┐  ┌──────────┐  ┌──────────┐            │
│ │[Оператив.]│  │[Стратег.] │  │[Координ.] │           │
│ │Оперативка │  │Упр. комит│  │Ревью №3   │           │
│ │В процессе │  │Утверждено│  │На соглас. │           │
│ │19.05.2026 │  │18.05.2026│  │17.05.2026 │           │
│ └──────────┘  └──────────┘  └──────────┘            │
└──────────────────────────────────────────────────────┘
```

### States
| State | Behavior |
|---|---|
| **Loading** | 3 skeleton cards with `animate-pulse` |
| **Empty** | "Нет совещаний" message + create prompt |
| **Error** | Red alert box with "Повторить" button |

### Color-coded Level Badges
| Level | Badge Color |
|---|---|
| `strategic` | `bg-amber-100 text-amber-800` |
| `coordination` | `bg-purple-100 text-purple-800` |
| `operational` | `bg-blue-100 text-blue-800` |
| `situational` | `bg-red-100 text-red-800` |

---

## 3. Meeting Editor (`/meetings/:id`) — Screen 3

**Component**: [`frontend/src/pages/MeetingEditor.tsx`](frontend/src/pages/MeetingEditor.tsx)

```
┌──────────────────────────────────────────────────────────────────┐
│ Книга › Объект Север › Оперативка №26    [В процессе] [PDF][XLSX]│
├──────────────────────────────────────────────────────────────────┤
│ ✓ Подготовка ─ ✓ Ведение ─ ● Согласование ─ ○ Утверждено       │
├──────────┬───────────────────────────┬───────────────────────────┤
│ LEFT     │ CENTER                    │ RIGHT (AI Panel)          │
│ 280px    │ flex-1                    │ 380px                     │
│          │                           │                           │
│ Участники│ ## СЛУШАЛИ                │ 🤖 ИИ-Ассистент           │
│ ● Иванов │ Доклад по объекту...       │                           │
│ ● Петров │                           │ 💡 Задачи (3)             │
│          │ ## ВЫСТУПИЛИ               │ Закупить кран [94%][+Доб] │
│ Повестка │ Иванов: задержка...        │ График работ [87%][+Доб]  │
│ 1. Блок- │                           │                           │
│    ки    │ ## ПОСТАНОВИЛИ             │ ⚠️ Риски (1)              │
│ 2. Сроки │ Закупить кран до пятницы   │ █ CRITICAL: Дефицит      │
│          │                           │   ресурсов               │
│ Задачи   │                           │                           │
│ ●─●──●   │                           │ 🎙 Транскрипт             │
│          │                           │ Speaker 0: текст...       │
├──────────┴───────────────────────────┴───────────────────────────┤
│ ● Не сохранено                          версия 12               │
└──────────────────────────────────────────────────────────────────┘
```

### 3.1 Sticky Header
- Breadcrumbs from `meeting.breadcrumbs`
- Status badge (color-coded by `MeetingStatus`)
- **[PDF]** + **[Excel]** export buttons → `ExportButtons` component
- **[Завершить]** (secretary, when `in_progress`) → transitions to `on_approval`
- **[Утвердить]** (chairman, when `on_approval`) → transitions to `approved`

### 3.2 Left Sidebar

#### Participants Widget
**Component**: Inline in `MeetingEditor.tsx`
- Green dot: present (`is_present=true`)
- Red dot: absent
- Role badges: `chairman` (amber), `secretary` (blue), `participant` (gray)

#### Agenda Widget
**Component**: Inline in `MeetingEditor.tsx`
- Numbered list from `meeting.agenda`
- Completed items shown with `line-through`

#### Task Chain
**Component**: [`components/tasks/DependencyChain.tsx`](frontend/src/components/tasks/DependencyChain.tsx)
- Horizontal DAG: `[prev] → [prev] → [● CURRENT] → [next]`
- Current task highlighted with blue ring
- Arrow connectors between nodes

### 3.3 Center — Rich Text Editor
- Large `<textarea>` with font-mono
- Placeholder: "Начните вводить текст протокола..."
- Template hint: `## СЛУШАЛИ\n\n## ВЫСТУПИЛИ\n\n## ПОСТАНОВИЛИ`
- Read-only when `status` is `on_approval` or `approved` (gray background)
- Autosave: Zustand `meetingStore.saveContent()` called every 3 seconds if `isDirty`

### 3.4 Right Panel — AI Assistant

**Component**: [`components/ai/AIPanel.tsx`](frontend/src/components/ai/AIPanel.tsx)

Three collapsible sections:

| Section | Content | Polling |
|---|---|---|
| 💡 Suggested Tasks | Cards: description, confidence %, [+Добавить] button → calls `POST /tasks` | Every 10s |
| ⚠️ Risk Highlights | Cards with severity-colored left border: CRITICAL (red), HIGH (orange), MEDIUM (yellow), LOW (gray) | Every 10s |
| 🎙 Live Transcript | Scrollable transcript area — placeholder ("Транскрипт появится здесь...") | — |

### 3.5 Approval Stepper

**Component**: [`components/ui/ApprovalStepper.tsx`](frontend/src/components/ui/ApprovalStepper.tsx)

```
✓ Подготовка ─ ✓ Ведение ─ ● Согласование ─ ○ Утверждено
  (green)       (green)      (blue, current)   (gray, future)
```

### 3.6 Status Bar (Footer)
- `● Не сохранено` (when `isDirty`) / `✓ Сохранено` (clean)
- Current version number

---

## 4. RACI Grid (Modal)

**Component**: [`components/raci/RACIGrid.tsx`](frontend/src/components/raci/RACIGrid.tsx)

```
┌─────────────────────────────────────────┐
│ Матрица RACI                          [×]│
│ ⚠️ Обнаружено 2 роли Accountable       │
│ R=Исполнитель A=Ответственный            │
│ C=Консультант I=Информируемый           │
├─────────────────────────────────────────┤
│ Пользователь      │ Роль │ Изменить     │
│ Иванов И.И.       │ [A]  │ [R ▼]       │
│ Петров П.П.       │ [R]  │ [A ▼]       │
├─────────────────────────────────────────┤
│                          [Сохранить]    │
└─────────────────────────────────────────┘
```

**Edit Mode**: Dropdowns for each role cell → PUT `/api/v1/tasks/{id}/raci`  
**Validation**: Highlights warning if 0 or 2+ Accountable

---

## 5. Task Detail Modal

**Component**: [`components/tasks/TaskDetailModal.tsx`](frontend/src/components/tasks/TaskDetailModal.tsx)

```
┌─────────────────────────────────────────┐
│ Детали задачи                         [×]│
│ Номер: KDD-FLD-003                      │
│ Статус: to_do                           │
│ Цепочка: [← prev] → [●] → [next →]    │
│ [Матрица RACI]  [Эскалировать]          │
│                                         │
│ ▼ Эскалация (collapsed by default)      │
│   Уровень: [Координационный ▼]          │
│   Причина: [textarea]                   │
│   [Отмена] [Эскалировать]               │
└─────────────────────────────────────────┘
```

---

## 6. Shared UI Components

| Component | File | Description |
|---|---|---|
| `ExportButtons` | [`components/ui/ExportButtons.tsx`](frontend/src/components/ui/ExportButtons.tsx) | PDF (red) + Excel (green) download links |
| `ApprovalStepper` | [`components/ui/ApprovalStepper.tsx`](frontend/src/components/ui/ApprovalStepper.tsx) | 4-step progress indicator |

---

## 7. State Management

### `meetingStore` — [`store/meetingStore.ts`](frontend/src/store/meetingStore.ts)

```typescript
interface MeetingState {
  meeting: MeetingWorkspace | null;
  contentMarkdown: string;    // Synced with textarea
  isDirty: boolean;           // Tracks unsaved changes
  version: number;            // Optimistic concurrency
  
  loadWorkspace(id): void;    // GET /meetings/{id}/workspace
  setContent(markdown): void; // Update local state
  saveContent(): void;        // PATCH /meetings/{id}/content
  finalize(): void;           // POST finalize
  approve(): void;            // POST approve
}
```

### `authStore` — [`store/authStore.ts`](frontend/src/store/authStore.ts)

```typescript
interface AuthState {
  user: User | null;
  token: string | null;
  isAuthenticated: boolean;
  
  login(email, password): void;    // POST /auth/login
  register(name, email, pw, r): void;
  logout(): void;
  loadFromStorage(): void;
}
```

---

## 8. API Client

**File**: [`frontend/src/api/client.ts`](frontend/src/api/client.ts)

- Axios instance with `baseURL: '/api/v1'`
- **Request interceptor**: Attaches `Authorization: Bearer <token>` from localStorage
- **Response interceptor**: On 401 → clears token, redirects to `/login`
- 14 typed API functions for all endpoints

---

## 9. Component Tree

```
App
├── BrowserRouter
│   ├── Route / → Dashboard
│   │   └── MeetingCard[] (inline)
│   ├── Route /meetings/:id → MeetingEditor
│   │   ├── StickyHeader (inline)
│   │   │   └── ExportButtons
│   │   ├── ApprovalStepper
│   │   ├── Left Sidebar (inline)
│   │   │   ├── Participants list (inline)
│   │   │   ├── Agenda list (inline)
│   │   │   └── DependencyChain
│   │   ├── Center: textarea (inline)
│   │   ├── AIPanel
│   │   │   ├── SuggestedTasks (inline)
│   │   │   ├── RiskHighlights (inline)
│   │   │   └── LiveTranscript (inline)
│   │   └── StatusBar (inline)
│   └── Route /login → Login
└── (modals, rendered at root)
    ├── RACIGrid
    └── TaskDetailModal