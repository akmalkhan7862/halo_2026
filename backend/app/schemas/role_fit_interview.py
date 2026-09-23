from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field, ConfigDict


class RoleFitInterviewRequest(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    resume_id: str = Field(..., description="ID of previously parsed resume")
    role_key: str = Field(..., description="Key of target taxonomy role (e.g. backend_developer)")
    difficulty: Optional[str] = Field("medium", description="Interview difficulty level: easy, medium, or hard")
    question_count: Optional[int] = Field(8, ge=5, le=12, description="Target question count (7-10)")


class InterviewQuestionItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    question_id: str
    type: str = "technical"
    difficulty: Optional[str] = "medium"
    skill_focus: List[str] = Field(default_factory=list)
    resume_evidence: Optional[str] = None
    question_text: str
    expected_answer_points: List[str] = Field(default_factory=list)
    follow_up_possible: Optional[bool] = True
    follow_up_hint: Optional[str] = None


class InterviewSessionEmbedded(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    session_id: str
    questions: List[Dict[str, Any]] = Field(default_factory=list)


class RoleFitGapSummary(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    overall_fit: str
    overall_readiness: Optional[str] = None
    narrative_summary: str
    top_missing_skills: List[str] = Field(default_factory=list)
    critical_missing_skills: Optional[List[str]] = Field(default_factory=list)
    quick_wins: List[str] = Field(default_factory=list)
    recommended_focus_areas: List[str] = Field(default_factory=list)


class RoleFitInterviewResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    analysis_id: str
    role_key: str
    display_name: str
    matched_skills: List[Dict[str, Any]] = Field(default_factory=list)
    missing_skills: List[Dict[str, Any]] = Field(default_factory=list)
    weak_skills: List[Dict[str, Any]] = Field(default_factory=list)
    extra_skills: List[str] = Field(default_factory=list)
    coverage_ratio: float
    gap_summary: Dict[str, Any]
    gap_analysis: Optional[Dict[str, Any]] = None
    learning_roadmap: Optional[Dict[str, Any]] = None
    scores: Optional[Dict[str, Any]] = None
    interview: Dict[str, Any]
