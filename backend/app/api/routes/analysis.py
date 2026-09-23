import uuid
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.exceptions import ResourceNotFoundException
from app.models.resume import Resume
from app.models.job_description import JobDescription
from app.models.analysis_result import AnalysisResult
from app.models.role_profile import RoleProfile
from app.models.interview_session import InterviewSession
from app.repositories.analysis_repo import AnalysisRepository
from app.repositories.resume_repo import ResumeRepository
from app.repositories.jd_repo import JobDescriptionRepository
from app.repositories.role_profile_repo import RoleProfileRepository
from app.repositories.interview_repo import InterviewRepository
from app.schemas.analysis import AnalysisRequest, AnalysisResponse
from app.schemas.role_fit_interview import RoleFitInterviewRequest, RoleFitInterviewResponse
from app.schemas.manual_jd_analysis import ManualJDAnalysisRequest, ManualJDAnalysisResponse
from app.api.deps import (
    get_taxonomy_service,
    get_skill_matcher,
    get_gap_analyzer,
    get_scoring_engine,
    get_llm
)
from app.services.taxonomy_service import TaxonomyService
from app.services.skill_matcher import SkillMatcherService
from app.services.jd_parser import JobDescriptionParserService
from app.services.gap_analyzer import GapAnalyzerService
from app.services.scoring_engine import ScoringEngineService
from app.services.role_matcher import RoleMatcherService
from app.services.role_profile_loader import RoleProfileLoader
from app.services.interview_service import InterviewService
from app.services.llm_client import BaseLLMClient
from app.services.skill_gap_service import SkillGapService
from app.services.learning_roadmap_service import LearningRoadmapService
from app.schemas.gap_analysis import SkillGapAnalysisResponse
from app.schemas.learning_roadmap import PersonalizedRoadmapResponse

router = APIRouter(prefix="/analysis", tags=["Skill Gap Analysis"])


@router.post("", response_model=AnalysisResponse, status_code=status.HTTP_201_CREATED)
def run_analysis(
    req: AnalysisRequest,
    db: Session = Depends(get_db),
    skill_matcher: SkillMatcherService = Depends(get_skill_matcher),
    gap_analyzer: GapAnalyzerService = Depends(get_gap_analyzer),
    scoring_engine: ScoringEngineService = Depends(get_scoring_engine)
):
    """
    Executes deep skill gap analysis comparing parsed resume with job description requirements.
    Calculates explainable 5-factor scores and synthesizes actionable gap summary.
    """
    resume_repo = ResumeRepository(db)
    resume = resume_repo.get(req.resume_id)
    if not resume:
        raise ResourceNotFoundException("Resume", req.resume_id)

    jd_repo = JobDescriptionRepository(db)
    jd = jd_repo.get(req.job_description_id)
    if not jd:
        raise ResourceNotFoundException("JobDescription", req.job_description_id)

    resume_data = resume.parsed_json or {}
    jd_data = jd.parsed_json or {}

    target_role = req.target_role or jd_data.get("job_title") or jd.title or "Target Role"

    # 1. Match skills and classify
    match_result = skill_matcher.match_skills(
        resume_skills=resume_data.get("skills", []),
        jd_required_skills=jd_data.get("required_skills", []),
        jd_preferred_skills=jd_data.get("preferred_skills", []),
        resume_experience=resume_data.get("experience", []),
        resume_projects=resume_data.get("projects", [])
    )

    matched_skills = match_result["matched_skills"]
    weak_skills = match_result["weak_skills"]
    missing_skills = match_result["missing_skills"]
    related_partial = match_result["related_partial_skills"]
    extra_skills = match_result["extra_skills"]

    # 2. Gap summary
    gap_summary = gap_analyzer.generate_gap_summary(
        target_role=target_role,
        seniority=jd_data.get("seniority", "mid"),
        matched_skills=matched_skills,
        weak_skills=weak_skills,
        missing_skills=missing_skills,
        related_partial_skills=related_partial,
        extra_skills=extra_skills
    )

    # 3. Compute 5-factor explainable scores
    scores = scoring_engine.compute_all_scores(
        matched_skills=matched_skills,
        weak_skills=weak_skills,
        missing_skills=missing_skills,
        related_partial_skills=related_partial,
        resume_data=resume_data,
        jd_data=jd_data
    )

    provenance = {
        "parser": "PyMuPDF+python-docx+spaCy",
        "taxonomy_sources": req.taxonomy_sources,
        "scoring_version": "v1.0.0",
        "timestamp": datetime.now(timezone.utc).isoformat()
    }

    analysis_id = str(uuid.uuid4())
    analysis_record = AnalysisResult(
        id=analysis_id,
        resume_id=req.resume_id,
        job_description_id=req.job_description_id,
        target_role=target_role,
        matched_skills=matched_skills,
        weak_skills=weak_skills,
        missing_skills=missing_skills,
        related_partial_skills=related_partial,
        extra_skills=extra_skills,
        gap_summary=gap_summary,
        scores=scores,
        explanations={
            "scoring_logic": "Explainable weighted multi-factor scoring model.",
            "citations_included": True
        },
        provenance=provenance
    )

    analysis_repo = AnalysisRepository(db)
    created = analysis_repo.create(analysis_record)
    return created


