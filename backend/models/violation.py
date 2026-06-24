from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Float
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from backend.database import Base


class Violation(Base):
    __tablename__ = "violations"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("test_sessions.id"), nullable=False)
    type = Column(String, nullable=False)  # face_absent | face_away | multiple_faces
    weight = Column(Float, nullable=False)
    elapsed_seconds = Column(Integer, nullable=False, default=0)  # offset from test start, for heatmap
    snapshot_path = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    session = relationship("TestSession", back_populates="violations")
