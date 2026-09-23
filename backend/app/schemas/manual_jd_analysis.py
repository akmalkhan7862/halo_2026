from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field, ConfigDict


class ManualJDAnalysisRequest(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    resume_id: str = Field(..., description="UUID of previously parsed resume")
    jd_text: str = Field(..., min_length=20, description="Raw job description text")
    difficulty: Optional[str] = Field("medium", description="Interview difficulty level: easy, medium, or hard")
    question_count: Optional[int] = Field(8, ge=5, le=12, description="Target question count (7-10)")


class ManualJDAnalysisResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    analysis_id: str
    mode: str = "manual_jd"
    role_key: Optional[str] = None
    role_display_name: str
    display_name: Optional[str] = None
    target_role: Optional[str] = None
    matched_skills: List[Dict[str, Any]] = Field(default_factory=list)
    missing_skills: List[Dict[str, Any]] = Field(default_factory=list)
    weak_skills: List[Dict[str, Any]] = Field(default_factory=list)
    extra_skills: List[str] = Field(default_factory=list)
    coverage_ratio: float = 0.0
    scores: Dict[str, Any] = Field(default_factory=dict)
    gap_summary: Dict[str, Any] = Field(default_factory=dict)
    gap_analysis: Optional[Dict[str, Any]] = None
    learning_roadmap: Optional[Dict[str, Any]] = None
    interview: Optional[Dict[str, Any]] = None
