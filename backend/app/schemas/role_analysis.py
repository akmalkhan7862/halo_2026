from typing import List, Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict


class RoleSourceInfo(BaseModel):
    source: str
    occupation_label: Optional[str] = None
    soc_code: Optional[str] = None
    occupation_title: Optional[str] = None
    uri: Optional[str] = None


class RoleProfileSummary(BaseModel):
    id: str
    role_key: str
    display_name: str
    seniority: str
    domain: str
    description: Optional[str] = None
    required_skills_count: int
    preferred_skills_count: int
    model_config = ConfigDict(from_attributes=True)


class RoleProfileDetail(BaseModel):
    id: str
    role_key: str
    display_name: str
    seniority: str
    domain: str
    description: Optional[str] = None
    sources: List[Dict[str, Any]] = Field(default_factory=list)
    required_skills: List[str] = Field(default_factory=list)
    preferred_skills: List[str] = Field(default_factory=list)
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)


class SkillMatchItem(BaseModel):
    canonical_skill: str
    status: str  # MATCHED, WEAK, MISSING, RELATED_PARTIAL, EXTRA
    importance: str = "required"  # required | preferred | extra
    confidence: float = 1.0
    evidence_citation: Optional[str] = None
    related_to: Optional[str] = None
    reason: str


class RoleGapSummary(BaseModel):
    overall_readiness: str  # high, moderate, low
    critical_missing_skills: List[str] = Field(default_factory=list)
    quick_wins: List[str] = Field(default_factory=list)
    narrative_summary: str


class RoleMatchResult(BaseModel):
    role_key: str
    display_name: str
    seniority: str
    domain: str
    fit_score: float  # 0 to 100
    matched_skills: List[SkillMatchItem] = Field(default_factory=list)
    weak_skills: List[SkillMatchItem] = Field(default_factory=list)
    missing_skills: List[SkillMatchItem] = Field(default_factory=list)
    related_partial_skills: List[SkillMatchItem] = Field(default_factory=list)
    extra_skills: List[str] = Field(default_factory=list)
    gap_summary: RoleGapSummary


class RoleAnalysisRequest(BaseModel):
    resume_id: str
    target_role_key: Optional[str] = None  # None indicates analyze against all 12 curated roles


class SingleRoleAnalysisResponse(BaseModel):
    resume_id: str
    candidate_name: Optional[str] = None
    role_analysis: RoleMatchResult


class MultiRoleAnalysisResponse(BaseModel):
    resume_id: str
    candidate_name: Optional[str] = None
    total_roles_evaluated: int
    top_recommended_role: str
    role_rankings: List[RoleMatchResult]
