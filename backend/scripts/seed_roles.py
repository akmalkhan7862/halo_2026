"""
Seed Benchmark Roles and Occupations
"""
import os
import sys
import uuid

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.database import SessionLocal, engine, Base
from app.models.taxonomy import TaxonomyOccupation, CustomSkill
from app.utils.logger import logger

BENCHMARK_ROLES = [
    {
        "source": "esco",
        "source_id": "occ-backend-dev",
        "title": "Backend Developer",
        "description": "Designs, implements, and maintains server-side web applications, databases, and microservices.",
        "required_skills": ["Python", "FastAPI", "PostgreSQL", "REST API", "Docker", "Git"],
        "optional_skills": ["Redis", "Kubernetes", "Amazon Web Services", "CI/CD", "System Design"]
    },
    {
        "source": "esco",
        "source_id": "occ-fullstack-dev",
        "title": "Full Stack Developer",
        "description": "Develops both user-facing client applications and backend APIs and database schemas.",
        "required_skills": ["JavaScript", "TypeScript", "React", "Python", "REST API", "Git"],
        "optional_skills": ["Docker", "PostgreSQL", "Amazon Web Services", "GraphQL"]
    },
    {
        "source": "onet",
        "source_id": "occ-devops-eng",
        "title": "DevOps Engineer",
        "description": "Automates deployments, cloud infrastructure, and CI/CD pipelines.",
        "required_skills": ["Docker", "Kubernetes", "CI/CD", "Amazon Web Services", "Git"],
        "optional_skills": ["Python", "System Design", "Terraform", "Monitoring"]
    }
]

CUSTOM_SKILLS = [
    {
        "canonical_name": "Pydantic",
        "aliases": ["pydantic v2", "pydantic validation"],
        "skill_type": "framework",
        "description": "Data validation and settings management using Python type annotations."
    },
    {
        "canonical_name": "SQLAlchemy",
        "aliases": ["sqlalchemy orm", "sql alchemy"],
        "skill_type": "framework",
        "description": "Python SQL toolkit and Object Relational Mapper."
    },
    {
        "canonical_name": "Tailwind CSS",
        "aliases": ["tailwindcss", "tailwind"],
        "skill_type": "framework",
        "description": "Utility-first CSS framework for rapid UI development."
    }
]


def seed_roles():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        # Seed Occupations
        for r in BENCHMARK_ROLES:
            existing = db.query(TaxonomyOccupation).filter(TaxonomyOccupation.source_id == r["source_id"]).first()
            if not existing:
                occ = TaxonomyOccupation(
                    id=str(uuid.uuid4()),
                    source=r["source"],
                    source_id=r["source_id"],
                    title=r["title"],
                    description=r["description"],
                    required_skills=r["required_skills"],
                    optional_skills=r["optional_skills"]
                )
                db.add(occ)

        # Seed Custom Skills
        for cs in CUSTOM_SKILLS:
            existing = db.query(CustomSkill).filter(CustomSkill.canonical_name == cs["canonical_name"]).first()
            if not existing:
                custom = CustomSkill(
                    id=str(uuid.uuid4()),
                    canonical_name=cs["canonical_name"],
                    aliases=cs["aliases"],
                    skill_type=cs["skill_type"],
                    description=cs["description"]
                )
                db.add(custom)

        db.commit()
        logger.info("Successfully seeded benchmark roles and custom framework skills.")
    except Exception as e:
        db.rollback()
        logger.error(f"Failed to seed roles: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed_roles()
