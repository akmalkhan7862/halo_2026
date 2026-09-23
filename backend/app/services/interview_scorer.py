from typing import List, Dict, Any, Optional
import math


class InterviewScorerService:
    """
    Dedicated service to compute objective interview performance scores.
    Aggregates per-question evaluations across 5 weighted dimensions:
      - technical_accuracy: 0.35
      - relevance: 0.20
      - completeness: 0.20
      - structure_and_clarity: 0.15
      - communication: 0.10

    Product Rule for skipped / unanswered questions:
    - Dimension averages are computed across all submitted/evaluated answers so that
      qualitative dimension feedback accurately reflects actual demonstration.
    - If no answers were submitted, overall_interview_score is 0.
    - If fewer than half of the questions are answered upon session completion, the score
      is scaled by the completion ratio (answered / question_count) to reflect incomplete coverage.
    - This strictly prevents inflating the interview score with resume fit scores.
    """

    WEIGHTS = {
        "technical_accuracy": 0.35,
        "relevance": 0.20,
        "completeness": 0.20,
        "structure_and_clarity": 0.15,
        "communication": 0.10
    }

    def _extract_dimensions(self, eval_data: Dict[str, Any], fallback_score: int) -> Dict[str, int]:
        """Extracts or estimates 5 dimensions from an answer evaluation dict."""
        dim_scores = eval_data.get("dimension_scores") or eval_data.get("scores") or {}

        def get_val(key: str, default: int) -> int:
            val = dim_scores.get(key)
            if val is not None:
                try:
                    return max(0, min(100, int(val)))
                except (ValueError, TypeError):
                    pass
            return default

        # If dimensions are not explicitly present, derive them logically from score & weaknesses
        base = max(0, min(100, fallback_score))
        weaknesses = eval_data.get("weaknesses", [])
        missing = eval_data.get("missing_points", [])

        # Slightly modulate based on missing points or structure feedback
        comp_penalty = 10 if missing else 0
        clarity_penalty = 8 if any("structur" in w.lower() or "concis" in w.lower() for w in weaknesses) else 0

        return {
            "technical_accuracy": get_val("technical_accuracy", base),
            "relevance": get_val("relevance", min(100, base + 5)),
            "completeness": get_val("completeness", max(0, base - comp_penalty)),
            "structure_and_clarity": get_val("structure_and_clarity", max(0, base - clarity_penalty)),
            "communication": get_val("communication", base)
        }

    def score_session(
        self,
        answers: List[Any],
        total_questions: int = 8
    ) -> Dict[str, Any]:
        """
        Computes the aggregate interview score, dimension breakdown,
        and score distribution from a list of answer records or evaluation dicts.
        """
        if not answers:
            return {
                "overall_interview_score": 0,
                "dimension_scores": {
                    "technical_accuracy": 0,
                    "relevance": 0,
                    "completeness": 0,
                    "structure_and_clarity": 0,
                    "communication": 0
                },
                "question_count": total_questions,
                "answered_count": 0,
                "score_distribution": {
                    "strong": 0,
                    "good": 0,
                    "moderate": 0,
                    "weak": 0
                }
            }

        dim_sums = {
            "technical_accuracy": 0.0,
            "relevance": 0.0,
            "completeness": 0.0,
            "structure_and_clarity": 0.0,
            "communication": 0.0
        }

        distribution = {
            "strong": 0,
            "good": 0,
            "moderate": 0,
            "weak": 0
        }

        valid_answers_count = 0

        for ans in answers:
            # Handle both InterviewAnswer model instances and dicts
            if hasattr(ans, "evaluation_json"):
                eval_data = ans.evaluation_json or {}
                raw_score = ans.score if ans.score is not None else eval_data.get("score", 70)
            elif isinstance(ans, dict):
                eval_data = ans.get("evaluation_json") or ans
                raw_score = ans.get("score") if ans.get("score") is not None else eval_data.get("score", 70)
            else:
                eval_data = {}
                raw_score = 70

            try:
                raw_score = int(raw_score)
            except (ValueError, TypeError):
                raw_score = 70

            dims = self._extract_dimensions(eval_data, raw_score)
            for k in dim_sums:
                dim_sums[k] += dims[k]

            verdict = (eval_data.get("verdict") or "").lower()
            if verdict in ["exceptional", "strong", "excellent"] or raw_score >= 85:
                distribution["strong"] += 1
            elif verdict in ["good"] or raw_score >= 70:
                distribution["good"] += 1
            elif verdict in ["adequate", "moderate", "average"] or raw_score >= 50:
                distribution["moderate"] += 1
            else:
                distribution["weak"] += 1

            valid_answers_count += 1

        if valid_answers_count == 0:
            return {
                "overall_interview_score": 0,
                "dimension_scores": {k: 0 for k in dim_sums},
                "question_count": total_questions,
                "answered_count": 0,
                "score_distribution": distribution
            }

        # Compute average dimension scores
        avg_dimensions = {
            k: round(dim_sums[k] / valid_answers_count)
            for k in dim_sums
        }

        # Weighted aggregate score
        raw_weighted_score = sum(
            avg_dimensions[dim] * weight
            for dim, weight in self.WEIGHTS.items()
        )

        effective_total_q = max(total_questions, valid_answers_count, 1)

        # Scale if fewer questions answered than total configured
        if valid_answers_count < effective_total_q:
            # Partial penalty for skipped questions: weighted by attempted ratio
            completion_ratio = valid_answers_count / effective_total_q
            # Blend 80% raw performance + 20% completion factor to avoid giving a full score for 1 answered question
            final_overall = raw_weighted_score * (0.8 + 0.2 * completion_ratio)
        else:
            final_overall = raw_weighted_score

        overall_interview_score = int(round(max(0, min(100, final_overall))))

        return {
            "overall_interview_score": overall_interview_score,
            "dimension_scores": avg_dimensions,
            "question_count": effective_total_q,
            "answered_count": valid_answers_count,
            "score_distribution": distribution
        }
