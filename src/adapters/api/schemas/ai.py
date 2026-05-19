from typing import Optional, Literal

from pydantic import BaseModel, Field


class AudioChunkResponse(BaseModel):
    chunk_processed: bool = True
    recognized_text_fragment: Optional[str] = None
    speaker_detected: Optional[str] = None


class SuggestedActionItem(BaseModel):
    temporary_id: str
    extracted_description: str
    confidence_score: float = Field(ge=0.0, le=1.0)
    json_schema_matched: bool = True


class DetectedRisk(BaseModel):
    risk_id: str
    severity: Literal["LOW", "MEDIUM", "HIGH", "CRITICAL"]
    text_anchor: str
    message: str


class AIInsightsResponse(BaseModel):
    suggested_action_items: list[SuggestedActionItem] = []
    detected_risks: list[DetectedRisk] = []