from pydantic import BaseModel
from typing import Optional, Literal
from datetime import datetime


class ViolationCreate(BaseModel):
    session_id: int
    type: Literal["face_absent", "face_away", "multiple_faces"]
    elapsed_seconds: int = 0
    snapshot_base64: Optional[str] = None  # data:image/jpeg;base64,...


class ViolationOut(BaseModel):
    id: int
    session_id: int
    type: str
    weight: float
    elapsed_seconds: int
    snapshot_path: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True