@router.post("/role-fit-with-interview", response_model=RoleFitInterviewResponse, status_code=status.HTTP_201_CREATED)
async def run_role_fit_with_interview(
    req: RoleFitInterviewRequest,
    db: Session = Depends(get_db),
    taxonomy_service: TaxonomyService = Depends(get_taxonomy_service),
    scoring_engine: ScoringEngineService = Depends(get_scoring_engine),
    llm_client: BaseLLMClient = Depends(get_llm)
):
    """
    Unifies role-fit evaluation and mock interview question generation into a single call.
    Compares candidate resume with preloaded ESCO/O*NET canonical requirements (no manual JD needed),
    computes explainable gap analysis and scores, and generates 7-10 resume-grounded mock interview questions.
    """
    resume_repo = ResumeRepository(db)
    resume = resume_repo.get(req.resume_id)
    if not resume:
        raise ResourceNotFoundException("Resume", req.resume_id)

    role_repo = RoleProfileRepository(db)
    role = role_repo.get_by_role_key(req.role_key)
    if not role:
        loader = RoleProfileLoader(db)
        role = loader.get_role_by_key(req.role_key)
    if not role:
        raise ResourceNotFoundException("RoleProfile", req.role_key)

    resume_data = resume.parsed_json or {}
    role_matcher = RoleMatcherService(taxonomy_service)
    match_result = role_matcher.match_resume_to_role(resume_data, role)

    matched_skills = match_result["matched_skills"]
    weak_skills = match_result["weak_skills"]
    missing_skills = match_result["missing_skills"]
    related_partial = match_result["related_partial_skills"]
    extra_skills = match_result["extra_skills"]
    gap_summary = match_result["gap_summary"]

    # Compute coverage ratio
    total_reqs = len(matched_skills) + len(weak_skills) + len(missing_skills) + len(related_partial)
    coverage_ratio = round((len(matched_skills) + 0.6 * len(related_partial)) / max(total_reqs, 1), 2)
    gap_summary["coverage_ratio"] = coverage_ratio
    gap_summary["overall_fit"] = gap_summary.get("overall_fit") or gap_summary.get("overall_readiness", "moderate")
    gap_summary["top_missing_skills"] = [s.get("canonical_skill") for s in missing_skills if s.get("canonical_skill")]

    # Build role-based JD data for scoring and interview generation
    role_jd_data = {
        "job_title": role.display_name,
        "seniority": role.seniority or "mid",
        "domain": role.domain or "software_engineering",
        "required_skills": [{"canonical_skill": s} for s in (role.required_skills or [])],
        "preferred_skills": [{"canonical_skill": s} for s in (role.preferred_skills or [])],
        "keywords": (role.required_skills or []) + (role.preferred_skills or []),
        "company": "Official Industry Profile (ESCO / O*NET)"
    }

    # Compute 5-factor explainable scores
    scores = scoring_engine.compute_all_scores(
        matched_skills=matched_skills,
        weak_skills=weak_skills,
        missing_skills=missing_skills,
        related_partial_skills=related_partial,
        resume_data=resume_data,
        jd_data=role_jd_data
    )

    # Compute role-aware, resume-grounded skill gap analysis
    skill_gap_service = SkillGapService()
    gap_analysis = skill_gap_service.analyze_skill_gaps(
        role_key=role.role_key,
        display_name=role.display_name,
        seniority=role.seniority or "mid",
        domain=role.domain or "software_engineering",
        required_skills=role.required_skills or [],
        preferred_skills=role.preferred_skills or [],
        resume_data=resume_data,
        matched_skills=matched_skills,
        weak_skills=weak_skills,
        missing_skills=missing_skills,
        related_partial_skills=related_partial,
        extra_skills=extra_skills
    )

    # Compute personalized learning roadmap
    learning_roadmap_service = LearningRoadmapService()
    learning_roadmap = learning_roadmap_service.generate_roadmap(
        role_key=role.role_key,
        display_name=role.display_name,
        seniority=role.seniority or "mid",
        domain=role.domain or "software_engineering",
        gap_analysis=gap_analysis,
        resume_data=resume_data
    )

    analysis_id = str(uuid.uuid4())
    analysis_record = AnalysisResult(
        id=analysis_id,
        resume_id=req.resume_id,
        job_description_id=None,
        role_key=role.role_key,
        target_role=role.display_name,
        matched_skills=matched_skills,
        weak_skills=weak_skills,
        missing_skills=missing_skills,
        related_partial_skills=related_partial,
        extra_skills=extra_skills,
        gap_summary=gap_summary,
        gap_analysis=gap_analysis,
        learning_roadmap=learning_roadmap,
        scores=scores,
        explanations={
            "scoring_logic": "Explainable weighted multi-factor scoring model against canonical taxonomy standard.",
            "citations_included": True
        },
        provenance={
            "parser": "PyMuPDF+python-docx+spaCy",
            "taxonomy_sources": ["ESCO", "O*NET"],
            "scoring_version": "v1.0.0",
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    )

    analysis_repo = AnalysisRepository(db)
    analysis_repo.create(analysis_record)

    # Generate 7-10 resume-grounded mock interview questions
    interview_service = InterviewService(llm_client)
    difficulty = req.difficulty or "medium"
    question_count = req.question_count or 8

    generated = await interview_service.generate_interview_session(
        target_role=role.display_name,
        difficulty=difficulty,
        question_count=question_count,
        resume_data=resume_data,
        jd_data=role_jd_data,
        matched_skills=matched_skills,
        weak_skills=weak_skills,
        missing_skills=missing_skills
    )

    session_id = str(uuid.uuid4())
    session = InterviewSession(
        id=session_id,
        analysis_result_id=analysis_id,
        target_role=role.display_name,
        difficulty=difficulty,
        question_count=len(generated.get("questions", [])),
        status="in_progress",
        interview_plan=generated.get("interview_plan", {}),
        generated_questions=generated.get("questions", []),
        summary_feedback={}
    )
    interview_repo = InterviewRepository(db)
    interview_repo.create(session)

    return {
        "analysis_id": analysis_id,
        "mode": "taxonomy_role",
        "role_key": role.role_key,
        "display_name": role.display_name,
        "role_display_name": role.display_name,
        "target_role": role.display_name,
        "matched_skills": matched_skills,
        "missing_skills": missing_skills,
        "weak_skills": weak_skills,
        "extra_skills": extra_skills,
        "coverage_ratio": coverage_ratio,
        "gap_summary": gap_summary,
        "gap_analysis": gap_analysis,
        "learning_roadmap": learning_roadmap,
        "scores": scores,
        "interview": {
            "session_id": session_id,
            "questions": session.generated_questions
        }
    }


@router.post("/manual-jd", response_model=ManualJDAnalysisResponse, status_code=status.HTTP_201_CREATED)
async def run_manual_jd_analysis(
    req: ManualJDAnalysisRequest,
    db: Session = Depends(get_db),
    taxonomy_service: TaxonomyService = Depends(get_taxonomy_service),
    scoring_engine: ScoringEngineService = Depends(get_scoring_engine),
    skill_matcher: SkillMatcherService = Depends(get_skill_matcher),
    gap_analyzer: GapAnalyzerService = Depends(get_gap_analyzer),
    llm_client: BaseLLMClient = Depends(get_llm)
):
    """
    MODE 2: Manual Job Description Analysis.
    Parses custom user-provided Job Description text, extracts required & preferred skills,
    computes explainable 5-factor fit scores, produces skill gap summary,
    and generates 7-10 resume-grounded mock interview questions.
    """
    resume_repo = ResumeRepository(db)
    resume = resume_repo.get(req.resume_id)
    if not resume:
        raise ResourceNotFoundException("Resume", req.resume_id)

    resume_data = resume.parsed_json or {}

    # 1. Parse raw JD text
    jd_parser = JobDescriptionParserService(taxonomy_service)
    parsed_jd = jd_parser.parse(req.jd_text)

    role_display_name = parsed_jd.get("job_title") or "Custom Role from JD"
    seniority = parsed_jd.get("seniority") or "mid"
    domain = parsed_jd.get("domain") or "software_engineering"

    # 2. Match candidate skills against JD requirements
    match_result = skill_matcher.match_skills(
        resume_skills=resume_data.get("skills", []),
        jd_required_skills=parsed_jd.get("required_skills", []),
        jd_preferred_skills=parsed_jd.get("preferred_skills", []),
        resume_experience=resume_data.get("experience", []),
        resume_projects=resume_data.get("projects", [])
    )

    matched_skills = match_result["matched_skills"]
    weak_skills = match_result["weak_skills"]
    missing_skills = match_result["missing_skills"]
    related_partial = match_result["related_partial_skills"]
    extra_skills = match_result["extra_skills"]

    # 3. Compute coverage ratio & gap summary
    total_reqs = len(matched_skills) + len(weak_skills) + len(missing_skills) + len(related_partial)
    coverage_ratio = round((len(matched_skills) + 0.6 * len(related_partial)) / max(total_reqs, 1), 2)

    gap_summary = gap_analyzer.generate_gap_summary(
        target_role=role_display_name,
        seniority=seniority,
        matched_skills=matched_skills,
        weak_skills=weak_skills,
        missing_skills=missing_skills,
        related_partial_skills=related_partial,
        extra_skills=extra_skills
    )
    gap_summary["coverage_ratio"] = coverage_ratio
    gap_summary["overall_fit"] = gap_summary.get("overall_fit") or gap_summary.get("overall_readiness", "moderate")
    gap_summary["top_missing_skills"] = [s.get("canonical_skill") for s in missing_skills if s.get("canonical_skill")]
    if not gap_summary.get("recommended_focus_areas"):
        gap_summary["recommended_focus_areas"] = [s.get("canonical_skill") for s in missing_skills[:4] if s.get("canonical_skill")]

    # 4. Compute 5-factor explainable scores
    scores = scoring_engine.compute_all_scores(
        matched_skills=matched_skills,
        weak_skills=weak_skills,
        missing_skills=missing_skills,
        related_partial_skills=related_partial,
        resume_data=resume_data,
        jd_data=parsed_jd
    )

    # 5. Compute role-aware skill gap analysis & learning roadmap
    required_names = [s["canonical_skill"] for s in parsed_jd.get("required_skills", [])]
    preferred_names = [s["canonical_skill"] for s in parsed_jd.get("preferred_skills", [])]

    skill_gap_service = SkillGapService()
    gap_analysis = skill_gap_service.analyze_skill_gaps(
        role_key="manual_jd",
        display_name=role_display_name,
        seniority=seniority,
        domain=domain,
        required_skills=required_names,
        preferred_skills=preferred_names,
        resume_data=resume_data,
        matched_skills=matched_skills,
        weak_skills=weak_skills,
        missing_skills=missing_skills,
        related_partial_skills=related_partial,
        extra_skills=extra_skills
    )

    learning_roadmap_service = LearningRoadmapService()
    learning_roadmap = learning_roadmap_service.generate_roadmap(
        role_key="manual_jd",
        display_name=role_display_name,
        seniority=seniority,
        domain=domain,
        gap_analysis=gap_analysis,
        resume_data=resume_data
    )

    # 6. Save AnalysisResult to DB
    analysis_id = str(uuid.uuid4())
    analysis_record = AnalysisResult(
        id=analysis_id,
        resume_id=req.resume_id,
        job_description_id=None,
        role_key=None,
        target_role=role_display_name,
        matched_skills=matched_skills,
        weak_skills=weak_skills,
        missing_skills=missing_skills,
        related_partial_skills=related_partial,
        extra_skills=extra_skills,
        gap_summary=gap_summary,
        gap_analysis=gap_analysis,
        learning_roadmap=learning_roadmap,
        scores=scores,
        explanations={
            "scoring_logic": "Explainable weighted multi-factor scoring model against manual Job Description.",
            "mode": "manual_jd",
            "role_display_name": role_display_name
        },
        provenance={
            "parser": "PyMuPDF+python-docx+spaCy",
            "source": "manual_jd",
            "scoring_version": "v1.0.0",
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    )

    analysis_repo = AnalysisRepository(db)
    analysis_repo.create(analysis_record)

    # 7. Generate 7-10 resume-grounded mock interview questions
    interview_service = InterviewService(llm_client)
    difficulty = req.difficulty or "medium"
    question_count = req.question_count or 8

    generated = await interview_service.generate_interview_session(
        target_role=role_display_name,
        difficulty=difficulty,
        question_count=question_count,
        resume_data=resume_data,
        jd_data=parsed_jd,
        matched_skills=matched_skills,
        weak_skills=weak_skills,
        missing_skills=missing_skills
    )

    session_id = str(uuid.uuid4())
    session = InterviewSession(
        id=session_id,
        analysis_result_id=analysis_id,
        target_role=role_display_name,
        difficulty=difficulty,
        question_count=len(generated.get("questions", [])),
        status="in_progress",
        interview_plan=generated.get("interview_plan", {}),
        generated_questions=generated.get("questions", []),
        summary_feedback={}
    )
    interview_repo = InterviewRepository(db)
    interview_repo.create(session)

    return {
        "analysis_id": analysis_id,
        "mode": "manual_jd",
        "role_key": None,
        "role_display_name": role_display_name,
        "display_name": role_display_name,
        "target_role": role_display_name,
        "matched_skills": matched_skills,
        "missing_skills": missing_skills,
        "weak_skills": weak_skills,
        "extra_skills": extra_skills,
        "coverage_ratio": coverage_ratio,
        "scores": scores,
        "gap_summary": gap_summary,
        "gap_analysis": gap_analysis,
        "learning_roadmap": learning_roadmap,
        "interview": {
            "session_id": session_id,
            "questions": session.generated_questions
        }
    }


@router.get("/{analysis_id}", response_model=AnalysisResponse)
def get_analysis(analysis_id: str, db: Session = Depends(get_db)):
    repo = AnalysisRepository(db)
    analysis = repo.get(analysis_id)
    if not analysis:
        raise ResourceNotFoundException("AnalysisResult", analysis_id)
    return analysis


@router.get("/{analysis_id}/gap", response_model=SkillGapAnalysisResponse)
def get_gap_analysis(analysis_id: str, db: Session = Depends(get_db)):
    """
    Returns the role-aware, resume-grounded, explainable skill gap analysis.
    """
    repo = AnalysisRepository(db)
    analysis = repo.get(analysis_id)
    if not analysis:
        raise ResourceNotFoundException("AnalysisResult", analysis_id)

    if analysis.gap_analysis and "skill_gap_details" in analysis.gap_analysis:
        return analysis.gap_analysis

    # Regenerate if not stored
    resume_data = analysis.resume.parsed_json if analysis.resume else {}
    role_key = analysis.role_key or "backend_developer"
    role_repo = RoleProfileRepository(db)
    role = role_repo.get_by_role_key(role_key)
    if not role:
        role = RoleProfileLoader(db).get_role_by_key(role_key)

    req_skills = role.required_skills if role else []
    pref_skills = role.preferred_skills if role else []
    display_name = role.display_name if role else (analysis.target_role or "Software Engineer")
    seniority = role.seniority if role else "mid"
    domain = role.domain if role else "software_engineering"

    gap_service = SkillGapService()
    gap_result = gap_service.analyze_skill_gaps(
        role_key=role_key,
        display_name=display_name,
        seniority=seniority,
        domain=domain,
        required_skills=req_skills,
        preferred_skills=pref_skills,
        resume_data=resume_data,
        matched_skills=analysis.matched_skills or [],
        weak_skills=analysis.weak_skills or [],
        missing_skills=analysis.missing_skills or [],
        related_partial_skills=analysis.related_partial_skills or [],
        extra_skills=analysis.extra_skills or []
    )
    analysis.gap_analysis = gap_result
    db.commit()
    return gap_result


@router.get("/{analysis_id}/roadmap", response_model=PersonalizedRoadmapResponse)
def get_learning_roadmap(analysis_id: str, db: Session = Depends(get_db)):
    """
    Returns the personalized learning roadmap focused on the candidate's missing/weak skills.
    """
    repo = AnalysisRepository(db)
    analysis = repo.get(analysis_id)
    if not analysis:
        raise ResourceNotFoundException("AnalysisResult", analysis_id)

    if analysis.learning_roadmap and "learning_roadmap" in analysis.learning_roadmap:
        return analysis.learning_roadmap

    gap = analysis.gap_analysis
    if not gap or "skill_gap_details" not in gap:
        gap = get_gap_analysis(analysis_id, db)
        if hasattr(gap, "model_dump"):
            gap = gap.model_dump()

    resume_data = analysis.resume.parsed_json if analysis.resume else {}
    role_key = analysis.role_key or "backend_developer"
    role_repo = RoleProfileRepository(db)
    role = role_repo.get_by_role_key(role_key)
    if not role:
        role = RoleProfileLoader(db).get_role_by_key(role_key)

    display_name = role.display_name if role else (analysis.target_role or "Software Engineer")
    seniority = role.seniority if role else "mid"
    domain = role.domain if role else "software_engineering"

    roadmap_service = LearningRoadmapService()
    roadmap_result = roadmap_service.generate_roadmap(
        role_key=role_key,
        display_name=display_name,
        seniority=seniority,
        domain=domain,
        gap_analysis=gap if isinstance(gap, dict) else dict(gap),
        resume_data=resume_data
    )
    analysis.learning_roadmap = roadmap_result
    db.commit()
    return roadmap_result
