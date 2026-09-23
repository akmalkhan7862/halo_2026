from typing import List, Optional
from pydantic import BaseModel, Field, ConfigDict


class SkillGapDetail(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    skill: str = Field(..., description="Canonical name of the target skill")
    importance: str = Field(..., description="'required' or 'preferred'")
    status: str = Field(..., description="'matched', 'weak', 'missing', or 'related_partial'")
    evidence: List[str] = Field(default_factory=list, description="Concrete evidence citations from candidate resume")
    explanation: str = Field(..., description="Explainable reason behind this classification and readiness impact")
    related_to: Optional[str] = Field(None, description="Transferable skill name if classified as related_partial")


class SkillGapAnalysisResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    role_key: str
    display_name: str
    coverage_ratio: float
    required_coverage: float
    preferred_coverage: float
    skill_gap_details: List[SkillGapDetail] = Field(default_factory=list)
    critical_missing_skills: List[str] = Field(default_factory=list)
    quick_wins: List[str] = Field(default_factory=list)
    gap_narrative: str
