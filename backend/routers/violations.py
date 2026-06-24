import base64
import os
import uuid
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from backend.database import get_db
from backend.models.session import TestSession
from backend.models.test import Test
from backend.models.violation import Violation
from backend.models.user import User
from backend.schemas.violation import ViolationCreate, ViolationOut
from backend.services.auth_service import get_current_user, require_role
from backend.services.risk_score import violation_weight
from backend.services.ws_manager import manager

router = APIRouter(prefix="/violations", tags=["violations"])

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SNAPSHOTS_DIR = os.environ.get("SNAPSHOTS_DIR", os.path.join(BASE_DIR, "snapshots"))
os.makedirs(SNAPSHOTS_DIR, exist_ok=True)


def save_snapshot(session_id: int, snapshot_base64: str) -> str:
    header, _, data = snapshot_base64.partition(",")
    payload = data if data else header
    filename = f"{session_id}_{uuid.uuid4().hex}.jpg"
    path = os.path.join(SNAPSHOTS_DIR, filename)
    with open(path, "wb") as f:
        f.write(base64.b64decode(payload))
    return f"/snapshots/{filename}"


@router.post("", response_model=ViolationOut, status_code=status.HTTP_201_CREATED)
async def create_violation(payload: ViolationCreate, student: User = Depends(require_role("student")), db: Session = Depends(get_db)):
    session = db.query(TestSession).filter(TestSession.id == payload.session_id, TestSession.student_id == student.id).first()
    if not session:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Сессия не найдена")
    if session.status != "in_progress":
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Сессия не активна")

    weight = violation_weight(payload.type)
    snapshot_path = None
    if payload.snapshot_base64:
        snapshot_path = save_snapshot(session.id, payload.snapshot_base64)

    violation = Violation(
        session_id=session.id,
        type=payload.type,
        weight=weight,
        elapsed_seconds=payload.elapsed_seconds,
        snapshot_path=snapshot_path,
    )
    db.add(violation)

    session.risk_score = session.risk_score + weight
    test_obj = db.query(Test).filter(Test.id == session.test_id).first()
    blocked = False
    if test_obj and session.risk_score >= test_obj.risk_threshold:
        session.status = "blocked"
        blocked = True

    db.commit()
    db.refresh(violation)
    db.refresh(session)

    await manager.broadcast(session.id, {
        "type": "risk_update",
        "risk_score": session.risk_score,
        "violation": {
            "id": violation.id,
            "type": violation.type,
            "weight": violation.weight,
            "elapsed_seconds": violation.elapsed_seconds,
            "snapshot_path": violation.snapshot_path,
        },
        "blocked": blocked,
    })

    return violation


@router.get("/session/{session_id}", response_model=List[ViolationOut])
def list_violations(session_id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    session = db.query(TestSession).filter(TestSession.id == session_id).first()
    if not session:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Сессия не найдена")
    if user.role == "student" and session.student_id != user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Нет доступа")
    return db.query(Violation).filter(Violation.session_id == session_id).all()
