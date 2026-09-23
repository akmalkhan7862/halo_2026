import os
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)
FIXTURES_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "fixtures")


def test_role_fit_with_interview_unified_workflow():
    # 1. Upload sample PDF resume
    pdf_path = os.path.join(FIXTURES_DIR, "clean_resume.pdf")
    with open(pdf_path, "rb") as f:
        pdf_bytes = f.read()

    files = {"file": ("clean_resume.pdf", pdf_bytes, "application/pdf")}
    res_upload = client.post("/api/v1/resumes/upload", files=files)
    assert res_upload.status_code in [200, 201, 202], res_upload.text
    resume_id = res_upload.json()["resume_id"]

    # 2. Call unified endpoint: POST /api/v1/analysis/role-fit-with-interview
    payload = {
        "resume_id": resume_id,
        "role_key": "backend_developer",
        "difficulty": "medium",
        "question_count": 8
    }
    res_unified = client.post("/api/v1/analysis/role-fit-with-interview", json=payload)
    assert res_unified.status_code == 201, res_unified.text
    data = res_unified.json()

    # Validate structure
    assert "analysis_id" in data
    assert data["role_key"] == "backend_developer"
    assert data["display_name"] == "Backend Developer"
    assert isinstance(data["matched_skills"], list)
    assert isinstance(data["missing_skills"], list)
    assert isinstance(data["weak_skills"], list)
    assert isinstance(data["extra_skills"], list)
    assert "coverage_ratio" in data
    assert 0.0 <= data["coverage_ratio"] <= 1.0

    gap = data["gap_summary"]
    assert "overall_fit" in gap
    assert "narrative_summary" in gap
    assert "top_missing_skills" in gap
    assert "quick_wins" in gap
    assert "recommended_focus_areas" in gap

    interview = data["interview"]
    assert "session_id" in interview
    session_id = interview["session_id"]
    questions = interview["questions"]
    assert len(questions) >= 5
    for q in questions:
        assert "question_id" in q
        assert "question_text" in q

    # 3. Submit an answer to Q1
    q1 = questions[0]
    ans_res = client.post(
        f"/api/v1/interviews/{session_id}/answers",
        json={
            "question_id": q1["question_id"],
            "answer_text": "We designed our FastAPI dependency injection with async generator yields to manage SQLAlchemy database sessions cleanly and avoid connection leaks."
        }
    )
    assert ans_res.status_code == 200, ans_res.text
    ans_data = ans_res.json()
    assert "score" in ans_data
    assert "verdict" in ans_data

    # 4. Complete the interview session
    comp_res = client.post(f"/api/v1/interviews/{session_id}/complete")
    assert comp_res.status_code == 200, comp_res.text
    comp_data = comp_res.json()
    assert comp_data["status"] == "completed"

    # 5. Retrieve final report for the role analysis
    analysis_id = data["analysis_id"]
    report_res = client.get(f"/api/v1/reports/{analysis_id}")
    assert report_res.status_code == 200, report_res.text
    rep_data = report_res.json()
    assert rep_data["target_job"]["title"] == "Backend Developer"
    assert "roadmap" in rep_data
    assert rep_data["interview_session"]["status"] == "completed"
