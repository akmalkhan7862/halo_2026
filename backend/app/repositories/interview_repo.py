from typing import List, Optional
from sqlalchemy.orm import Session
from app.models.interview_session import InterviewSession
from app.models.interview_answer import InterviewAnswer
from app.repositories.base import BaseRepository


class InterviewRepository(BaseRepository[InterviewSession]):
    def __init__(self, db: Session):
        super().__init__(InterviewSession, db)

    def get_by_analysis_id(self, analysis_id: str) -> List[InterviewSession]:
        return self.db.query(InterviewSession).filter(
            InterviewSession.analysis_result_id == analysis_id
        ).order_by(InterviewSession.created_at.desc()).all()

    def add_answer(self, answer: InterviewAnswer) -> InterviewAnswer:
        self.db.add(answer)
        self.db.commit()
        self.db.refresh(answer)
        return answer

    def get_answers(self, session_id: str) -> List[InterviewAnswer]:
        return self.db.query(InterviewAnswer).filter(
            InterviewAnswer.interview_session_id == session_id
        ).order_by(InterviewAnswer.created_at.asc()).all()
