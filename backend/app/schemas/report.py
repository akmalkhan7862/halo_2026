from typing import List, Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field

from app.schemas.analysis import AnalysisResponse
from app.schemas.interview import InterviewSessionResponse


class ShortTermAction(BaseModel):
    topic: str
    timeframe: str
    recommended_resources: List[str] = Field(default_factory=list)
    learning_objective: str


class ProjectSuggestion(BaseModel):
    project_title: str
    technologies: List[str] = Field(default_factory=list)
    problem_statement: str
    demonstrated_outcomes: List[str] = Field(default_factory=list)


class CertificationSuggestion(BaseModel):
    certification_name: str
    issuer: str
    relevance: str


class CareerRoadmap(BaseModel):
    immediate_resume_improvements: List[str] = Field(default_factory=list)
    short_term_learning_actions: List[ShortTermAction] = Field(default_factory=list)
    project_suggestions: List[ProjectSuggestion] = Field(default_factory=list)
    certification_suggestions: List[CertificationSuggestion] = Field(default_factory=list)
    interview_preparation_focus_areas: List[str] = Field(default_factory=list)


class FinalReportResponse(BaseModel):
    analysis_id: str
    generated_at: datetime
    candidate_profile: Dict[str, Any]
    target_job: Dict[str, Any]
    analysis: AnalysisResponse
    interview_session: Optional[InterviewSessionResponse] = None
    roadmap: CareerRoadmap
