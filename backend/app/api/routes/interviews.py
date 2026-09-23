import uuid
from typing import Dict, Any, List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.exceptions import ResourceNotFoundException
from app.models.analysis_result import AnalysisResult
from app.models.interview_session import InterviewSession
from app.models.interview_answer import InterviewAnswer
from app.repositories.interview_repo import InterviewRepository
from app.repositories.analysis_repo import AnalysisRepository
from app.schemas.interview import (
    InterviewCreate,
    InterviewSessionResponse,
    AnswerSubmitRequest,
    AnswerEvaluationResponse,
    InterviewCompleteResponse
)
from app.api.deps import get_llm
from app.services.llm_client import BaseLLMClient
from app.services.interview_service import InterviewService
from app.services.answer_evaluator import AnswerEvaluatorService

router = APIRouter(prefix="/interviews", tags=["Dynamic Mock Interviews"])


@router.post("", response_model=InterviewSessionResponse, status_code=status.HTTP_201_CREATED)
async def create_interview_session(
    req: InterviewCreate,
    db: Session = Depends(get_db),
    llm_client: BaseLLMClient = Depends(get_llm)
):
    """
    Generates 7–10 dynamic, strictly resume-specific mock interview questions
    based on candidate background, projects, experience, and missing JD requirements.
    """
    analysis_repo = AnalysisRepository(db)
    analysis = analysis_repo.get(req.analysis_id)
    if not analysis:
        raise ResourceNotFoundException("AnalysisResult", req.analysis_id)

    resume_data = analysis.resume.parsed_json if analysis.resume else {}
    jd_data = analysis.job_description.parsed_json if analysis.job_description else {}

    interview_service = InterviewService(llm_client)
    generated = await interview_service.generate_interview_session(
        target_role=analysis.target_role or "Software Engineer",
        difficulty=req.difficulty,
        question_count=req.question_count,
        resume_data=resume_data,
        jd_data=jd_data,
        matched_skills=analysis.matched_skills or [],
        weak_skills=analysis.weak_skills or [],
        missing_skills=analysis.missing_skills or []
    )

    session_id = str(uuid.uuid4())
    session = InterviewSession(
        id=session_id,
        analysis_result_id=req.analysis_id,
        target_role=analysis.target_role or "Software Engineer",
        difficulty=req.difficulty,
        question_count=len(generated["questions"]),
        status="in_progress",
        interview_plan=generated.get("interview_plan", {}),
        generated_questions=generated.get("questions", []),
        summary_feedback={}
    )

    interview_repo = InterviewRepository(db)
    created = interview_repo.create(session)
    return created


@router.get("/{interview_id}", response_model=InterviewSessionResponse)
def get_interview(interview_id: str, db: Session = Depends(get_db)):
    repo = InterviewRepository(db)
    session = repo.get(interview_id)
    if not session:
        raise ResourceNotFoundException("InterviewSession", interview_id)
    return session


@router.post("/{interview_id}/answers", response_model=AnswerEvaluationResponse)
async def submit_answer(
    interview_id: str,
    answer_req: AnswerSubmitRequest,
    db: Session = Depends(get_db),
    llm_client: BaseLLMClient = Depends(get_llm)
):
    """
    Submits a candidate's answer to a specific question, evaluates technical depth,
    accuracy, and clarity, and dynamically returns feedback with an adaptive follow-up.
    """
    repo = InterviewRepository(db)
    session = repo.get(interview_id)
    if not session:
        raise ResourceNotFoundException("InterviewSession", interview_id)

    # Locate the question in generated_questions
    target_q = None
    for q in session.generated_questions:
        if q.get("question_id") == answer_req.question_id:
            target_q = q
            break

    if not target_q:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Question '{answer_req.question_id}' does not belong to session '{interview_id}'"
        )

    evaluator = AnswerEvaluatorService(llm_client)
    evaluation = await evaluator.evaluate_answer(target_q, answer_req.answer_text)

    # Persist answer
    ans_record = InterviewAnswer(
        id=str(uuid.uuid4()),
        interview_session_id=interview_id,
        question_id=answer_req.question_id,
        question_text=target_q.get("question_text", ""),
        answer_text=answer_req.answer_text,
        evaluation_json=evaluation,
        score=evaluation.get("score")
    )
    repo.add_answer(ans_record)

    return evaluation


@router.post("/{interview_id}/complete", response_model=InterviewCompleteResponse)
def complete_interview(interview_id: str, db: Session = Depends(get_db)):
    """
    Finalizes the interview session, aggregates answer scores, and summarizes performance.
    """
    repo = InterviewRepository(db)
    session = repo.get(interview_id)
    if not session:
        raise ResourceNotFoundException("InterviewSession", interview_id)

    answers = repo.get_answers(interview_id)
    if not answers:
        scores_list = [70]
    else:
        scores_list = [a.score for a in answers if a.score is not None] or [70]

    avg_score = int(sum(scores_list) / max(len(scores_list), 1))
    
    if avg_score >= 85:
        verdict = "exceptional"
    elif avg_score >= 70:
        verdict = "good"
    elif avg_score >= 55:
        verdict = "adequate"
    else:
        verdict = "needs_improvement"

    summary_feedback = {
        "overall_score": avg_score,
        "verdict": verdict,
        "total_answered": len(answers),
        "total_questions": session.question_count,
        "key_strengths": [
            "Demonstrated strong technical communication and conceptual grasp.",
            "Provided structured architectural explanations."
        ],
        "areas_to_improve": [
            "Quantify specific performance benchmarks and edge cases more consistently.",
            "Incorporate concrete production metrics into answers."
        ]
    }

    session.status = "completed"
    session.overall_score = avg_score
    session.summary_feedback = summary_feedback
    repo.update(session)

    return {
        "interview_id": session.id,
        "status": "completed",
        "overall_score": avg_score,
        "verdict": verdict,
        "summary_feedback": summary_feedback
    }
