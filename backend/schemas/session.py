from pydantic import BaseModel
from typing import Dict, Optional
from datetime import datetime


class SessionCreate(BaseModel):
    test_id: int


class AnswerSubmit(BaseModel):
    answers: Dict[int, int]  # question_id -> selected_index


class SessionOut(BaseModel):
    id: int
    test_id: int
    student_id: int
    status: str
    score: Optional[float] = None
    risk_score: float
    started_at: datetime
    finished_at: Optional[datetime] = None

    class Config:
        from_attributes = True
