from typing import List, Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict


class ContactInfo(BaseModel):
    name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    linkedin: Optional[str] = None
    github: Optional[str] = None
    location: Optional[str] = None


class ExtractedSkill(BaseModel):
    raw_text: str
    canonical_skill: str
    taxonomy_source: str = "custom"
    taxonomy_id: Optional[str] = None
    confidence: float = 1.0
    evidence: List[str] = Field(default_factory=list)


class ExtractedExperience(BaseModel):
    job_title: Optional[str] = None
    organization: Optional[str] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    duration_months: Optional[int] = None
    bullets: List[str] = Field(default_factory=list)
    skills: List[str] = Field(default_factory=list)


class ExtractedProject(BaseModel):
    title: str
    description: Optional[str] = None
    technologies: List[str] = Field(default_factory=list)
    outcomes: List[str] = Field(default_factory=list)
    skills: List[str] = Field(default_factory=list)


class ExtractedEducation(BaseModel):
    degree: Optional[str] = None
    institution: Optional[str] = None
    graduation_year: Optional[str] = None
    gpa: Optional[str] = None


class ExtractedCertification(BaseModel):
    name: str
    issuer: Optional[str] = None
    year: Optional[str] = None


class ParsedResumeData(BaseModel):
    contact: ContactInfo = Field(default_factory=ContactInfo)
    summary: Optional[str] = None
    skills: List[ExtractedSkill] = Field(default_factory=list)
    unmapped_skills: List[str] = Field(default_factory=list)
    experience: List[ExtractedExperience] = Field(default_factory=list)
    projects: List[ExtractedProject] = Field(default_factory=list)
    education: List[ExtractedEducation] = Field(default_factory=list)
    certifications: List[ExtractedCertification] = Field(default_factory=list)
    extracted_keywords: List[str] = Field(default_factory=list)
    raw_text_length: int = 0


class ResumeUploadResponse(BaseModel):
    resume_id: str
    original_filename: str
    file_type: str
    status: str
    message: str


class ResumeDetailResponse(BaseModel):
    id: str
    original_filename: str
    file_type: str
    status: str
    parsed_json: Optional[ParsedResumeData] = None
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)


class ResumeStatusResponse(BaseModel):
    id: str
    status: str
    filename: str
