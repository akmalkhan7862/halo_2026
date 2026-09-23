"""
Seed Curated Target Roles from ESCO and O*NET
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.database import SessionLocal, engine, Base
from app.services.role_profile_loader import RoleProfileLoaderService
from app.utils.logger import logger


def seed_target_roles():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        loader = RoleProfileLoaderService(db)
        count = loader.sync_roles_to_database()
        logger.info(f"Target roles seeded successfully ({count} processed).")
    except Exception as e:
        db.rollback()
        logger.error(f"Failed to seed target roles: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed_target_roles()
