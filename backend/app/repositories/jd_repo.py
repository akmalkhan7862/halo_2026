from typing import List, Optional
from sqlalchemy.orm import Session
from app.models.job_description import JobDescription
from app.repositories.base import BaseRepository


class JobDescriptionRepository(BaseRepository[JobDescription]):
    def __init__(self, db: Session):
        super().__init__(JobDescription, db)

    def list_by_user(self, user_id: str) -> List[JobDescription]:
        return self.db.query(JobDescription).filter(JobDescription.user_id == user_id).order_by(JobDescription.created_at.desc()).all()
