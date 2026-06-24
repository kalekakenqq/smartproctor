from collections import defaultdict
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from backend.database import get_db
from backend.models.test import Test
from backend.models.session import TestSession
from backend.models.violation import Violation
from backend.models.user import User
from backend.schemas.violation import ViolationOut
from backend.services.auth_service import require_role

router = APIRouter(prefix="/reports", tags=["reports"])


def _get_owned_test(test_id: int, teacher: User, db: Session) -> Test:
    test = db.query(Test).filter(Test.id == test_id, Test.teacher_id == teacher.id).first()
    if not test:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Тест не найден")
    return test


@router.get("/test/{test_id}/scores")
def score_distribution(test_id: int, teacher: User = Depends(require_role("teacher")), db: Session = Depends(get_db)):
    _get_owned_test(test_id, teacher, db)
    sessions = (
        db.query(TestSession)
        .filter(TestSession.test_id == test_id, TestSession.status.in_(["finished", "blocked"]))
        .all()
    )
    result = []
    for s in sessions:
        student = db.query(User).filter(User.id == s.student_id).first()
        result.append({
            "session_id": s.id,
            "student_name": student.full_name if student else "Неизвестно",
            "score": s.score,
            "risk_score": s.risk_score,
            "status": s.status,
        })
    return result


@router.get("/test/{test_id}/heatmap")
def violation_heatmap(test_id: int, teacher: User = Depends(require_role("teacher")), db: Session = Depends(get_db)):
    _get_owned_test(test_id, teacher, db)
    session_ids = [s.id for s in db.query(TestSession).filter(TestSession.test_id == test_id).all()]
    if not session_ids:
        return {}

    violations = db.query(Violation).filter(Violation.session_id.in_(session_ids)).all()
    buckets: dict[int, int] = defaultdict(int)
    for v in violations:
        minute = v.elapsed_seconds // 60
        buckets[minute] += 1

    return dict(sorted(buckets.items()))


@router.get("/session/{session_id}", response_model=List[ViolationOut])
def session_report(session_id: int, teacher: User = Depends(require_role("teacher")), db: Session = Depends(get_db)):
    session = db.query(TestSession).filter(TestSession.id == session_id).first()
    if not session:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Сессия не найдена")
    test = db.query(Test).filter(Test.id == session.test_id, Test.teacher_id == teacher.id).first()
    if not test:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Нет доступа")
    return db.query(Violation).filter(Violation.session_id == session_id).all()
