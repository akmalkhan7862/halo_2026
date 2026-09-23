import os
import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.services.learning_roadmap_service import LearningRoadmapService

client = TestClient(app)
FIXTURES_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "fixtures")


def test_learning_roadmap_service_unit():
    service = LearningRoadmapService()

    resume_data = {
        "projects": [
            {
                "title": "OrderHub Microservices",
                "technologies": ["Python", "FastAPI"],
                "outcomes": ["Processed 5,000 orders/sec"]
            }
        ]
    }

    gap_analysis = {
        "critical_missing_skills": ["Docker", "CI/CD", "Kubernetes"],
        "skill_gap_details": [
            {"skill": "Docker", "status": "missing", "importance": "required"},
            {"skill": "CI/CD", "status": "missing", "importance": "required"},
            {"skill": "Kubernetes", "status": "missing", "importance": "required"},
            {"skill": "Redis", "status": "weak", "importance": "preferred"},
            {"skill": "FastAPI", "status": "matched", "importance": "required"}
        ]
    }

    res = service.generate_roadmap(
        role_key="backend_developer",
        display_name="Backend Developer",
        seniority="mid",
        domain="software_engineering",
        gap_analysis=gap_analysis,
        resume_data=resume_data
    )

    assert res["role_key"] == "backend_developer"
    assert "learning_roadmap" in res
    roadmap = res["learning_roadmap"]

    assert "priority_skills" in roadmap
    assert len(roadmap["priority_skills"]) >= 3

    for item in roadmap["priority_skills"]:
        assert "skill" in item
        assert "why_it_matters" in item
        assert len(item["why_it_matters"]) > 20
        assert "resources" in item
        assert len(item["resources"]) >= 2
        for r in item["resources"]:
            assert "type" in r
            assert "title" in r
            assert "url" in r
            assert r["url"].startswith("http")
        assert "project_task" in item
        assert "OrderHub Microservices" in item["project_task"]
        assert "estimated_effort" in item
        assert "success_criteria" in item
        assert len(item["success_criteria"]) >= 2

    assert "suggested_sequence" in roadmap
    assert len(roadmap["suggested_sequence"]) >= 2
    assert "general_advice" in roadmap
    assert len(roadmap["general_advice"]) >= 3


def test_api_learning_roadmap_endpoint():
    pdf_path = os.path.join(FIXTURES_DIR, "clean_resume.pdf")
    with open(pdf_path, "rb") as f:
        upload_res = client.post(
            "/api/v1/resumes/upload",
            files={"file": ("clean_resume.pdf", f.read(), "application/pdf")}
        )
    assert upload_res.status_code in [200, 201, 202]
    resume_id = upload_res.json()["resume_id"]

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

    # Call GET /api/v1/analysis/{analysis_id}/roadmap
    roadmap_res = client.get(f"/api/v1/analysis/{analysis_id}/roadmap")
    assert roadmap_res.status_code == 200
    data = roadmap_res.json()

    assert data["role_key"] == "backend_developer"
    assert "learning_roadmap" in data
    roadmap = data["learning_roadmap"]
    assert "priority_skills" in roadmap
    assert len(roadmap["priority_skills"]) >= 3
    assert "suggested_sequence" in roadmap
    assert "general_advice" in roadmap
