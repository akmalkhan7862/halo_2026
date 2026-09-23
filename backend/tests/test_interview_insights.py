import asyncio
import pytest
from app.services.interview_insights import InterviewInsightsService


def test_interview_insights_heuristic_derivation():
    service = InterviewInsightsService(llm_client=None)

    answers = [
        {
            "score": 85,
            "evaluation_json": {
                "score": 85,
                "verdict": "good",
                "strengths": [
                    "Clearly explained database connection pool lifecycle",
                    "Addressed transaction isolation levels and rollback semantics"
                ],
                "weaknesses": [
                    "Did not cite quantitative throughput metrics or latency numbers"
                ],
                "missing_points": [
                    "Connection leak monitoring"
                ],
                "suggested_improvement": "Structure your answer using STAR and explicitly specify pool size tuning formulas."
            }
        },
        {
            "score": 45,
            "evaluation_json": {
                "score": 45,
                "verdict": "weak",
                "strengths": [
                    "Recognized basic HTTP verb semantics"
                ],
                "weaknesses": [
                    "Limited depth in CI/CD concepts and pipeline design",
                    "Vague discussion of cloud deployment steps and tooling"
                ],
                "missing_points": [
                    "Automated rollback strategy",
                    "Kubernetes pod health checks"
                ],
                "suggested_improvement": "Practice describing concrete CI/CD pipelines with specific tools (e.g. GitHub Actions)."
            }
        }
    ]

    role_metadata = {
        "title": "Backend Developer",
        "display_name": "Backend Developer",
        "seniority": "mid",
        "domain": "software_engineering"
    }

    insights = asyncio.run(service.generate_insights(
        answers=answers,
        role_metadata=role_metadata,
        dimension_scores={"communication": 75, "structure_and_clarity": 60}
    ))

    assert "key_strengths" in insights
    assert len(insights["key_strengths"]) >= 2
    # Check that strengths are interview behaviors
    assert any("database" in s.lower() or "transaction" in s.lower() for s in insights["key_strengths"])

    assert "key_weaknesses" in insights
    assert len(insights["key_weaknesses"]) >= 2
    # Check that weaknesses reflect interview gaps
    assert any("ci/cd" in w.lower() or "cloud" in w.lower() or "metric" in w.lower() or "connection" in w.lower() for w in insights["key_weaknesses"])

    assert "recommendations" in insights
    assert len(insights["recommendations"]) >= 1
    assert any("ci/cd" in r.lower() or "star" in r.lower() or "metric" in r.lower() for r in insights["recommendations"])

    assert "communication_feedback" in insights
    assert "strengths" in insights["communication_feedback"]
    assert "improvements" in insights["communication_feedback"]
    assert len(insights["communication_feedback"]["improvements"]) >= 1


def test_interview_insights_empty():
    service = InterviewInsightsService(llm_client=None)
    role_metadata = {"title": "Backend Developer", "seniority": "mid"}
    insights = asyncio.run(service.generate_insights([], role_metadata))

    assert "key_strengths" in insights
    assert "key_weaknesses" in insights
    assert "recommendations" in insights
    assert "communication_feedback" in insights
