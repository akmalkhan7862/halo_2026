import os
from typing import Dict, Any, List, Optional
from jinja2 import Template

from app.core.config import settings
from app.services.llm_client import BaseLLMClient
from app.utils.logger import logger


class AnswerEvaluatorService:
    def __init__(self, llm_client: BaseLLMClient):
        self.llm_client = llm_client
        self.template_path = os.path.join(settings.PROMPTS_DIR, "answer_evaluation.txt")

    def _render_prompt(
        self,
        question: Dict[str, Any],
        candidate_answer: str
    ) -> str:
        with open(self.template_path, "r", encoding="utf-8") as f:
            template_str = f.read()

        template = Template(template_str)
        expected_points = "\n".join([f"- {pt}" for pt in question.get("expected_answer_points", [])])
        focus_skills = ", ".join(question.get("skill_focus", []))

        return template.render(
            question_id=question.get("question_id", "q"),
            question_text=question.get("question_text", ""),
            question_type=question.get("type", "technical"),
            skill_focus=focus_skills,
            expected_answer_points=expected_points or "- Comprehensive, accurate technical explanation",
            candidate_answer=candidate_answer
        )

    async def evaluate_answer(
        self,
        question: Dict[str, Any],
        candidate_answer: str
    ) -> Dict[str, Any]:
        """Evaluates candidate answer and produces objective feedback and follow-up."""
        prompt = self._render_prompt(question, candidate_answer)
        evaluation = await self.llm_client.generate_json(prompt)

        # Sanitize score and fields
        score = evaluation.get("score", 70)
        try:
            score = int(score)
            score = max(0, min(100, score))
        except (ValueError, TypeError):
            score = 70

        verdict = evaluation.get("verdict", "good").lower()
        if verdict not in ["exceptional", "good", "adequate", "weak", "unsatisfactory"]:
            verdict = "adequate" if score >= 60 else "weak"

        return {
            "question_id": question.get("question_id", "q"),
            "score": score,
            "verdict": verdict,
            "strengths": evaluation.get("strengths", ["Addressed core premise of the question."]),
            "weaknesses": evaluation.get("weaknesses", []),
            "missing_points": evaluation.get("missing_points", []),
            "suggested_improvement": evaluation.get("suggested_improvement", "Incorporate more concrete metrics and structured examples."),
            "follow_up_question": evaluation.get("follow_up_question")
        }
