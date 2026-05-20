import json
import re
from typing import Any, Optional

import httpx

from src.infrastructure.config import get_settings

settings = get_settings()

DEFAULT_TIMEOUT = 180

SYSTEM_PROMPTS = {
    "summary_agent": {
        "role": "system",
        "content": (
            "ROLE: Senior Corporate Secretary & Business Analyst Expert\n"
            "CONTEXT: Ты внутри ИИ-подсистемы платформы «Книга добрых дел». "
            "Анализируй сырой транскрипт совещания и преврати его в профессиональный протокол.\n"
            "INSTRUCTIONS:\n"
            "1. Раздели текст по блокам обсуждения.\n"
            "2. Для каждого блока соблюдай структуру: "
            "## СЛУШАЛИ (краткая суть) / ## ВЫСТУПИЛИ (тезисы + позиции) / ## ПОСТАНОВИЛИ (решения).\n"
            "3. Деловой, лаконичный стиль. Убирай слова-паразиты, сохраняй фактологическую точность.\n"
            "4. Выдавай результат СТРОГО в формате JSON по заданной схеме."
        ),
    },
    "task_extraction_agent": {
        "role": "system",
        "content": (
            "ROLE: Lead Project Manager & Data Integrity Architect (PMI/PMBOK Expert)\n"
            "CONTEXT: Ты ИИ-модуль платформы «Книга добрых дел». "
            "Проанализируй текст протокола и извлеки массив поручений с распределением RACI.\n"
            "BUSINESS RULES:\n"
            "1. На каждую задачу — СТРОГО ОДНА роль 'A' (Accountable).\n"
            "2. Минимум один 'R' (Responsible), может совпадать с 'A'.\n"
            "3. Формат ответа — СТРОГО JSON по заданной схеме."
        ),
    },
}


class LLMGatewayError(Exception):
    pass


class LLMGateway:
    def __init__(self):
        self.client = httpx.AsyncClient(timeout=DEFAULT_TIMEOUT)

    def _api_key(self) -> str:
        from os import environ
        return environ.get("STEPFUN_API_KEY", "") or settings.llm_api_key or ""

    def _base_url(self) -> str:
        return settings.llm_base_url or "https://api.stepfun.com/step_plan/v1"

    async def chat_completion(
        self,
        messages: list[dict],
        model: str = "step-router-v1",
        temperature: float = 0.0,
        max_tokens: int = 4096,
        response_format: Optional[dict] = None,
        tools: Optional[list[dict]] = None,
        tool_choice: Optional[dict] = None,
    ) -> dict:
        headers = {
            "Authorization": f"Bearer {self._api_key()}",
            "Content-Type": "application/json",
        }
        payload: dict[str, Any] = {
            "model": model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
        }
        if response_format:
            payload["response_format"] = response_format
        if tools:
            payload["tools"] = tools
            payload["tool_choice"] = tool_choice or "auto"

        response = await self.client.post(
            f"{self._base_url()}/chat/completions",
            json=payload,
            headers=headers,
        )
        if response.status_code != 200:
            raise LLMGatewayError(f"LLM error {response.status_code}: {response.text[:200]}")
        return response.json()

    def _build_tool_from_schema(self, schema: dict) -> list[dict]:
        return [{
            "type": "function",
            "function": {
                "name": "output_structured_data",
                "description": "Output the extracted data in the required JSON structure",
                "parameters": {
                    "type": "object",
                    "properties": schema.get("properties", {}),
                    "required": schema.get("required", []),
                },
            },
        }]

    async def structured_output(
        self,
        system_prompt: dict,
        user_message: str,
        schema: dict,
        max_retries: int = 2,
    ) -> dict:
        messages: list[dict] = [
            system_prompt,
            {"role": "user", "content": user_message},
        ]

        tools = self._build_tool_from_schema(schema)

        for attempt in range(max_retries + 1):
            try:
                result = await self.chat_completion(
                    messages,
                    temperature=0.0,
                    tools=tools,
                    tool_choice="required",
                )
                choice = result["choices"][0]
                message = choice["message"]

                # Prefer tool_calls — guarantees schema adherence
                if message.get("tool_calls"):
                    args_str = message["tool_calls"][0]["function"]["arguments"]
                    parsed = json.loads(args_str)
                elif message.get("content"):
                    parsed = self._extract_json(message["content"])
                else:
                    raise ValueError("Empty response from LLM")

                self._validate_schema(parsed, schema)
                return parsed

            except (KeyError, json.JSONDecodeError, LLMGatewayError, ValueError) as e:
                if attempt < max_retries:
                    correction_prompt = (
                        f"Твой предыдущий ответ невалиден. Ошибка: {e}. "
                        f"Исправь ответ и верни СТРОГО валидный JSON, соответствующий схеме. "
                        f"Без markdown-обёрток, без лишнего текста."
                    )
                    prev_content = message.get("content", "") if "message" in dir() else ""
                    messages.append({"role": "assistant", "content": prev_content})
                    messages.append({"role": "user", "content": correction_prompt})
                else:
                    raise LLMGatewayError(f"Failed after {max_retries + 1} attempts: {e}")

        raise LLMGatewayError("Max retries exceeded")

    def _extract_json(self, raw: str) -> dict:
        raw = raw.strip()

        if raw.startswith("```json"):
            raw = raw[7:]
        if raw.startswith("```"):
            raw = raw[3:]
        if raw.endswith("```"):
            raw = raw[:-3]
        raw = raw.strip()

        match = re.search(r"\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}", raw, re.DOTALL)
        if match:
            try:
                return json.loads(match.group(0))
            except json.JSONDecodeError:
                pass

        return json.loads(raw)

    def _validate_schema(self, data: dict, schema: dict) -> None:
        required_fields = schema.get("required", [])
        for field in required_fields:
            if field not in data:
                raise ValueError(f"Missing required field: {field}")

    async def close(self):
        await self.client.aclose()