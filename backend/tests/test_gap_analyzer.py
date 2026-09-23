import pytest
from app.core.database import SessionLocal
from app.services.taxonomy_service import TaxonomyService
from app.services.skill_matcher import SkillMatcherService
from app.services.gap_analyzer import GapAnalyzerService


def test_gap_classification_5way():
    db = SessionLocal()
    try:
        taxonomy = TaxonomyService(db)
        matcher = SkillMatcherService(taxonomy)
        gap_analyzer = GapAnalyzerService()

        resume_skills = [
            {"canonical_skill": "FastAPI", "confidence": 1.0, "evidence": ["Built REST APIs in FastAPI"]},
            {"canonical_skill": "MySQL", "confidence": 0.9, "evidence": ["Used MySQL for storage"]},
            {"canonical_skill": "Docker", "confidence": 0.8, "evidence": ["Listed under skills"]}
        ]
        jd_required = [
            {"canonical_skill": "FastAPI", "importance": "required"},
            {"canonical_skill": "PostgreSQL", "importance": "required"},  # Candidate has MySQL (RELATED_PARTIAL)
            {"canonical_skill": "Kubernetes", "importance": "required"},  # Candidate has Docker (RELATED_PARTIAL)
            {"canonical_skill": "System Design", "importance": "required"} # Candidate lacks (MISSING)
        ]
        jd_preferred = [
            {"canonical_skill": "Docker", "importance": "preferred"}      # Weak evidence (WEAK)
        ]
        resume_exp = [
            {"job_title": "Backend Dev", "skills": ["FastAPI"], "bullets": ["Built high throughput FastAPI services"]}
        ]
        resume_projects = []

        result = matcher.match_skills(resume_skills, jd_required, jd_preferred, resume_exp, resume_projects)

        matched_names = [s["canonical_skill"] for s in result["matched_skills"]]
        assert "FastAPI" in matched_names

        related_names = [s["canonical_skill"] for s in result["related_partial_skills"]]
        assert "PostgreSQL" in related_names or "Kubernetes" in related_names

        missing_names = [s["canonical_skill"] for s in result["missing_skills"]]
        assert "System Design" in missing_names

        summary = gap_analyzer.generate_gap_summary(
            target_role="Backend Developer",
            seniority="mid",
            matched_skills=result["matched_skills"],
            weak_skills=result["weak_skills"],
            missing_skills=result["missing_skills"],
            related_partial_skills=result["related_partial_skills"],
            extra_skills=result["extra_skills"]
        )

        assert "overall_readiness" in summary
        assert "critical_missing_skills" in summary
        assert "quick_wins" in summary
        assert len(summary["quick_wins"]) > 0
    finally:
        db.close()
