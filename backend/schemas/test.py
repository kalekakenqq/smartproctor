from pydantic import BaseModel, Field
from typing import List, Optional


class QuestionCreate(BaseModel):
    text: str
    options: List[str] = Field(min_length=2)
    correct_index: int


class QuestionOut(BaseModel):
    id: int
    text: str
    options: List[str]

    class Config:
        from_attributes = True


class QuestionWithAnswer(QuestionOut):
    correct_index: int


class TestCreate(BaseModel):
    title: str
    description: str = ""
    duration_minutes: int = 30
    risk_threshold: int = 10
    questions: List[QuestionCreate]


class TestOut(BaseModel):
    id: int
    title: str
    description: str
    duration_minutes: int
    risk_threshold: int
    teacher_id: int

    class Config:
        from_attributes = True


class TestDetail(TestOut):
    questions: List[QuestionOut]


class TestDetailWithAnswers(TestOut):
    questions: List[QuestionWithAnswer]
