import os
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)
FIXTURES_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "fixtures")


def test_api_workflow_end_to_end():
    # 1. Health check
    res = client.get("/health")
    assert res.status_code == 200
    assert res.json()["status"] == "healthy"

    # 2. Upload Resume
    pdf_path = os.path.join(FIXTURES_DIR, "clean_resume.pdf")
    with open(pdf_path, "rb") as f:
        upload_res = client.post(
            "/api/v1/resumes/upload",
            files={"file": ("clean_resume.pdf", f, "application/pdf")},
            data={"async_processing": "false"}
        )
    assert upload_res.status_code in [200, 202]
    resume_id = upload_res.json()["resume_id"]
    assert resume_id is not None

    # Verify resume detail
    resume_get = client.get(f"/api/v1/resumes/{resume_id}")
    assert resume_get.status_code == 200
    assert resume_get.json()["status"] == "processed"

    # 3. Create Job Description
    jd_res = client.post(
        "/api/v1/job-descriptions",
        data={
            "title": "Senior Backend Developer",
            "company": "CloudWave Technologies",
            "raw_text": "Requirements: 4+ years of Python, FastAPI, PostgreSQL, and Docker. Preferred: Kubernetes."
        }
    )
    assert jd_res.status_code == 201
    jd_id = jd_res.json()["id"]

    # 4. Run Analysis
    analysis_res = client.post(
        "/api/v1/analysis",
        json={
            "resume_id": resume_id,
            "job_description_id": jd_id,
            "target_role": "Senior Backend Developer",
            "taxonomy_sources": ["esco", "onet", "custom"]
        }
    )
    assert analysis_res.status_code == 201
    analysis_data = analysis_res.json()
    analysis_id = analysis_data["id"]
    assert "scores" in analysis_data
    assert "overall_score" in analysis_data["scores"]
    assert len(analysis_data["matched_skills"]) > 0

    # 5. Create Mock Interview Session
    interview_res = client.post(
        "/api/v1/interviews",
        json={
            "analysis_id": analysis_id,
            "question_count": 8,
            "difficulty": "medium",
            "interview_type": "technical_behavioral_mixed"
        }
    )
    assert interview_res.status_code == 201
    interview_data = interview_res.json()
    interview_id = interview_data["id"]
    questions = interview_data["generated_questions"]
    assert len(questions) >= 7

    # 6. Submit an Answer
    first_q_id = questions[0]["question_id"]
    answer_res = client.post(
        f"/api/v1/interviews/{interview_id}/answers",
        json={
            "question_id": first_q_id,
            "answer_text": "In our backend architecture, we used asyncpg connection pooling configured with 20 connections and handled transactions using async context managers."
        }
    )
    assert answer_res.status_code == 200
    eval_data = answer_res.json()
    assert "score" in eval_data
    assert "verdict" in eval_data

    # 7. Complete Interview
    complete_res = client.post(f"/api/v1/interviews/{interview_id}/complete")
    assert complete_res.status_code == 200
    assert complete_res.json()["status"] == "completed"

    # 8. Fetch Final Consolidated Report & Roadmap
    report_res = client.get(f"/api/v1/reports/{analysis_id}")
    assert report_res.status_code == 200
    report_data = report_res.json()
    assert "candidate_profile" in report_data
    assert "roadmap" in report_data
    assert "immediate_resume_improvements" in report_data["roadmap"]

    # 9. Download PDF Report
    pdf_res = client.get(f"/api/v1/reports/{analysis_id}/download")
    assert pdf_res.status_code == 200
    assert pdf_res.headers["content-type"] == "application/pdf"
    assert len(pdf_res.content) > 1000  # Non-empty PDF
