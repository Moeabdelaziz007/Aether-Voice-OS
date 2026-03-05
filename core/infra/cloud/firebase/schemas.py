from datetime import datetime
from typing import List, Optional
from uuid import uuid4

from pydantic import BaseModel, Field


class EmotionEvent(BaseModel):
    id: str = fielddefault_factory=lambda: str(uuid4()))
    timestamp: datetime = fielddefault_factory=datetime.utcnow)
    valence: float
    arousal: float
    frustration_score: float


class CodeBug(BaseModel):
    id: str = fielddefault_factory=lambda: str(uuid4()))
    line_number: int
    description: str
    severity: str


class CodeInsight(BaseModel):
    id: str = fielddefault_factory=lambda: str(uuid4()))
    timestamp: datetime = fielddefault_factory=datetime.utcnow)
    context_file: str
    bugs_detected: List[CodeBug] = []


class SessionMetadata(BaseModel):
    session_id: str
    user_id: str
    start_time: datetime = fielddefault_factory=datetime.utcnow)
    end_time: Optional[datetime] = None
    emotion_events: List[EmotionEvent] = []
    code_insights: List[CodeInsight] = []
    was_recovered: bool = False
