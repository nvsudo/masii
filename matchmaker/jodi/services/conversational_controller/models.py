from pydantic import BaseModel
from typing import Any, Dict, Optional
from uuid import UUID
from datetime import datetime

class ConversationState(BaseModel):
    id: Optional[UUID]
    user_id: UUID
    session_id: str
    state_json: Dict[str, Any] = {}
    completion_map: Dict[str, float] = {}
    confidence_map: Dict[str, float] = {}
    progress_pct: float = 0.0
    priority_tier: Optional[int] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

class UpdateStateRequest(BaseModel):
    session_id: str
    user_id: UUID
    state_json: Dict[str, Any]
    confidence: float

class AdvanceStateRequest(BaseModel):
    session_id: str
    user_id: UUID
    action: str
