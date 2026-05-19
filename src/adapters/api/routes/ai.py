from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession

from src.adapters.api.schemas.ai import AIInsightsResponse, AudioChunkResponse
from src.adapters.services.ai_service import AIService
from src.infrastructure.database import get_async_session
from src.infrastructure.dependencies import require_user, require_role

router = APIRouter(prefix="/api/v1", tags=["ai"])


@router.post("/ai/stream-audio", response_model=AudioChunkResponse)
async def stream_audio(
    meeting_id: UUID,
    file: UploadFile = File(...),
    session: AsyncSession = Depends(get_async_session),
    _current_user=Depends(require_role("secretary", "admin")),
):
    audio_data = await file.read()
    ai = AIService(session)
    try:
        result = await ai.process_audio_chunk(meeting_id, audio_data)
        return AudioChunkResponse(**result)
    finally:
        await ai.close()


@router.get("/meetings/{meeting_id}/ai-insights", response_model=AIInsightsResponse)
async def get_ai_insights(
    meeting_id: UUID,
    session: AsyncSession = Depends(get_async_session),
    _current_user=Depends(require_user),
):
    ai = AIService(session)
    try:
        insights = await ai.generate_insights(meeting_id)
        return AIInsightsResponse(**insights)
    except ValueError:
        raise HTTPException(status_code=404, detail="Meeting not found")
    finally:
        await ai.close()