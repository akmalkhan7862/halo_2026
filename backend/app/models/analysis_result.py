import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship

from app.models.base import Base, GUID, CompatibleJSON


class AnalysisResult(Base):
    __tablename__ = "analysis_results"

    id = Column(GUID, primary_key=True, default=lambda: str(uuid.uuid4()))
    resume_id = Column(GUID, ForeignKey("resumes.id", ondelete="CASCADE"), nullable=False, index=True)
    job_description_id = Column(GUID, ForeignKey("job_descriptions.id", ondelete="CASCADE"), nullable=True, index=True)
    role_key = Column(String(100), nullable=True, index=True)
    target_role = Column(String(255), nullable=True)
    matched_skills = Column(CompatibleJSON, nullable=False, default=list)
    missing_skills = Column(CompatibleJSON, nullable=False, default=list)
    weak_skills = Column(CompatibleJSON, nullable=False, default=list)
    related_partial_skills = Column(CompatibleJSON, nullable=False, default=list)
    extra_skills = Column(CompatibleJSON, nullable=False, default=list)
    gap_summary = Column(CompatibleJSON, nullable=False, default=dict)
    gap_analysis = Column(CompatibleJSON, nullable=True, default=dict)
    learning_roadmap = Column(CompatibleJSON, nullable=True, default=dict)
    scores = Column(CompatibleJSON, nullable=False, default=dict)
    explanations = Column(CompatibleJSON, nullable=False, default=dict)
    provenance = Column(CompatibleJSON, nullable=True, default=dict)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    resume = relationship("Resume", back_populates="analysis_results")
    job_description = relationship("JobDescription", back_populates="analysis_results")
    interview_sessions = relationship("InterviewSession", back_populates="analysis_result", cascade="all, delete-orphan")
