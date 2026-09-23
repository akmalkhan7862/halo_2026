from typing import List, Dict, Any, Optional
import re
from app.services.llm_client import BaseLLMClient
from app.utils.logger import logger


class InterviewInsightsService:
    """
    Derives key strengths, key weaknesses, role-specific recommendations,
    and communication feedback directly from candidate mock interview answer evaluations.
    Guarantees insights reflect actual interview performance rather than just resume keywords.
    """

    def __init__(self, llm_client: Optional[BaseLLMClient] = None):
        self.llm_client = llm_client

    def _heuristic_insights(
        self,
        evaluations: List[Dict[str, Any]],
        role_metadata: Dict[str, Any],
        dimension_scores: Optional[Dict[str, int]] = None
    ) -> Dict[str, Any]:
        """Deterministic heuristic generator when LLM is unavailable or offline."""
        all_strengths: List[str] = []
        all_weaknesses: List[str] = []
        all_missing: List[str] = []
        all_improvements: List[str] = []

        for ev in evaluations:
            for s in ev.get("strengths", []):
                if s and s not in all_strengths:
                    all_strengths.append(s)
            for w in ev.get("weaknesses", []):
                if w and w not in all_weaknesses:
                    all_weaknesses.append(w)
            for m in ev.get("missing_points", []):
                if m and m not in all_missing:
                    all_missing.append(m)
            imp = ev.get("suggested_improvement")
            if imp and imp not in all_improvements:
                all_improvements.append(imp)

        role_name = role_metadata.get("display_name") or role_metadata.get("title") or "target role"
        seniority = role_metadata.get("seniority", "mid").lower()

        # Format key strengths phrased around interview performance
        key_strengths = []
        for s in all_strengths[:4]:
            clean = s.strip().rstrip(".")
            if not any(clean.lower().startswith(prefix) for prefix in ["clearly", "demonstrated", "consistently", "effectively", "strong"]):
                clean = f"Consistently demonstrated {clean[0].lower() + clean[1:]}"
            key_strengths.append(f"{clean}.")

        if not key_strengths:
            key_strengths = [
                f"Engaged constructively with technical interview questions for {role_name}.",
                "Demonstrated familiarity with fundamental engineering concepts."
            ]

        # Format key weaknesses focused on patterns
        key_weaknesses = []
        for w in all_weaknesses[:3]:
            clean = w.strip().rstrip(".")
            key_weaknesses.append(f"{clean}.")

        for m in all_missing[:2]:
            clean = m.strip().rstrip(".")
            key_weaknesses.append(f"Did not sufficiently address {clean.lower()} during technical explanations.")

        if not key_weaknesses:
            key_weaknesses = [
                "Answers occasionally lacked quantitative metrics (latency, throughput, scale).",
                "Could provide deeper operational examples when discussing trade-offs."
            ]

        # Format actionable recommendations tied to role and seniority expectations
        recommendations = []
        for imp in all_improvements[:3]:
            recommendations.append(imp if imp.endswith(".") else f"{imp}.")

        if len(recommendations) < 3 and all_missing:
            recommendations.append(
                f"Prepare concrete production scenarios demonstrating {all_missing[0].lower()} to satisfy {seniority}-level interviewer expectations."
            )

        if not recommendations:
            recommendations = [
                f"For a {seniority} {role_name} interview, structure explanations using the STAR method (Situation, Task, Action, Result).",
                "Consistently quantify technical impact using measurable performance metrics (e.g. latency, concurrency, error rates).",
                "Explicitly articulate architectural trade-offs and alternative approaches considered."
            ]

        # Derive communication feedback from structure and communication observations
        comm_score = (dimension_scores or {}).get("communication", 65)
        struct_score = (dimension_scores or {}).get("structure_and_clarity", 65)

        comm_strengths = []
        if comm_score >= 70:
            comm_strengths.append("Maintained clear, confident technical articulation throughout the session.")
        else:
            comm_strengths.append("Conveyed technical terminology appropriately during responses.")

        if struct_score >= 70:
            comm_strengths.append("Answers were organized logically with coherent sequence.")
        else:
            comm_strengths.append("Addressed the central premise of each interview prompt.")

        comm_improvements = []
        if struct_score < 70:
            comm_improvements.append("Avoid long, rambling paragraphs; lead directly with your architectural conclusion before expanding.")
        else:
            comm_improvements.append("Keep answers concise and highlight high-level system boundaries before diving into implementation details.")

        comm_improvements.append("Explicitly state edge cases and failure modes proactively rather than waiting for follow-up prompts.")

        return {
            "key_strengths": key_strengths[:4],
            "key_weaknesses": key_weaknesses[:4],
            "recommendations": recommendations[:4],
            "communication_feedback": {
                "strengths": comm_strengths,
                "improvements": comm_improvements
            }
        }

    async def generate_insights(
        self,
        answers: List[Any],
        role_metadata: Dict[str, Any],
        dimension_scores: Optional[Dict[str, int]] = None
    ) -> Dict[str, Any]:
        """
        Synthesizes interview insights from answer evaluations.
        Uses LLM prompt when available; falls back smoothly to heuristic engine.
        """
        evaluations: List[Dict[str, Any]] = []
        for a in answers:
            if hasattr(a, "evaluation_json") and a.evaluation_json:
                evaluations.append(a.evaluation_json)
            elif isinstance(a, dict):
                ev = a.get("evaluation_json") or a
                evaluations.append(ev)

        if not evaluations:
            role_title = role_metadata.get("display_name") or role_metadata.get("title") or "target role"
            return {
                "key_strengths": ["No interview answers have been submitted for evaluation yet."],
                "key_weaknesses": ["Interview session incomplete."],
                "recommendations": [f"Complete the mock interview session to unlock personalized interview coaching for {role_title}."],
                "communication_feedback": {
                    "strengths": ["Pending interview answers."],
                    "improvements": ["Complete mock interview questions to assess technical communication."]
                }
            }

        # If LLM client is available and not in testing, attempt LLM synthesis
        if self.llm_client and hasattr(self.llm_client, "generate_json"):
            prompt = f"""You are a senior technical hiring manager reviewing a candidate's completed mock interview session for the role of {role_metadata.get('display_name', 'Software Engineer')} ({role_metadata.get('seniority', 'mid')} level).

Here are the individual question evaluation summaries from the candidate's actual interview answers:
{evaluations}

Task:
Analyze the candidate's actual answers and evaluations to generate:
1. "key_strengths": 3-4 recurring strengths demonstrated during the interview (worded in terms of interview behavior, e.g. "Consistently explained API design decisions clearly").
2. "key_weaknesses": 3-4 recurring weaknesses, gaps, or missing points from their answers. Focus on patterns.
3. "recommendations": 3-4 concrete, actionable coaching recommendations tied to {role_metadata.get('seniority', 'mid')}-level expectations.
4. "communication_feedback": object with "strengths" (list of 2 strings) and "improvements" (list of 2 strings) evaluating communication clarity and structure.

Return STRICTLY a JSON object with this exact structure:
{{
  "key_strengths": ["..."],
  "key_weaknesses": ["..."],
  "recommendations": ["..."],
  "communication_feedback": {{
    "strengths": ["..."],
    "improvements": ["..."]
  }}
}}
"""
            try:
                res = await self.llm_client.generate_json(prompt)
                if (
                    isinstance(res, dict)
                    and res.get("key_strengths")
                    and res.get("key_weaknesses")
                    and res.get("recommendations")
                    and res.get("communication_feedback")
                ):
                    return res
            except Exception as e:
                logger.warning(f"LLM interview insights synthesis failed: {e}. Falling back to heuristic insights.")

        return self._heuristic_insights(evaluations, role_metadata, dimension_scores)
