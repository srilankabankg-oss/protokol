# AI Services: LLM Gateway & Agents

**Gateway**: [`src/infrastructure/llm_gateway.py`](src/infrastructure/llm_gateway.py)  
**Service**: [`src/adapters/services/ai_service.py`](src/adapters/services/ai_service.py)  
**Routes**: [`src/adapters/api/routes/ai.py`](src/adapters/api/routes/ai.py)  
**Schemas**: [`src/adapters/api/schemas/ai.py`](src/adapters/api/schemas/ai.py)

---

## 1. Architecture Overview

```
┌─────────────────────┐
│   API Routes (ai.py) │
│   /ai/stream-audio    │
│   /meetings/{id}/     │
│     ai-insights       │
└─────────┬───────────┘
          │
┌─────────▼───────────┐
│   AIService          │
│   - process_audio()  │
│   - generate_insights()│
└─────────┬───────────┘
          │
┌─────────▼───────────┐
│   LLMGateway         │
│   - chat_completion() │
│   - structured_output()│
│   - _extract_json()  │
│   - _validate_schema()│
└─────────┬───────────┘
          │
┌─────────▼───────────┐
│  Provider APIs       │
│  StepFun (primary)    │
│  OpenRouter (fallback)│
│  Gemini (fallback)    │
└─────────────────────┘
```

---

## 2. LLM Gateway (`LLMGateway`)

### 2.1 Configuration

Set via `Settings` in [`src/infrastructure/config.py`](src/infrastructure/config.py) and environment variables:

| Setting | Default | Description |
|---|---|---|
| `llm_base_url` | `https://api.stepfun.com/step_plan/v1` | Primary API endpoint |
| `llm_model` | `step-router-v1` | Default model |
| `llm_api_key` | `STEPFUN_API_KEY` env var | API key (never committed) |
| `llm_timeout` | `180` seconds | Request timeout |

### 2.2 Methods

#### `chat_completion(messages, temperature, max_tokens) → str`

Low-level chat completion. Sends POST to `{base_url}/chat/completions`.  
Raises `LLMGatewayError` on non-200 response.

#### `structured_output(system_prompt, user_message, schema, max_retries=2) → dict`

High-level method for JSON-structured responses. Supports **4-level fallback**:

```
Attempt 0: temperature=0.3
  ↓ (invalid JSON / missing fields)
Attempt 1: temperature=0.0 + error correction prompt
  ↓ (still fails)
Attempt 2: temperature=0.0 + error correction prompt
  ↓ (still fails)
→ LLMGatewayError raised → AIService returns empty insights
```

#### `_extract_json(raw: str) → dict`

Handles common LLM output issues:
- Strips markdown code fences (` ```json ` / ` ``` `)
- Regex extraction: `re.search(r"\{.*\}", raw, re.DOTALL)`
- Falls back to `json.loads(raw)`

#### `_validate_schema(data: dict, schema: dict) → None`

Checks all `required` fields from the JSON schema are present. Raises `ValueError` on missing fields.

---

## 3. AI Agents

### 3.1 Summary Agent

**System Prompt**: `SUMMARY_AGENT_PROMPT` in [`src/infrastructure/llm_gateway.py`](src/infrastructure/llm_gateway.py)

**Role**: Senior Corporate Secretary & Business Analyst Expert  
**Input**: Raw meeting transcript / unformatted text  
**Output**: Structured Markdown with three-section format + risk detection

**JSON Schema** — `MEETING_SUMMARY_SCHEMA` in [`src/adapters/services/ai_service.py`](src/adapters/services/ai_service.py):
```json
{
  "required": ["content_markdown", "identified_speakers", "detected_risks"],
  "properties": {
    "content_markdown": {"type": "string"},
    "identified_speakers": {"type": "array", "items": {"type": "string"}},
    "detected_risks": {
      "type": "array",
      "items": {
        "required": ["severity", "text_anchor", "message"],
        "properties": {
          "severity": {"enum": ["LOW", "MEDIUM", "HIGH", "CRITICAL"]},
          "text_anchor": {"type": "string"},
          "message": {"type": "string"}
        }
      }
    }
  }
}
```

