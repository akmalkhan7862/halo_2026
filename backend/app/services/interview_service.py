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
            primary_matched = matched_skills[0].get("canonical_skill") if matched_skills else "software development"
            secondary_matched = matched_skills[1].get("canonical_skill") if len(matched_skills) > 1 else "API design"
            primary_missing = missing_skills[0].get("canonical_skill") if missing_skills else "Distributed Systems"
            proj_title = resume_data.get("projects", [{}])[0].get("title", "primary project") if resume_data.get("projects") else "backend system"

            q_templates = [
                {
                    "type": "technical",
                    "skill_focus": [primary_matched],
                    "resume_evidence": f"Candidate demonstrates {primary_matched} in recent implementations",
                    "question_text": f"In your work with {primary_matched}, how do you manage database connection lifecycles and handle high-concurrency race conditions?",
                    "expected_answer_points": ["Connection pooling", "Transaction isolation levels", "Async non-blocking execution", "Connection leak prevention"],
                    "follow_up_hint": "Ask about tuning pool sizes and handling connection deadlocks."
                },
                {
                    "type": "project_based",
                    "skill_focus": [primary_matched, secondary_matched],
                    "resume_evidence": f"Candidate documented project '{proj_title}' incorporating {primary_matched}",
                    "question_text": f"In your project '{proj_title}', what were the most critical architecture trade-offs you made when integrating {primary_matched}?",
                    "expected_answer_points": ["Architecture pattern chosen", "Latency and throughput trade-offs", "Data consistency guarantees", "Error recovery"],
                    "follow_up_hint": "Probe on how they evaluated alternative architectures before finalizing the design."
                },
                {
                    "type": "gap_probing",
                    "skill_focus": [primary_missing],
                    "resume_evidence": f"Identified as a critical missing requirement for target {target_role} role",
                    "question_text": f"The target role requires strong proficiency in {primary_missing}. How would you architect and deploy solutions using {primary_missing} in production?",
                    "expected_answer_points": ["Core concepts of " + primary_missing, "Deployment lifecycle", "Observability and health checks", "Security best practices"],
                    "follow_up_hint": "Ask how their existing skills transfer to bridge this technology gap."
                },
                {
                    "type": "scenario",
                    "skill_focus": ["System Design", "Scalability"],
                    "resume_evidence": f"Seniority requirements for {target_role}",
                    "question_text": f"Suppose your service handles a sudden 20x traffic surge during a campaign event. How would you design rate limiting, caching, and failover to protect downstream services?",
                    "expected_answer_points": ["Distributed rate limiting (e.g. Redis token bucket)", "Multi-layer caching strategy", "Circuit breakers and fallback responses", "Horizontal autoscaling"],
                    "follow_up_hint": "Inquire how they avoid thundering herd problem during cache invalidation."
                },
                {
                    "type": "behavioral",
                    "skill_focus": ["Engineering Ownership", "Incident Management"],
                    "resume_evidence": "Past engineering team and delivery responsibilities",
                    "question_text": "Tell me about a time a production release introduced a critical regression or failed under unexpected load. How did you triage, resolve, and prevent future occurrences?",
                    "expected_answer_points": ["Systematic log and telemetry analysis", "Rollback vs hotfix triage", "Blameless post-mortem analysis", "Automated regression tests and alerts"],
                    "follow_up_hint": "Probe on how they maintained transparent stakeholder communication throughout the incident."
                }
            ]

            questions = []
            for idx in range(question_count):
                tmpl = q_templates[idx % len(q_templates)]
                questions.append({
                    "question_id": f"q{idx+1}",
                    "type": tmpl["type"],
                    "difficulty": difficulty,
                    "skill_focus": tmpl["skill_focus"],
                    "resume_evidence": tmpl["resume_evidence"],
                    "question_text": tmpl["question_text"],
                    "expected_answer_points": tmpl["expected_answer_points"],
                    "follow_up_possible": True,
                    "follow_up_hint": tmpl["follow_up_hint"]
                })

        # Ensure every question has valid fields
        for idx, q in enumerate(questions):
            if not q.get("question_id"):
                q["question_id"] = f"q{idx+1}"
            if "follow_up_possible" not in q:
                q["follow_up_possible"] = True
            if not q.get("follow_up_hint"):
                q["follow_up_hint"] = "Probe deeper into architectural boundaries, failure recovery, or production scale constraints."

        return {
            "interview_plan": llm_response.get("interview_plan", {
                "target_role": target_role,
                "difficulty": difficulty,
                "total_questions": len(questions)
            }),
            "questions": questions
        }
