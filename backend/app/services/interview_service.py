import os
from typing import Dict, Any, List
from jinja2 import Template

from app.core.config import settings
from app.services.llm_client import BaseLLMClient
from app.utils.logger import logger


class InterviewService:
    def __init__(self, llm_client: BaseLLMClient):
        self.llm_client = llm_client
        self.template_path = os.path.join(settings.PROMPTS_DIR, "interview_generation.txt")

    def _render_prompt(
        self,
        target_role: str,
        difficulty: str,
        question_count: int,
        resume_data: Dict[str, Any],
        jd_data: Dict[str, Any],
        matched_skills: List[Dict[str, Any]],
        weak_skills: List[Dict[str, Any]],
        missing_skills: List[Dict[str, Any]]
    ) -> str:
        with open(self.template_path, "r", encoding="utf-8") as f:
            template_str = f.read()

        template = Template(template_str)

        matched_names = [m.get("canonical_skill") for m in matched_skills]
        weak_names = [w.get("canonical_skill") for w in weak_skills]
        missing_names = [m.get("canonical_skill") for m in missing_skills]
        
        # Format projects and experience summaries
        projects_summary = "; ".join([
            f"{p.get('title')}: {p.get('description', '')} (Tech: {', '.join(p.get('technologies', []))})"
            for p in resume_data.get("projects", [])[:3]
        ]) or "General backend engineering projects."

        exp_summary = "; ".join([
            f"{e.get('job_title')} at {e.get('organization')}: {', '.join(e.get('bullets', [])[:2])}"
            for e in resume_data.get("experience", [])[:3]
        ]) or "Self-directed engineering and internship experience."

        cert_summary = ", ".join([c.get("name") for c in resume_data.get("certifications", [])]) or "None specified."

        rendered = template.render(
            target_role=target_role,
            difficulty=difficulty,
            question_count=question_count,
            resume_summary=resume_data.get("summary") or "Technical candidate with hands-on software development profile.",
            matched_skills=", ".join(matched_names) if matched_names else "Core fundamentals",
            weak_skills=", ".join(weak_names) if weak_names else "None",
            missing_skills=", ".join(missing_names) if missing_names else "None",
            projects=projects_summary,
            experience=exp_summary,
            certifications=cert_summary,
            jd_title=jd_data.get("job_title", target_role),
            jd_seniority=jd_data.get("seniority", "mid"),
            jd_required_skills=", ".join([s.get("canonical_skill") for s in jd_data.get("required_skills", [])]),
            jd_domain=jd_data.get("domain", "software_engineering")
        )
        return rendered

    async def generate_interview_session(
        self,
        target_role: str,
        difficulty: str,
        question_count: int,
        resume_data: Dict[str, Any],
        jd_data: Dict[str, Any],
        matched_skills: List[Dict[str, Any]],
        weak_skills: List[Dict[str, Any]],
        missing_skills: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Generates dynamic, resume-specific mock interview questions via LLM."""
        prompt = self._render_prompt(
            target_role=target_role,
            difficulty=difficulty,
            question_count=question_count,
            resume_data=resume_data,
            jd_data=jd_data,
            matched_skills=matched_skills,
            weak_skills=weak_skills,
            missing_skills=missing_skills
        )

        llm_response = await self.llm_client.generate_json(prompt)
        
        # Fallback if structure is malformed
        questions = llm_response.get("questions", [])
        if not questions:
            logger.warning("LLM returned empty questions array. Supplying fallback question set.")
            questions = [
                {
                    "question_id": f"q{idx+1}",
                    "type": "technical",
                    "difficulty": difficulty,
                    "skill_focus": [m.get("canonical_skill") for m in matched_skills[:2]],
                    "resume_evidence": f"Candidate cites experience in {matched_skills[0].get('canonical_skill') if matched_skills else 'software development'}",
                    "question_text": f"How do you ensure performance, error handling, and test coverage in your {matched_skills[0].get('canonical_skill') if matched_skills else 'backend'} implementations?",
                    "expected_answer_points": ["Error handling", "Automated tests", "Concurrency", "Optimization"],
                    "follow_up_possible": True
                }
                for idx in range(question_count)
            ]

        # Ensure every question has valid fields
        for idx, q in enumerate(questions):
            if not q.get("question_id"):
                q["question_id"] = f"q{idx+1}"
            if "follow_up_possible" not in q:
                q["follow_up_possible"] = True

        return {
            "interview_plan": llm_response.get("interview_plan", {
                "target_role": target_role,
                "difficulty": difficulty,
                "total_questions": len(questions)
            }),
            "questions": questions
        }