### 3.2 Task Extraction Agent

**System Prompt**: `TASK_EXTRACTION_AGENT_PROMPT` in [`src/infrastructure/llm_gateway.py`](src/infrastructure/llm_gateway.py)

**Role**: Lead Project Manager & Data Integrity Architect  
**Input**: Structured meeting Markdown  
**Output**: Action items with RACI assignments and confidence scores

**JSON Schema** — `TASK_EXTRACTION_SCHEMA` in [`src/adapters/services/ai_service.py`](src/adapters/services/ai_service.py):
```json
{
  "required": ["extracted_tasks"],
  "properties": {
    "extracted_tasks": {
      "type": "array",
      "items": {
        "required": ["description", "raci_assignments", "confidence_score", "raci_valid"],
        "properties": {
          "description": {"type": "string"},
          "raci_assignments": {
            "type": "array",
            "items": {
              "required": ["name", "role"],
              "properties": {
                "name": {"type": "string"},
                "role": {"enum": ["R", "A", "C", "I"]}
              }
            }
          },
          "confidence_score": {"type": "number", "minimum": 0.0, "maximum": 1.0},
          "raci_valid": {"type": "boolean"}
        }
      }
    }
  }
}
```

### 3.3 Execution Flow

```
User clicks "AI Insights" / Polling timer fires (every 10s)
   │
   ▼
AIService.generate_insights(meeting_id)
   │
   ├─► Load meeting.content_markdown from DB
   │
   ├─► Summary Agent (structured_output)
   │   ├─► Returns: {content_markdown, identified_speakers, detected_risks}
   │   └─► Updates meeting.content_markdown in DB
   │
   ├─► Task Extraction Agent (structured_output)
   │   ├─► Returns: {extracted_tasks: [...]}
   │   └─► Maps to SuggestedActionItem[] for frontend
   │
   └─► Returns: {suggested_action_items, detected_risks}
```

---

## 4. Audio Streaming (Planned)

**Endpoint**: `POST /api/v1/ai/stream-audio`  
**Status**: API stub ready — accepts `multipart/form-data` audio chunks  
**Planned**: Integration with STT service (diarization + transcription)

**Route**: [`src/adapters/api/routes/ai.py`](src/adapters/api/routes/ai.py) — `stream_audio()`

---

## 5. Fallback Strategy (from Technical Specification)

Per the system requirements, a 4-level degradation strategy is implemented:

| Level | Trigger | Action |
|---|---|---|
| **1. JSON Repair** | LLM wrapped JSON in markdown fences or added trailing text | `_extract_json()` with regex, strip code fences |
| **2. Self-Correction** | Valid JSON but missing required fields | Retry up to 2 times with `temperature=0.0` + error-aware correction prompt |
| **3. Auto-Fix** | Multiple Accountable (A) roles | `RaciService._auto_correct_assignments()` — extra A's → R |
| **4. Graceful Degradation** | Total LLM failure (timeout, crash) | Return empty `{suggested_action_items: [], detected_risks: []}` — system stays operational |

---

## 6. RACI Validation Integration

After task extraction, the AI pipeline invokes `RaciService`:

- `validate_raci_for_task(task_id)` — checks existing assignments for compliance
- `update_assignments(task_id, data, auto_correct=True)` — applies with automatic fixes
- `_auto_correct_assignments()` — internal self-healing for RACI violations

**Service**: [`src/adapters/services/raci_service.py`](src/adapters/services/raci_service.py)  
**DB Trigger**: [`alembic/versions/656a3c5ba51a_add_raci_accountable_constraint.py`](alembic/versions/656a3c5ba51a_add_raci_accountable_constraint.py)