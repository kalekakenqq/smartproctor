from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, JSON, Float
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from backend.database import Base


class TestSession(Base):
    __tablename__ = "test_sessions"

    id = Column(Integer, primary_key=True, index=True)
    test_id = Column(Integer, ForeignKey("tests.id"), nullable=False)
    student_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    status = Column(String, nullable=False, default="in_progress")  # in_progress | finished | blocked
    answers = Column(JSON, default=dict)  # {question_id: selected_index}
    score = Column(Float, nullable=True)
    risk_score = Column(Float, nullable=False, default=0)
    started_at = Column(DateTime(timezone=True), server_default=func.now())
    finished_at = Column(DateTime(timezone=True), nullable=True)

    violations = relationship("Violation", back_populates="session", cascade="all, delete-orphan")
