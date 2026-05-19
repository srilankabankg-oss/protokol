from datetime import datetime, UTC
from uuid import UUID, uuid4

from sqlalchemy.ext.asyncio import AsyncSession

from src.adapters.db.models import Meeting, Task
from src.adapters.services.raci_service import RaciService
from src.core.enums import MeetingStatus
from src.infrastructure.llm_gateway import LLMGateway, SYSTEM_PROMPTS


MEETING_SUMMARY_SCHEMA = {
    "type": "object",
    "required": ["content_markdown", "identified_speakers", "detected_risks"],
    "properties": {
        "content_markdown": {
            "type": "string",
            "description": "Markdown текст с блоками ## СЛУШАЛИ, ## ВЫСТУПИЛИ, ## ПОСТАНОВИЛИ",
        },
        "identified_speakers": {
            "type": "array",
            "items": {"type": "string"},
        },
        "detected_risks": {
            "type": "array",
            "items": {
                "type": "object",
                "required": ["severity", "text_anchor", "message"],
                "properties": {
                    "severity": {"type": "string", "enum": ["LOW", "MEDIUM", "HIGH", "CRITICAL"]},
                    "text_anchor": {"type": "string"},
                    "message": {"type": "string"},
                },
            },
        },
    },
}

TASK_EXTRACTION_SCHEMA = {
    "type": "object",
    "required": ["extracted_tasks"],
    "properties": {
        "extracted_tasks": {
            "type": "array",
            "items": {
                "type": "object",
                "required": ["description", "raci_assignments", "confidence_score", "raci_valid"],
                "properties": {
                    "description": {"type": "string"},
                    "raci_assignments": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "required": ["name", "role"],
                            "properties": {
                                "name": {"type": "string"},
                                "role": {"type": "string", "enum": ["R", "A", "C", "I"]},
                            },
                        },
                    },
                    "confidence_score": {"type": "number", "minimum": 0.0, "maximum": 1.0},
                    "raci_valid": {"type": "boolean"},
                },
            },
        },
    },
}


class AIService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.llm = LLMGateway()

    async def process_audio_chunk(self, meeting_id: UUID, audio_data: bytes) -> dict:
        recognized_text = "[транскрипт недоступен — STT сервис в разработке]"
        speaker = "Speaker_0"

        return {
            "chunk_processed": True,
            "recognized_text_fragment": f"Фрагмент речи из встречи {meeting_id}",
            "speaker_detected": speaker,
        }

    async def generate_insights(self, meeting_id: UUID) -> dict:
        meeting = await self.session.get(Meeting, meeting_id)
        if meeting is None:
            raise ValueError("Meeting not found")

        if not meeting.content_markdown:
            return {
                "suggested_action_items": [],
                "detected_risks": [],
            }

        try:
            summary = await self.llm.structured_output(
                system_prompt=SYSTEM_PROMPTS["summary_agent"],
                user_message=meeting.content_markdown,
                schema=MEETING_SUMMARY_SCHEMA,
                max_retries=2,
            )

            update_data = {
                "content_markdown": summary.get("content_markdown", meeting.content_markdown),
                "identified_speakers": summary.get("identified_speakers", []),
                "detected_risks": summary.get("detected_risks", []),
            }

            meeting.content_markdown = update_data["content_markdown"]
            self.session.add(meeting)

            tasks = await self.llm.structured_output(
                system_prompt=SYSTEM_PROMPTS["task_extraction_agent"],
                user_message=meeting.content_markdown,
                schema=TASK_EXTRACTION_SCHEMA,
                max_retries=2,
            )

            suggested_items = []
            for t in tasks.get("extracted_tasks", []):
                suggested_items.append({
                    "temporary_id": f"tmp-ai-{uuid4().hex[:8]}",
                    "extracted_description": t.get("description", ""),
                    "confidence_score": t.get("confidence_score", 0.7),
                    "json_schema_matched": t.get("raci_valid", False),
                })

            return {
                "suggested_action_items": suggested_items,
                "detected_risks": update_data["detected_risks"],
            }

        except Exception:
            return {
                "suggested_action_items": [],
                "detected_risks": [],
            }

    async def close(self):
        await self.llm.close()