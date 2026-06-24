from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from backend.database import get_db
from backend.models.session import TestSession
from backend.models.test import Test, Question
from backend.models.user import User
from backend.schemas.session import SessionCreate, SessionOut, AnswerSubmit
from backend.services.auth_service import get_current_user, require_role

router = APIRouter(prefix="/sessions", tags=["sessions"])


@router.post("", response_model=SessionOut, status_code=status.HTTP_201_CREATED)
def start_session(payload: SessionCreate, student: User = Depends(require_role("student")), db: Session = Depends(get_db)):
    test = db.query(Test).filter(Test.id == payload.test_id).first()
    if not test:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Тест не найден")

    existing = (
        db.query(TestSession)
        .filter(TestSession.test_id == test.id, TestSession.student_id == student.id, TestSession.status == "in_progress")
        .first()
    )
    if existing:
        return existing

    session = TestSession(test_id=test.id, student_id=student.id, answers={})
    db.add(session)
    db.commit()
    db.refresh(session)
    return session


@router.get("/{session_id}", response_model=SessionOut)
def get_session(session_id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    session = db.query(TestSession).filter(TestSession.id == session_id).first()
    if not session:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Сессия не найдена")
    if user.role == "student" and session.student_id != user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Нет доступа")
    return session


@router.post("/{session_id}/finish", response_model=SessionOut)
def finish_session(session_id: int, payload: AnswerSubmit, student: User = Depends(require_role("student")), db: Session = Depends(get_db)):
    session = db.query(TestSession).filter(TestSession.id == session_id, TestSession.student_id == student.id).first()
    if not session:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Сессия не найдена")
    if session.status != "in_progress":
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Сессия уже завершена")

    questions = db.query(Question).filter(Question.test_id == session.test_id).all()
    correct = 0
    for q in questions:
        selected = payload.answers.get(q.id)
        if selected is not None and selected == q.correct_index:
            correct += 1
    score = (correct / len(questions) * 100) if questions else 0

    session.answers = {str(k): v for k, v in payload.answers.items()}
    session.score = score
    session.status = "finished"
    session.finished_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(session)
    return session


@router.get("/test/{test_id}/all", response_model=List[SessionOut])
def list_sessions_for_test(test_id: int, teacher: User = Depends(require_role("teacher")), db: Session = Depends(get_db)):
    test = db.query(Test).filter(Test.id == test_id, Test.teacher_id == teacher.id).first()
    if not test:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Тест не найден")
    return db.query(TestSession).filter(TestSession.test_id == test_id).all()
