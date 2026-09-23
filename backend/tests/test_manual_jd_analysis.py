import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.core.database import SessionLocal
from app.models.resume import Resume
from app.services.taxonomy_service import TaxonomyService
from app.services.jd_parser import JobDescriptionParserService


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture
def db():
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()


def test_jd_parser_service(db):
    tax_service = TaxonomyService(db)
    parser = JobDescriptionParserService(tax_service)

    sample_jd = """
    Senior Backend Engineer
    Acme Software Inc.
    
    About the Role:
    We are looking for a Senior Backend Engineer to build scalable microservices.
    
    Required Qualifications:
    * 5+ years of experience in backend development
    * Must have strong proficiency in Python and FastAPI
    * Deep understanding of PostgreSQL and REST API design
    * Experience with Docker and Git
    
    Preferred Qualifications:
    * Nice to have: Experience with Kubernetes and Redis
    * Knowledge of Amazon Web Services (AWS) is a plus
    * Familiarity with CI/CD pipelines
    """

    parsed = parser.parse(sample_jd)

    assert "Backend" in parsed["job_title"] or "Engineer" in parsed["job_title"]
    assert parsed["seniority"] == "senior"
    assert parsed["experience_requirements"]["minimum_years"] == 5
    assert parsed["experience_requirements"]["detected_from_text"] is True

    req_skills = [s["canonical_skill"].lower() for s in parsed["required_skills"]]
    pref_skills = [s["canonical_skill"].lower() for s in parsed["preferred_skills"]]

    # Python, FastAPI, PostgreSQL should be in required
    assert any("python" in s for s in req_skills)
    assert any("fastapi" in s for s in req_skills)
    assert any("postgresql" in s for s in req_skills)

    # Kubernetes or Redis or AWS should be detected in preferred
    all_extracted = req_skills + pref_skills
    assert any("kubernetes" in s or "redis" in s or "aws" in s or "amazon" in s for s in all_extracted)


def test_manual_jd_analysis_endpoint(client, db):
    # Create mock resume
    mock_resume = Resume(
        id="mock-manual-jd-resume",
        original_filename="manual_candidate.pdf",
        file_type="pdf",
        raw_text="Experienced engineer with Python, FastAPI, Docker, and PostgreSQL experience.",
        status="processed",
        parsed_json={
            "contact": {"name": "Alex Taylor"},
            "skills": [
                {"canonical_skill": "Python", "confidence": 1.0, "evidence": ["Built REST APIs in Python"]},
                {"canonical_skill": "FastAPI", "confidence": 1.0, "evidence": ["Developed microservices using FastAPI"]},
                {"canonical_skill": "PostgreSQL", "confidence": 1.0, "evidence": ["Database design in PostgreSQL"]},
                {"canonical_skill": "Docker", "confidence": 1.0, "evidence": ["Containerized apps with Docker"]},
                {"canonical_skill": "Git", "confidence": 1.0, "evidence": ["Git workflow"]}
            ],
            "projects": [
                {
                    "title": "Cloud Inventory Service",
                    "technologies": ["Python", "FastAPI", "PostgreSQL", "Docker"],
                    "outcomes": ["Deployed Dockerized FastAPI microservices backed by PostgreSQL"]
                }
            ],
            "experience": [
                {
                    "job_title": "Software Engineer",
                    "organization": "TechCorp",
                    "skills": ["Python", "FastAPI", "PostgreSQL"],
                    "bullets": ["Engineered core backend services using Python and FastAPI"]
                }
            ]
        }
    )
    db.merge(mock_resume)
    db.commit()

    sample_jd_text = """
    Senior Backend Engineer
    We are seeking a Backend Engineer with strong expertise in Python, FastAPI, and PostgreSQL.
    Requirements:
    - 4+ years of professional backend software development
    - Proficient in Python, FastAPI, REST API, Docker, PostgreSQL
    Preferred:
    - Experience with Kubernetes and CI/CD pipelines
    """

    payload = {
        "resume_id": "mock-manual-jd-resume",
        "jd_text": sample_jd_text,
        "difficulty": "medium",
        "question_count": 8
    }

    response = client.post("/api/v1/analysis/manual-jd", json=payload)
    assert response.status_code == 201, response.text
    data = response.json()

    assert data["mode"] == "manual_jd"
    assert data["role_key"] is None
    assert "Backend" in data["role_display_name"] or "Engineer" in data["role_display_name"]
    assert len(data["matched_skills"]) > 0
    assert "scores" in data
    assert "overall_score" in data["scores"]
    assert "gap_summary" in data
    assert "overall_fit" in data["gap_summary"]
    assert "narrative_summary" in data["gap_summary"]
    assert "interview" in data
    assert len(data["interview"]["questions"]) > 0
