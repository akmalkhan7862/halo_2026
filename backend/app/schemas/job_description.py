from typing import List, Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict


class JDSkillRequirement(BaseModel):
    raw_text: str
    canonical_skill: str
    importance: str = "required"  # required | preferred
    confidence: float = 1.0


class ExperienceRequirement(BaseModel):
    minimum_years: int = 0
    maximum_years: Optional[int] = None
    detected_from_text: bool = False


class ParsedJDData(BaseModel):
    job_title: str
    company: Optional[str] = None
    seniority: str = "mid"  # intern, junior, mid, senior, lead
    required_skills: List[JDSkillRequirement] = Field(default_factory=list)
    preferred_skills: List[JDSkillRequirement] = Field(default_factory=list)
    responsibilities: List[str] = Field(default_factory=list)
    qualifications: List[str] = Field(default_factory=list)
    keywords: List[str] = Field(default_factory=list)
    experience_requirements: ExperienceRequirement = Field(default_factory=ExperienceRequirement)
    domain: str = "general"


class JDCreate(BaseModel):
    title: Optional[str] = None
    company: Optional[str] = None
    raw_text: Optional[str] = None
    url: Optional[str] = None


class JDResponse(BaseModel):
    id: str
    title: str
    company: Optional[str] = None
    parsed_json: Optional[ParsedJDData] = None
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)
