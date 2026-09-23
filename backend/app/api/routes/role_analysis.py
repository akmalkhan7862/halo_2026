from typing import List, Optional, Union
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.exceptions import ResourceNotFoundException
from app.models.resume import Resume
from app.repositories.resume_repo import ResumeRepository
from app.schemas.role_analysis import (
    RoleProfileSummary,
    RoleProfileDetail,
    RoleAnalysisRequest,
    SingleRoleAnalysisResponse,
    MultiRoleAnalysisResponse,
    RoleMatchResult
)
from app.api.deps import get_taxonomy_service
from app.services.taxonomy_service import TaxonomyService
from app.services.role_profile_loader import RoleProfileLoaderService
from app.services.role_matcher import RoleMatcherService

router = APIRouter(prefix="/roles", tags=["Taxonomy Target Roles"])


@router.get("", response_model=List[RoleProfileSummary])
def list_target_roles(db: Session = Depends(get_db)):
    """
    Returns the curated catalog of 10–15 target job roles derived from official
    ESCO and O*NET taxonomies. No manual Job Description needed.
    """
    loader = RoleProfileLoaderService(db)
    roles = loader.get_all_roles()

    summaries = []
    for r in roles:
        summaries.append({
            "id": str(r.id),
            "role_key": r.role_key,
            "display_name": r.display_name,
            "seniority": r.seniority,
            "domain": r.domain,
            "description": r.description,
            "required_skills_count": len(r.required_skills or []),
            "preferred_skills_count": len(r.preferred_skills or [])
        })
    return summaries


@router.get("/{role_key}", response_model=RoleProfileDetail)
def get_target_role_detail(role_key: str, db: Session = Depends(get_db)):
    """
    Returns full canonical specification, required and preferred skills, and source
    taxonomies (ESCO/O*NET) for a specific target role.
    """
    loader = RoleProfileLoaderService(db)
    role = loader.get_role_by_key(role_key)
    if not role:
        raise ResourceNotFoundException("RoleProfile", role_key)

    return {
        "id": str(role.id),
        "role_key": role.role_key,
        "display_name": role.display_name,
        "seniority": role.seniority,
        "domain": role.domain,
        "description": role.description,
        "sources": role.sources or [],
        "required_skills": role.required_skills or [],
        "preferred_skills": role.preferred_skills or [],
        "created_at": role.created_at
    }


@router.post("/analyze", response_model=Union[SingleRoleAnalysisResponse, MultiRoleAnalysisResponse])
def analyze_resume_against_roles(
    req: RoleAnalysisRequest,
    db: Session = Depends(get_db),
    taxonomy_service: TaxonomyService = Depends(get_taxonomy_service)
):
    """
    Compares candidate resume extracted skills directly with official ESCO/O*NET
    taxonomy role profiles. Eliminates the requirement of a manual Job Description.

    - If target_role_key is provided: Evaluates alignment for that role.
    - If target_role_key is omitted or 'all': Evaluates and ranks fit across all 12 roles.
    """
    resume_repo = ResumeRepository(db)
    resume = resume_repo.get(req.resume_id)
    if not resume:
        raise ResourceNotFoundException("Resume", req.resume_id)

    resume_data = resume.parsed_json or {}
    candidate_name = resume_data.get("contact", {}).get("name") or "Candidate"

    loader = RoleProfileLoaderService(db)
    matcher = RoleMatcherService(taxonomy_service)

    # Single role evaluation
    if req.target_role_key and req.target_role_key.strip().lower() != "all":
        role = loader.get_role_by_key(req.target_role_key.strip().lower())
        if not role:
            raise ResourceNotFoundException("RoleProfile", req.target_role_key)

        match_result = matcher.match_resume_to_role(resume_data, role)
        return {
            "resume_id": req.resume_id,
            "candidate_name": candidate_name,
            "role_analysis": match_result
        }

    # Multi-role evaluation (evaluates all 12 curated roles)
    all_roles = loader.get_all_roles()
    role_rankings: List[Dict] = []

    for role in all_roles:
        res = matcher.match_resume_to_role(resume_data, role)
        role_rankings.append(res)

    # Sort descending by fit score
    role_rankings.sort(key=lambda x: x["fit_score"], reverse=True)
    top_role = role_rankings[0]["display_name"] if role_rankings else "None"

    return {
        "resume_id": req.resume_id,
        "candidate_name": candidate_name,
        "total_roles_evaluated": len(role_rankings),
        "top_recommended_role": top_role,
        "role_rankings": role_rankings
    }
