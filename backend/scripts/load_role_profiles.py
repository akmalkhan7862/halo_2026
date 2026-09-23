"""
CLI tool to inspect and reload curated target role profiles.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.database import SessionLocal
from app.services.role_profile_loader import RoleProfileLoaderService
from app.utils.logger import logger


def list_and_sync_roles():
    db = SessionLocal()
    try:
        loader = RoleProfileLoaderService(db)
        loader.sync_roles_to_database()
        roles = loader.get_all_roles()
        print(f"\n--- Loaded {len(roles)} Target Role Profiles ---")
        for r in roles:
            print(f"• [{r.role_key}] {r.display_name} ({r.seniority}, {r.domain})")
            print(f"  Required: {', '.join(r.required_skills or [])}")
            print(f"  Preferred: {', '.join(r.preferred_skills or [])}\n")
    finally:
        db.close()


if __name__ == "__main__":
    list_and_sync_roles()
