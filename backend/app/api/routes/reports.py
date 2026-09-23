from fastapi import APIRouter, Depends, HTTPException, status, Response
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.exceptions import ResourceNotFoundException
from app.models.analysis_result import AnalysisResult
from app.repositories.analysis_repo import AnalysisRepository
from app.repositories.interview_repo import InterviewRepository
from app.schemas.report import FinalReportResponse
from app.api.deps import get_llm
from app.services.llm_client import BaseLLMClient
from app.services.report_service import ReportService

router = APIRouter(prefix="/reports", tags=["Reports & Roadmaps"])


@router.get("/{analysis_id}", response_model=FinalReportResponse)
async def get_final_report(
    analysis_id: str,
    db: Session = Depends(get_db),
    llm_client: BaseLLMClient = Depends(get_llm)
):
    """
    Generates and returns the consolidated final report and personalized career roadmap.
    """
    analysis_repo = AnalysisRepository(db)
    analysis = analysis_repo.get(analysis_id)
    if not analysis:
        raise ResourceNotFoundException("AnalysisResult", analysis_id)

    resume_data = analysis.resume.parsed_json if analysis.resume else {}
    jd_data = analysis.job_description.parsed_json if analysis.job_description else {}

    if not jd_data and analysis.role_key:
        from app.repositories.role_profile_repo import RoleProfileRepository
        from app.services.role_profile_loader import RoleProfileLoader
        role_repo = RoleProfileRepository(db)
        role = role_repo.get_by_role_key(analysis.role_key)
        if not role:
            role = RoleProfileLoader(db).get_role_by_key(analysis.role_key)
        if role:
            jd_data = {
                "job_title": role.display_name,
                "company": "Official Industry Profile (ESCO / O*NET)",
                "seniority": role.seniority or "mid",
                "domain": role.domain or "software_engineering"
            }
        else:
            jd_data = {
                "job_title": analysis.target_role or "Target Role",
                "company": "Industry Benchmark",
                "seniority": "mid",
                "domain": "software_engineering"
            }
    elif not jd_data:
        jd_data = {
            "job_title": analysis.target_role or "Target Role",
            "company": "Industry Benchmark",
            "seniority": "mid",
            "domain": "software_engineering"
        }

    interview_repo = InterviewRepository(db)
    sessions = interview_repo.get_by_analysis_id(analysis_id)
    latest_session = sessions[0] if sessions else None

    session_data = None
    if latest_session:
        session_data = {
            "id": latest_session.id,
            "analysis_result_id": latest_session.analysis_result_id,
            "target_role": latest_session.target_role,
            "difficulty": latest_session.difficulty,
            "question_count": latest_session.question_count,
            "status": latest_session.status,
            "interview_plan": latest_session.interview_plan,
            "generated_questions": latest_session.generated_questions,
            "answers": [
                {
                    "id": a.id,
                    "question_id": a.question_id,
                    "question_text": a.question_text,
                    "answer_text": a.answer_text,
                    "score": a.score,
                    "evaluation_json": a.evaluation_json,
                    "created_at": a.created_at
                }
                for a in latest_session.answers
            ],
            "overall_score": latest_session.overall_score,
            "summary_feedback": latest_session.summary_feedback,
            "created_at": latest_session.created_at
        }

    analysis_data = {
        "id": analysis.id,
        "resume_id": analysis.resume_id,
        "job_description_id": analysis.job_description_id,
        "target_role": analysis.target_role,
        "matched_skills": analysis.matched_skills,
        "weak_skills": analysis.weak_skills,
        "missing_skills": analysis.missing_skills,
        "related_partial_skills": analysis.related_partial_skills,
        "extra_skills": analysis.extra_skills,
        "gap_summary": analysis.gap_summary,
        "scores": analysis.scores,
        "explanations": analysis.explanations,
        "provenance": analysis.provenance or {},
        "created_at": analysis.created_at
    }

    report_service = ReportService(llm_client)
    report = await report_service.build_consolidated_report(
        analysis_data=analysis_data,
        resume_data=resume_data,
        jd_data=jd_data,
        interview_session_data=session_data
    )
    return report


@router.get("/{analysis_id}/download")
async def download_report_pdf(
    analysis_id: str,
    db: Session = Depends(get_db),
    llm_client: BaseLLMClient = Depends(get_llm)
):
    """
    Exports and streams the complete report as a downloadable styled PDF.
    """
    report_data = await get_final_report(analysis_id, db, llm_client)
    report_service = ReportService(llm_client)
    pdf_buffer = report_service.export_pdf(dict(report_data))

    headers = {
        "Content-Disposition": f'attachment; filename="interview_readiness_report_{analysis_id[:8]}.pdf"'
    }
    return Response(
        content=pdf_buffer.getvalue(),
        media_type="application/pdf",
        headers=headers
    )
