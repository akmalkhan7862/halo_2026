import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Text, Integer, DateTime, ForeignKey
from sqlalchemy.orm import relationship

from app.models.base import Base, GUID, CompatibleJSON


class InterviewAnswer(Base):
    __tablename__ = "interview_answers"

    id = Column(GUID, primary_key=True, default=lambda: str(uuid.uuid4()))
    interview_session_id = Column(GUID, ForeignKey("interview_sessions.id", ondelete="CASCADE"), nullable=False, index=True)
    question_id = Column(String(50), nullable=False)
    question_text = Column(Text, nullable=False)
    answer_text = Column(Text, nullable=False)
    evaluation_json = Column(CompatibleJSON, nullable=True, default=dict)
    score = Column(Integer, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    session = relationship("InterviewSession", back_populates="answers")
