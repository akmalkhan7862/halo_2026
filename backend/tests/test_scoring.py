import pytest
from app.services.scoring_engine import ScoringEngineService


def test_scoring_engine_breakdown_and_weights():
    engine = ScoringEngineService()

    matched_skills = [
        {"canonical_skill": "Python", "importance": "required"}
    ]
    weak_skills = [
        {"canonical_skill": "Docker", "importance": "preferred"}
    ]
    missing_skills = [
        {"canonical_skill": "Kubernetes", "importance": "required"}
    ]
    related_skills = [
        {"canonical_skill": "PostgreSQL", "related_to": "MySQL", "importance": "required"}
    ]

    resume_data = {
        "experience": [{"job_title": "Backend Dev", "bullets": ["Architected scalable APIs with Python"]}],
        "projects": [{"title": "Cloud API", "description": "Handled 5,000 req/s with 99.9% uptime", "technologies": ["Python"]}],
        "extracted_keywords": ["Python", "Docker", "APIs"],
        "summary": "Led software architecture and optimized latency."
    }

    jd_data = {
        "job_title": "Senior Backend Developer",
        "seniority": "senior",
        "keywords": ["Python", "Docker", "Kubernetes", "PostgreSQL"],
        "experience_requirements": {"minimum_years": 3, "detected_from_text": True}
    }

    scores = engine.compute_all_scores(
        matched_skills=matched_skills,
        weak_skills=weak_skills,
        missing_skills=missing_skills,
        related_partial_skills=related_skills,
        resume_data=resume_data,
        jd_data=jd_data
    )

    assert "overall_score" in scores
    assert 0.0 <= scores["overall_score"] <= 100.0

    for metric in ["skill_match_score", "experience_score", "project_score", "keyword_score", "seniority_score"]:
        assert metric in scores
        component = scores[metric]
        assert "score" in component
        assert "breakdown" in component
        assert len(component["breakdown"]) > 0
        # Check that reasons have "+/-" impact
        for b in component["breakdown"]:
            assert "reason" in b
            assert "impact" in b
