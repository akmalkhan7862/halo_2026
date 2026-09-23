from typing import Generator, Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.core.database import SessionLocal, get_db
from app.core.security import decode_token
from app.core.exceptions import UnauthorizedException
from app.models.user import User
from app.repositories.user_repo import UserRepository
from app.services.taxonomy_service import TaxonomyService
from app.services.skill_matcher import SkillMatcherService
from app.services.gap_analyzer import GapAnalyzerService
from app.services.scoring_engine import ScoringEngineService
from app.services.llm_client import BaseLLMClient, get_llm_client

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login", auto_error=False)


def get_current_user(
    db: Session = Depends(get_db),
    token: Optional[str] = Depends(oauth2_scheme)
) -> Optional[User]:
    if not token:
        return None
    user_id = decode_token(token)
    if not user_id:
        raise UnauthorizedException("Could not validate credentials")
    user_repo = UserRepository(db)
    user = user_repo.get(user_id)
    if not user:
        raise UnauthorizedException("User not found")
    return user


def get_taxonomy_service(db: Session = Depends(get_db)) -> TaxonomyService:
    return TaxonomyService(db)


def get_skill_matcher(taxonomy_service: TaxonomyService = Depends(get_taxonomy_service)) -> SkillMatcherService:
    return SkillMatcherService(taxonomy_service)


def get_gap_analyzer() -> GapAnalyzerService:
    return GapAnalyzerService()


def get_scoring_engine() -> ScoringEngineService:
    return ScoringEngineService()


def get_llm() -> BaseLLMClient:
    return get_llm_client()
