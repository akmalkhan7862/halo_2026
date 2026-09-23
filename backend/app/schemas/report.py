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


class ResumeFitScoresSchema(BaseModel):
    skill_match_score: float
    experience_score: float
    project_score: float
    keyword_score: float
    seniority_score: float
    overall_resume_score: float


class ResumeFitGapSummarySchema(BaseModel):
    overall_fit: str
    narrative_summary: str
    top_missing_skills: List[str] = Field(default_factory=list)
    quick_wins: List[str] = Field(default_factory=list)
    recommended_focus_areas: List[str] = Field(default_factory=list)


class ResumeFitReportSchema(BaseModel):
    role_key: Optional[str] = None
    display_name: str
    scores: ResumeFitScoresSchema
    gap_summary: ResumeFitGapSummarySchema


class CommunicationFeedbackSchema(BaseModel):
    strengths: List[str] = Field(default_factory=list)
    improvements: List[str] = Field(default_factory=list)


class InterviewPerformanceReportSchema(BaseModel):
    overall_interview_score: int
    dimension_scores: Dict[str, int] = Field(default_factory=dict)
    question_count: int = 8
    answered_count: int = 0
    score_distribution: Dict[str, int] = Field(default_factory=dict)
    key_strengths: List[str] = Field(default_factory=list)
    key_weaknesses: List[str] = Field(default_factory=list)
    recommendations: List[str] = Field(default_factory=list)
    communication_feedback: CommunicationFeedbackSchema


class FinalReportResponse(BaseModel):
    analysis_id: str
    generated_at: datetime
    candidate_profile: Dict[str, Any]
    target_job: Dict[str, Any]
    resume_fit: Optional[ResumeFitReportSchema] = None
    interview_performance: Optional[InterviewPerformanceReportSchema] = None
    analysis: AnalysisResponse
    interview_session: Optional[InterviewSessionResponse] = None
    roadmap: CareerRoadmap
    gap_analysis: Optional[Dict[str, Any]] = None
    learning_roadmap: Optional[Dict[str, Any]] = None
