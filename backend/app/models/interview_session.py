import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Integer, DateTime, ForeignKey
from sqlalchemy.orm import relationship

from app.models.base import Base, GUID, CompatibleJSON


class InterviewSession(Base):
    __tablename__ = "interview_sessions"

    id = Column(GUID, primary_key=True, default=lambda: str(uuid.uuid4()))
    analysis_result_id = Column(GUID, ForeignKey("analysis_results.id", ondelete="CASCADE"), nullable=False, index=True)
    target_role = Column(String(255), nullable=False)
    difficulty = Column(String(50), nullable=False, default="medium")  # easy, medium, hard
    question_count = Column(Integer, nullable=False, default=8)
    status = Column(String(50), nullable=False, default="created")  # created, in_progress, completed, failed
    interview_plan = Column(CompatibleJSON, nullable=True, default=dict)
    generated_questions = Column(CompatibleJSON, nullable=False, default=list)
    overall_score = Column(Integer, nullable=True)
    summary_feedback = Column(CompatibleJSON, nullable=True, default=dict)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    analysis_result = relationship("AnalysisResult", back_populates="interview_sessions")
    answers = relationship("InterviewAnswer", back_populates="session", cascade="all, delete-orphan")
