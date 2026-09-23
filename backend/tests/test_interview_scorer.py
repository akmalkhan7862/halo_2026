import pytest
from app.services.interview_scorer import InterviewScorerService


def test_interview_scorer_weighted_average():
    scorer = InterviewScorerService()

    # Answers with explicit dimension scores
    answers = [
        {
            "score": 60,
            "evaluation_json": {
                "score": 60,
                "verdict": "moderate",
                "dimension_scores": {
                    "technical_accuracy": 60,
                    "relevance": 70,
                    "completeness": 50,
                    "structure_and_clarity": 60,
                    "communication": 60
                }
            }
        },
        {
            "score": 40,
            "evaluation_json": {
                "score": 40,
                "verdict": "weak",
                "dimension_scores": {
                    "technical_accuracy": 40,
                    "relevance": 50,
                    "completeness": 30,
                    "structure_and_clarity": 40,
                    "communication": 50
                }
            }
        }
    ]

    res = scorer.score_session(answers, total_questions=2)
    # Average technical_accuracy: (60+40)/2 = 50
    # Average relevance: (70+50)/2 = 60
    # Average completeness: (50+30)/2 = 40
    # Average structure_and_clarity: (60+40)/2 = 50
    # Average communication: (60+50)/2 = 55
    # Weighted: 50*0.35 + 60*0.20 + 40*0.20 + 50*0.15 + 55*0.10
    # = 17.5 + 12 + 8 + 7.5 + 5.5 = 50.5 -> 51
    assert res["overall_interview_score"] in [50, 51]
    assert res["dimension_scores"]["technical_accuracy"] == 50
    assert res["dimension_scores"]["relevance"] == 60
    assert res["dimension_scores"]["completeness"] == 40
    assert res["dimension_scores"]["structure_and_clarity"] == 50
    assert res["dimension_scores"]["communication"] == 55
    assert res["score_distribution"]["weak"] == 1
    assert res["score_distribution"]["moderate"] == 1
    assert res["answered_count"] == 2


def test_interview_scorer_not_inflated_for_weak_answers():
    scorer = InterviewScorerService()

    # When all answers are weak, interview score must be strictly low (< 50), never inflated by resume
    answers = [
        {
            "score": 35,
            "evaluation_json": {
                "score": 35,
                "verdict": "weak",
                "weaknesses": ["Vague explanations", "Missed core concepts"],
                "missing_points": ["Indexing", "Async sessions"]
            }
        },
        {
            "score": 40,
            "evaluation_json": {
                "score": 40,
                "verdict": "weak",
                "weaknesses": ["Did not mention docker or k8s"],
                "missing_points": ["Container lifecycle"]
            }
        },
        {
            "score": 30,
            "evaluation_json": {
                "score": 30,
                "verdict": "unsatisfactory",
                "weaknesses": ["Incorrect syntax and conceptual flaws"],
                "missing_points": ["Transaction isolation"]
            }
        }
    ]

    res = scorer.score_session(answers, total_questions=3)
    assert res["overall_interview_score"] < 50
    assert res["score_distribution"]["weak"] == 3
    assert res["score_distribution"]["strong"] == 0


def test_interview_scorer_empty_session():
    scorer = InterviewScorerService()
    res = scorer.score_session([], total_questions=8)
    assert res["overall_interview_score"] == 0
    assert res["answered_count"] == 0
    assert res["question_count"] == 8
