from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional

from src.adapters.services.file_parser import parse_uploaded_file
from src.adapters.services.protocol_parser import parse_notes_to_protocol
from src.infrastructure.database import get_async_session
from src.infrastructure.dependencies import require_role

router = APIRouter(prefix="/api/v1/import", tags=["import"])


@router.post("/protocol")
async def import_protocol(
    file: UploadFile = File(...),
    meeting_id: Optional[str] = None,
    session: AsyncSession = Depends(get_async_session),
    _user=Depends(require_role("secretary", "admin")),
):
    if not file.filename:
        raise HTTPException(400, "No file provided")

    ext = file.filename.rsplit(".", 1)[-1].lower() if "." in file.filename else ""
    if ext not in ("docx", "xlsx", "txt", "md"):
        raise HTTPException(400, f"Unsupported format: .{ext}")

    content = await file.read()
    text = await parse_uploaded_file(content, ext)

    protocol_data = await parse_notes_to_protocol(text, use_llm=True)

    missing_fields = []
    if not protocol_data.get("decided") and not protocol_data.get("heard"):
        missing_fields.append("No structured content found in file")

    return {
        "filename": file.filename,
        "extracted_text": text[:2000],
        "protocol_draft": protocol_data,
        "meeting_id": meeting_id,
        "missing_fields": missing_fields,
        "needs_clarification": len(missing_fields) > 0,
        "clarification_prompt": (
            "Необходимо уточнить: участники, повестка, принятые решения. "
            "Пожалуйста, укажите ФИО докладчиков, ответственных и сроки."
        ) if missing_fields else None,
    }