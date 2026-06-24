from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from backend.database import get_db
from backend.models.test import Test, Question
from backend.models.user import User
from backend.schemas.test import TestCreate, TestOut, TestDetail, TestDetailWithAnswers
from backend.services.auth_service import get_current_user, require_role

router = APIRouter(prefix="/tests", tags=["tests"])


@router.post("", response_model=TestDetailWithAnswers, status_code=status.HTTP_201_CREATED)
def create_test(payload: TestCreate, teacher: User = Depends(require_role("teacher")), db: Session = Depends(get_db)):
    test = Test(
        title=payload.title,
        description=payload.description,
        teacher_id=teacher.id,
        duration_minutes=payload.duration_minutes,
        risk_threshold=payload.risk_threshold,
    )
    db.add(test)
    db.flush()

    for q in payload.questions:
        db.add(Question(test_id=test.id, text=q.text, options=q.options, correct_index=q.correct_index))

    db.commit()
    db.refresh(test)
    return test


@router.get("", response_model=List[TestOut])
def list_tests(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    query = db.query(Test)
    if user.role == "teacher":
        query = query.filter(Test.teacher_id == user.id)
    return query.all()


@router.get("/{test_id}", response_model=TestDetail)
def get_test(test_id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    test = db.query(Test).filter(Test.id == test_id).first()
    if not test:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Тест не найден")
    return test


@router.get("/{test_id}/full", response_model=TestDetailWithAnswers)
def get_test_full(test_id: int, teacher: User = Depends(require_role("teacher")), db: Session = Depends(get_db)):
    test = db.query(Test).filter(Test.id == test_id, Test.teacher_id == teacher.id).first()
    if not test:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Тест не найден")
    return test
