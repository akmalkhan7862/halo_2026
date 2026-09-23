import asyncio
import pytest
from app.services.llm_client import DeterministicMockLLMClient
from app.services.interview_service import InterviewService
from app.services.answer_evaluator import AnswerEvaluatorService


def test_interview_question_generation():
    llm = DeterministicMockLLMClient()
    service = InterviewService(llm)

    resume_data = {
        "summary": "Experienced FastAPI backend engineer.",
        "projects": [{"title": "API Gateway", "technologies": ["FastAPI", "PostgreSQL"]}],
        "experience": [{"job_title": "Backend Dev", "bullets": ["Built microservices"]}]
    }
    jd_data = {
        "job_title": "Backend Developer",
        "seniority": "mid",
        "required_skills": [{"canonical_skill": "FastAPI"}],
        "domain": "software_engineering"
    }

    result = asyncio.run(service.generate_interview_session(
        target_role="Backend Developer",
        difficulty="medium",
        question_count=8,
        resume_data=resume_data,
        jd_data=jd_data,
        matched_skills=[{"canonical_skill": "FastAPI"}],
        weak_skills=[],
        missing_skills=[{"canonical_skill": "Kubernetes"}]
    ))

    assert "questions" in result
    questions = result["questions"]
    assert len(questions) >= 7

    # Ensure questions are resume-specific and not generic "Tell me about yourself"
    for q in questions:
        assert "question_text" in q
        assert "expected_answer_points" in q
        assert "tell me about yourself" not in q["question_text"].lower()


def test_answer_evaluator():
    llm = DeterministicMockLLMClient()
    evaluator = AnswerEvaluatorService(llm)

    question = {
        "question_id": "q1",
        "type": "technical",
        "question_text": "How do you manage database connections in FastAPI?",
        "expected_answer_points": ["Async connection pool", "Depends with yield"]
    }
    answer = "We used asyncpg and created a session dependency using yield in FastAPI to ensure proper cleanup."

    evaluation = asyncio.run(evaluator.evaluate_answer(question, answer))
    assert "score" in evaluation
    assert "verdict" in evaluation
    assert "strengths" in evaluation
    assert "follow_up_question" in evaluation
