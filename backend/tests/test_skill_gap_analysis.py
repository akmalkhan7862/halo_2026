import os
import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.services.skill_gap_service import SkillGapService

client = TestClient(app)
FIXTURES_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "fixtures")


def test_skill_gap_service_unit():
    service = SkillGapService()

    resume_data = {
        "skills": [
            {"canonical_skill": "FastAPI", "evidence": ["Built REST APIs with FastAPI"]},
            {"canonical_skill": "PostgreSQL", "evidence": ["Managed PostgreSQL database"]},
            {"canonical_skill": "Docker", "evidence": ["Listed under skills"]}
        ],
        "projects": [
            {
                "title": "E-commerce Backend",
                "technologies": ["FastAPI", "PostgreSQL"],
                "outcomes": ["Built high throughput REST APIs using FastAPI and PostgreSQL"]
            }
        ],
        "experience": [
            {
                "job_title": "Backend Intern",
                "organization": "CloudWave Systems",
                "bullets": ["Developed microservices with FastAPI and optimized PostgreSQL indexing"],
                "skills": ["FastAPI", "PostgreSQL"]
            }
        ],
        "certifications": [],
        "summary": "Familiar with containerization and Docker"
    }

    required_skills = ["FastAPI", "PostgreSQL", "CI/CD"]
    preferred_skills = ["Docker", "Kubernetes"]

    matched_skills = [
        {"canonical_skill": "FastAPI", "importance": "required"},
        {"canonical_skill": "PostgreSQL", "importance": "required"}
    ]
    weak_skills = [
        {"canonical_skill": "Docker", "importance": "preferred"}
    ]
    missing_skills = [
        {"canonical_skill": "CI/CD", "importance": "required"},
        {"canonical_skill": "Kubernetes", "importance": "preferred"}
    ]
    related_partial_skills = []

    res = service.analyze_skill_gaps(
        role_key="backend_developer",
        display_name="Backend Developer",
        seniority="mid",
        domain="software_engineering",
        required_skills=required_skills,
        preferred_skills=preferred_skills,
        resume_data=resume_data,
        matched_skills=matched_skills,
        weak_skills=weak_skills,
        missing_skills=missing_skills,
        related_partial_skills=related_partial_skills
    )

    assert res["role_key"] == "backend_developer"
    assert res["display_name"] == "Backend Developer"
    assert res["coverage_ratio"] == 0.4  # 2 matched out of 5 total
    assert res["required_coverage"] == 0.67  # 2 matched out of 3 required
    assert res["preferred_coverage"] == 0.0  # 0 matched out of 2 preferred

    details = {d["skill"]: d for d in res["skill_gap_details"]}
    assert "FastAPI" in details
    assert details["FastAPI"]["status"] == "matched"
    assert len(details["FastAPI"]["evidence"]) > 0
    assert "FastAPI" in details["FastAPI"]["explanation"]

    assert "CI/CD" in details
    assert details["CI/CD"]["status"] == "missing"
    assert details["CI/CD"]["evidence"] == []
    assert "No CI/CD" in details["CI/CD"]["explanation"]

    assert "Docker" in details
    assert details["Docker"]["status"] == "weak"
    assert len(details["Docker"]["evidence"]) > 0

    assert "CI/CD" in res["critical_missing_skills"]
    assert len(res["quick_wins"]) >= 1
    assert len(res["gap_narrative"]) > 50


def test_api_gap_analysis_endpoint():
    pdf_path = os.path.join(FIXTURES_DIR, "clean_resume.pdf")
    with open(pdf_path, "rb") as f:
        upload_res = client.post(
            "/api/v1/resumes/upload",
            files={"file": ("clean_resume.pdf", f.read(), "application/pdf")}
        )
    assert upload_res.status_code in [200, 201, 202]
    resume_id = upload_res.json()["resume_id"]

    # Call role fit interview unified endpoint
    fit_res = client.post(
        "/api/v1/analysis/role-fit-with-interview",
        json={
            "resume_id": resume_id,
            "role_key": "backend_developer",
            "difficulty": "medium",
            "question_count": 8
        }
    )
    assert fit_res.status_code == 201
    analysis_id = fit_res.json()["analysis_id"]

    # Now call GET /api/v1/analysis/{analysis_id}/gap
    gap_res = client.get(f"/api/v1/analysis/{analysis_id}/gap")
    assert gap_res.status_code == 200
    gap_data = gap_res.json()

    assert gap_data["role_key"] == "backend_developer"
    assert "coverage_ratio" in gap_data
    assert "required_coverage" in gap_data
    assert "preferred_coverage" in gap_data
    assert "skill_gap_details" in gap_data
    assert len(gap_data["skill_gap_details"]) > 0
    assert "critical_missing_skills" in gap_data
    assert "quick_wins" in gap_data
    assert "gap_narrative" in gap_data
