import os
import uuid
import yaml
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.role_profile import RoleProfile
from app.repositories.role_profile_repo import RoleProfileRepository
from app.utils.logger import logger


class RoleProfileLoaderService:
    def __init__(self, db: Optional[Session] = None):
        self.db = db
        self.repo = RoleProfileRepository(db) if db else None
        self.config_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
            "data",
            "roles_config.yaml"
        )

    def load_roles_from_yaml(self) -> List[Dict[str, Any]]:
        """Reads target roles defined in roles_config.yaml."""
        if not os.path.exists(self.config_path):
            logger.warning(f"roles_config.yaml not found at {self.config_path}")
            return []
        try:
            with open(self.config_path, "r", encoding="utf-8") as f:
                data = yaml.safe_load(f)
                return data.get("target_roles", [])
        except Exception as e:
            logger.error(f"Error parsing roles_config.yaml: {e}")
            return []

    def sync_roles_to_database(self) -> int:
        """Loads YAML definitions into PostgreSQL/SQLite role_profiles table."""
        if not self.db:
            return 0

        roles = self.load_roles_from_yaml()
        count = 0

        for r in roles:
            role_key = r.get("role_key", "").strip().lower()
            if not role_key:
                continue

            existing = self.repo.get_by_role_key(role_key)
            if existing:
                existing.display_name = r.get("display_name", existing.display_name)
                existing.seniority = r.get("seniority", existing.seniority)
                existing.domain = r.get("domain", existing.domain)
                existing.description = r.get("description", existing.description)
                existing.sources = r.get("sources", existing.sources)
                existing.required_skills = r.get("required_skills", existing.required_skills)
                existing.preferred_skills = r.get("preferred_skills", existing.preferred_skills)
            else:
                profile = RoleProfile(
                    id=str(uuid.uuid4()),
                    role_key=role_key,
                    display_name=r.get("display_name", role_key.title()),
                    seniority=r.get("seniority", "mid"),
                    domain=r.get("domain", "software_engineering"),
                    description=r.get("description", ""),
                    sources=r.get("sources", []),
                    required_skills=r.get("required_skills", []),
                    preferred_skills=r.get("preferred_skills", [])
                )
                self.db.add(profile)
                count += 1

        self.db.commit()
        logger.info(f"Synchronized {len(roles)} role profiles to database ({count} new).")
        return count

    def get_all_roles(self) -> List[RoleProfile]:
        """Retrieves all role profiles from database, falling back to YAML if DB is empty."""
        if self.repo:
            db_roles = self.repo.list_all_roles()
            if db_roles:
                return db_roles

        # Fallback to YAML objects if DB is unseeded
        yaml_roles = self.load_roles_from_yaml()
        mock_profiles = []
        for r in yaml_roles:
            mock_profiles.append(RoleProfile(
                id=str(uuid.uuid4()),
                role_key=r["role_key"],
                display_name=r.get("display_name", r["role_key"]),
                seniority=r.get("seniority", "mid"),
                domain=r.get("domain", "software_engineering"),
                description=r.get("description", ""),
                sources=r.get("sources", []),
                required_skills=r.get("required_skills", []),
                preferred_skills=r.get("preferred_skills", [])
            ))
        return mock_profiles

    def get_role_by_key(self, role_key: str) -> Optional[RoleProfile]:
        """Retrieves single role profile by role_key."""
        key = role_key.strip().lower()
        if self.repo:
            db_role = self.repo.get_by_role_key(key)
            if db_role:
                return db_role

        # Fallback to YAML
        yaml_roles = self.load_roles_from_yaml()
        for r in yaml_roles:
            if r.get("role_key", "").strip().lower() == key:
                return RoleProfile(
                    id=str(uuid.uuid4()),
                    role_key=r["role_key"],
                    display_name=r.get("display_name", r["role_key"]),
                    seniority=r.get("seniority", "mid"),
                    domain=r.get("domain", "software_engineering"),
                    description=r.get("description", ""),
                    sources=r.get("sources", []),
                    required_skills=r.get("required_skills", []),
                    preferred_skills=r.get("preferred_skills", [])
                )
        return None


RoleProfileLoader = RoleProfileLoaderService
