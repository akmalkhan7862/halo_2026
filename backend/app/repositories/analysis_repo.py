from typing import List, Optional
from sqlalchemy.orm import Session
from app.models.analysis_result import AnalysisResult
from app.repositories.base import BaseRepository


class AnalysisRepository(BaseRepository[AnalysisResult]):
    def __init__(self, db: Session):
        super().__init__(AnalysisResult, db)

    def get_by_resume_and_jd(self, resume_id: str, jd_id: str) -> Optional[AnalysisResult]:
        return self.db.query(AnalysisResult).filter(
            AnalysisResult.resume_id == resume_id,
            AnalysisResult.job_description_id == jd_id
        ).order_by(AnalysisResult.created_at.desc()).first()
