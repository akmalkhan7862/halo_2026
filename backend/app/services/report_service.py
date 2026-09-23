import os
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional
from jinja2 import Template

from app.core.config import settings
from app.services.llm_client import BaseLLMClient
from app.utils.pdf_generator import generate_report_pdf
from app.utils.logger import logger


class ReportService:
    def __init__(self, llm_client: BaseLLMClient):
        self.llm_client = llm_client
        self.template_path = os.path.join(settings.PROMPTS_DIR, "roadmap_generation.txt")

    async def generate_career_roadmap(
        self,
        target_role: str,
        overall_score: float,
        missing_skills: List[str],
        weak_skills: List[str],
        related_skills: List[str],
        experience_summary: str,
        interview_weaknesses: List[str]
    ) -> Dict[str, Any]:
        """Generates dynamic, highly personalized career roadmap using LLM with deterministic fallback."""
        with open(self.template_path, "r", encoding="utf-8") as f:
            template_str = f.read()

        template = Template(template_str)
        prompt = template.render(
            target_role=target_role,
            overall_score=overall_score,
            missing_skills=", ".join(missing_skills) if missing_skills else "None",
            weak_skills=", ".join(weak_skills) if weak_skills else "None",
            related_skills=", ".join(related_skills) if related_skills else "None",
            experience_summary=experience_summary or "Early to mid-level engineering background",
            interview_weaknesses=", ".join(interview_weaknesses) if interview_weaknesses else "Deep dive architecture specifics"
        )

        roadmap_data = await self.llm_client.generate_json(prompt)
        return roadmap_data

    async def build_consolidated_report(
        self,
        analysis_data: Dict[str, Any],
        resume_data: Dict[str, Any],
        jd_data: Dict[str, Any],
        interview_session_data: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Builds complete consolidated report object with live career roadmap."""
        scores = analysis_data.get("scores", {})
        overall_score = scores.get("overall_score", 0.0)

        missing = [m.get("canonical_skill") for m in analysis_data.get("missing_skills", [])]
        weak = [w.get("canonical_skill") for w in analysis_data.get("weak_skills", [])]
        related = [r.get("canonical_skill") for r in analysis_data.get("related_partial_skills", [])]

        exp_entries = resume_data.get("experience", [])
        exp_summary = "; ".join([e.get("job_title", "") for e in exp_entries[:3]])

        interview_weaknesses = []
        if interview_session_data and "answers" in interview_session_data:
            for ans in interview_session_data.get("answers", []):
                ev = ans.get("evaluation_json") or {}
                interview_weaknesses.extend(ev.get("weaknesses", []))

        target_role = analysis_data.get("target_role") or jd_data.get("job_title") or "Software Engineer"

        roadmap = await self.generate_career_roadmap(
            target_role=target_role,
            overall_score=overall_score,
            missing_skills=missing,
            weak_skills=weak,
            related_skills=related,
            experience_summary=exp_summary,
            interview_weaknesses=interview_weaknesses[:5]
        )

        report = {
            "analysis_id": analysis_data.get("id"),
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "candidate_profile": {
                "contact": resume_data.get("contact", {}),
                "summary": resume_data.get("summary", ""),
                "skills_count": len(resume_data.get("skills", [])),
                "projects_count": len(resume_data.get("projects", [])),
                "experience_count": len(resume_data.get("experience", []))
            },
            "target_job": {
                "title": jd_data.get("job_title"),
                "company": jd_data.get("company"),
                "seniority": jd_data.get("seniority"),
                "domain": jd_data.get("domain")
            },
            "analysis": analysis_data,
            "interview_session": interview_session_data,
            "roadmap": roadmap
        }
        return report

    def export_pdf(self, report_data: Dict[str, Any]):
        return generate_report_pdf(report_data)
