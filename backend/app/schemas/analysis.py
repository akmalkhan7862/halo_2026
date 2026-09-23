from typing import List, Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict


class AnalysisRequest(BaseModel):
    resume_id: str
    job_description_id: str
    target_role: Optional[str] = None
    taxonomy_sources: List[str] = Field(default_factory=lambda: ["esco", "onet", "custom"])


class SkillClassificationItem(BaseModel):
    canonical_skill: str
    raw_text: Optional[str] = None
    status: str  # MATCHED, WEAK, MISSING, RELATED_PARTIAL, EXTRA
    importance: Optional[str] = "required"  # required | preferred | extra
    confidence: float = 1.0
    evidence_citation: Optional[str] = None
    related_to: Optional[str] = None
    reason: str


class GapSummarySchema(BaseModel):
    overall_readiness: str  # high, moderate, low
    overall_fit: Optional[str] = None
    critical_missing_skills: List[str] = Field(default_factory=list)
    top_missing_skills: Optional[List[str]] = Field(default_factory=list)
    quick_wins: List[str] = Field(default_factory=list)
    recommended_focus_areas: Optional[List[str]] = Field(default_factory=list)
    narrative_summary: str
    coverage_ratio: Optional[float] = None


class ScoreBreakdownItem(BaseModel):
    reason: str
    impact: str  # e.g. "+12", "-8"


class ComponentScoreSchema(BaseModel):
    score: float
    max_score: float = 100.0
    weight: float
    breakdown: List[ScoreBreakdownItem] = Field(default_factory=list)
    recommendations: List[str] = Field(default_factory=list)


class OverallScoresSchema(BaseModel):
    overall_score: float
    skill_match_score: ComponentScoreSchema
    experience_score: ComponentScoreSchema
    project_score: ComponentScoreSchema
    keyword_score: ComponentScoreSchema
    seniority_score: ComponentScoreSchema


class AnalysisResponse(BaseModel):
    id: str
    resume_id: str
    job_description_id: Optional[str] = None
    role_key: Optional[str] = None
    target_role: str
    matched_skills: List[SkillClassificationItem] = Field(default_factory=list)
    weak_skills: List[SkillClassificationItem] = Field(default_factory=list)
    missing_skills: List[SkillClassificationItem] = Field(default_factory=list)
    related_partial_skills: List[SkillClassificationItem] = Field(default_factory=list)
    extra_skills: List[str] = Field(default_factory=list)
    gap_summary: GapSummarySchema
    scores: OverallScoresSchema
    explanations: Dict[str, Any] = Field(default_factory=dict)
    provenance: Dict[str, Any] = Field(default_factory=dict)
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)
