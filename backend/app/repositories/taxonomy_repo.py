from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.models.taxonomy import TaxonomySkill, TaxonomyOccupation, CustomSkill
from app.repositories.base import BaseRepository


class TaxonomyRepository(BaseRepository[TaxonomySkill]):
    def __init__(self, db: Session):
        super().__init__(TaxonomySkill, db)

    def find_by_canonical(self, name: str) -> Optional[TaxonomySkill]:
        clean = name.strip().lower()
        return self.db.query(TaxonomySkill).filter(
            func.lower(TaxonomySkill.canonical_name) == clean
        ).first()

    def find_all_skills(self) -> List[TaxonomySkill]:
        return self.db.query(TaxonomySkill).all()

    def get_custom_skills(self) -> List[CustomSkill]:
        return self.db.query(CustomSkill).all()

    def add_custom_skill(self, canonical_name: str, aliases: List[str], skill_type: str = "framework", description: str = "") -> CustomSkill:
        custom = CustomSkill(
            canonical_name=canonical_name,
            aliases=aliases,
            skill_type=skill_type,
            description=description
        )
        self.db.add(custom)
        self.db.commit()
        self.db.refresh(custom)
        return custom

    def get_occupation_by_title(self, title: str) -> Optional[TaxonomyOccupation]:
        clean = title.strip().lower()
        return self.db.query(TaxonomyOccupation).filter(
            func.lower(TaxonomyOccupation.title).contains(clean)
        ).first()
