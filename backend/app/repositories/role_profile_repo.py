from typing import List, Optional
from sqlalchemy.orm import Session
from app.models.role_profile import RoleProfile
from app.repositories.base import BaseRepository


class RoleProfileRepository(BaseRepository[RoleProfile]):
    def __init__(self, db: Session):
        super().__init__(RoleProfile, db)

    def get_by_role_key(self, role_key: str) -> Optional[RoleProfile]:
        return self.db.query(RoleProfile).filter(RoleProfile.role_key == role_key.strip().lower()).first()

    def list_all_roles(self) -> List[RoleProfile]:
        return self.db.query(RoleProfile).order_by(RoleProfile.display_name.asc()).all()
