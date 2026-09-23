from typing import List, Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict


class InterviewCreate(BaseModel):
    analysis_id: str
    question_count: int = Field(default=8, ge=5, le=15)
    difficulty: str = "medium"  # easy, medium, hard
    interview_type: str = "technical_behavioral_mixed"


class GeneratedQuestionSchema(BaseModel):
    question_id: str
    type: str  # technical, project_based, behavioral, gap_probing, scenario
    difficulty: str = "medium"
    skill_focus: List[str] = Field(default_factory=list)
    resume_evidence: Optional[str] = None
    question_text: str
    expected_answer_points: List[str] = Field(default_factory=list)
    follow_up_possible: bool = True
    follow_up_hint: Optional[str] = None


class AnswerSubmitRequest(BaseModel):
    question_id: str
    answer_text: str = Field(..., min_length=5)


class AnswerEvaluationResponse(BaseModel):
    question_id: str
    score: int
    verdict: str  # exceptional, good, adequate, weak, unsatisfactory
    dimension_scores: Optional[Dict[str, int]] = None
    strengths: List[str] = Field(default_factory=list)
    weaknesses: List[str] = Field(default_factory=list)
    missing_points: List[str] = Field(default_factory=list)
    suggested_improvement: str
    follow_up_question: Optional[str] = None


class AnswerDetailSchema(BaseModel):
    id: str
    question_id: str
    question_text: str
    answer_text: str
    score: Optional[int] = None
    evaluation_json: Optional[Dict[str, Any]] = None
    created_at: datetime


class InterviewSessionResponse(BaseModel):
    id: str
    analysis_result_id: str
    target_role: str
    difficulty: str
    question_count: int
    status: str
    interview_plan: Optional[Dict[str, Any]] = None
    generated_questions: List[GeneratedQuestionSchema] = Field(default_factory=list)
    answers: List[AnswerDetailSchema] = Field(default_factory=list)
    overall_score: Optional[int] = None
    summary_feedback: Optional[Dict[str, Any]] = None
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)


class InterviewCompleteResponse(BaseModel):
    interview_id: str
    status: str
    overall_score: int
    verdict: str
    summary_feedback: Dict[str, Any]
