import os
import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.core.database import SessionLocal
from app.services.taxonomy_service import TaxonomyService
from app.services.role_profile_loader import RoleProfileLoaderService
from app.services.role_matcher import RoleMatcherService

client = TestClient(app)
FIXTURES_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "fixtures")


def test_role_profile_loader():
    db = SessionLocal()
    try:
        loader = RoleProfileLoaderService(db)
        roles = loader.get_all_roles()
        assert len(roles) >= 10

        role_keys = [r.role_key for r in roles]
        assert "backend_developer" in role_keys
        assert "data_analyst" in role_keys
        assert "devops_engineer" in role_keys

        backend_role = loader.get_role_by_key("backend_developer")
        assert backend_role is not None
        assert "Python" in backend_role.required_skills
        assert "FastAPI" in backend_role.required_skills
    finally:
        db.close()


def test_role_matcher_service_single_role():
    db = SessionLocal()
    try:
        taxonomy = TaxonomyService(db)
        loader = RoleProfileLoaderService(db)
        matcher = RoleMatcherService(taxonomy)

        backend_role = loader.get_role_by_key("backend_developer")
        assert backend_role is not None

        candidate_resume = {
            "skills": [
                {"canonical_skill": "Python", "confidence": 1.0, "evidence": ["Built backend APIs"]},
                {"canonical_skill": "FastAPI", "confidence": 1.0, "evidence": ["FastAPI microservices"]},
                {"canonical_skill": "MySQL", "confidence": 0.9, "evidence": ["MySQL database"]}, # bridges PostgreSQL
                {"canonical_skill": "Tableau", "confidence": 0.9, "evidence": ["Data dashboards"]}, # Extra skill
                {"canonical_skill": "Git", "confidence": 0.8, "evidence": ["Used Git"]}
            ],
            "experience": [
                {"job_title": "Backend Dev", "skills": ["Python", "FastAPI"], "bullets": ["Engineered high scale FastAPI APIs"]}
            ],
            "projects": []
        }

        match_res = matcher.match_resume_to_role(candidate_resume, backend_role)

        assert match_res["role_key"] == "backend_developer"
        assert match_res["fit_score"] > 0

        matched_names = [m["canonical_skill"] for m in match_res["matched_skills"]]
        assert "Python" in matched_names
        assert "FastAPI" in matched_names

        # MySQL is transferable to PostgreSQL
        related_names = [r["canonical_skill"] for r in match_res["related_partial_skills"]]
        assert "PostgreSQL" in related_names

        # Tableau is not required for backend developer, should be in extra_skills
        assert "Tableau" in match_res["extra_skills"]

        # Docker is in required skills but absent in resume, should be missing
        missing_names = [m["canonical_skill"] for m in match_res["missing_skills"]]
        assert "Docker" in missing_names

        # Gap summary verification
        gap = match_res["gap_summary"]
        assert "overall_readiness" in gap
        assert len(gap["quick_wins"]) > 0
        assert "Backend Developer" in gap["narrative_summary"]
    finally:
        db.close()


def test_api_list_roles():
    res = client.get("/api/v1/roles")
    assert res.status_code == 200
    data = res.json()
    assert len(data) >= 10
    keys = [r["role_key"] for r in data]
    assert "backend_developer" in keys
    assert "data_analyst" in keys


def test_api_get_role_detail():
    res = client.get("/api/v1/roles/backend_developer")
    assert res.status_code == 200
    data = res.json()
    assert data["role_key"] == "backend_developer"
    assert "Python" in data["required_skills"]
    assert "sources" in data


def test_api_role_analysis_without_jd():
    # 1. Upload clean resume
    pdf_path = os.path.join(FIXTURES_DIR, "clean_resume.pdf")
    with open(pdf_path, "rb") as f:
        upload_res = client.post(
            "/api/v1/resumes/upload",
            files={"file": ("clean_resume.pdf", f, "application/pdf")},
            data={"async_processing": "false"}
        )
    assert upload_res.status_code in [200, 202]
    resume_id = upload_res.json()["resume_id"]

    # 2. Analyze against single specific role (NO JD TEXT NEEDED)
    single_res = client.post(
        "/api/v1/roles/analyze",
        json={
            "resume_id": resume_id,
            "target_role_key": "backend_developer"
        }
    )
    assert single_res.status_code == 200
    single_data = single_res.json()
    assert "role_analysis" in single_data
    analysis = single_data["role_analysis"]
    assert analysis["role_key"] == "backend_developer"
    assert len(analysis["matched_skills"]) > 0
    assert "gap_summary" in analysis

    # 3. Analyze against ALL 12 curated roles (Batch Comparison & Ranking)
    multi_res = client.post(
        "/api/v1/roles/analyze",
        json={
            "resume_id": resume_id,
            "target_role_key": "all"
        }
    )
    assert multi_res.status_code == 200
    multi_data = multi_res.json()
    assert multi_data["total_roles_evaluated"] >= 10
    assert "top_recommended_role" in multi_data
    assert len(multi_data["role_rankings"]) >= 10
    # Top ranking has highest score
    assert multi_data["role_rankings"][0]["fit_score"] >= multi_data["role_rankings"][-1]["fit_score"]
