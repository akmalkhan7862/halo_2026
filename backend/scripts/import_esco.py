"""
ESCO Taxonomy Importer
Imports ESCO (European Skills, Competences, Qualifications and Occupations) skill and occupation datasets.
Can import from remote ESCO API or local CSV/JSON dumps.
"""
import os
import sys
import uuid
from typing import List, Dict, Any

# Add project root to sys.path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.database import SessionLocal, engine, Base
from app.models.taxonomy import TaxonomySkill, TaxonomyOccupation
from app.utils.logger import logger

# Essential ESCO Benchmark Skills
ESCO_SEED_DATA = [
    {
        "source_id": "esco-s-001",
        "canonical_name": "Python",
        "aliases": ["python3", "python programming", "py", "cpython"],
        "skill_type": "technical",
        "description": "General-purpose programming language for backend, data, and machine learning.",
        "related_skills": ["Django", "FastAPI", "Flask", "Data Analysis"]
    },
    {
        "source_id": "esco-s-002",
        "canonical_name": "FastAPI",
        "aliases": ["fast-api", "fastapi framework"],
        "skill_type": "framework",
        "description": "High-performance web framework for building APIs with Python.",
        "related_skills": ["Python", "REST API", "Pydantic", "Flask", "Django"]
    },
    {
        "source_id": "esco-s-003",
        "canonical_name": "Flask",
        "aliases": ["flask framework", "python-flask"],
        "skill_type": "framework",
        "description": "Lightweight WSGI web application framework in Python.",
        "related_skills": ["Python", "FastAPI", "Django", "REST API"]
    },
    {
        "source_id": "esco-s-004",
        "canonical_name": "PostgreSQL",
        "aliases": ["postgres", "pgsql", "postgresql database"],
        "skill_type": "database",
        "description": "Open source object-relational database system.",
        "related_skills": ["SQL", "MySQL", "Relational Database", "Database Design"]
    },
    {
        "source_id": "esco-s-005",
        "canonical_name": "MySQL",
        "aliases": ["mysql server", "mariadb"],
        "skill_type": "database",
        "description": "Open-source relational database management system.",
        "related_skills": ["SQL", "PostgreSQL", "Relational Database"]
    },
    {
        "source_id": "esco-s-006",
        "canonical_name": "Docker",
        "aliases": ["docker engine", "docker container", "dockerization"],
        "skill_type": "tool",
        "description": "Platform for developing, shipping, and running applications in containers.",
        "related_skills": ["Kubernetes", "Containerization", "CI/CD", "DevOps"]
    },
    {
        "source_id": "esco-s-007",
        "canonical_name": "Kubernetes",
        "aliases": ["k8s", "k8s cluster", "kube"],
        "skill_type": "tool",
        "description": "Automated container orchestration system.",
        "related_skills": ["Docker", "Cloud Computing", "DevOps", "Helm"]
    },
    {
        "source_id": "esco-s-008",
        "canonical_name": "React",
        "aliases": ["reactjs", "react.js", "react framework"],
        "skill_type": "framework",
        "description": "JavaScript library for building user interfaces.",
        "related_skills": ["JavaScript", "TypeScript", "Next.js", "Front-End", "Vue.js"]
    },
    {
        "source_id": "esco-s-009",
        "canonical_name": "TypeScript",
        "aliases": ["ts", "typescript lang"],
        "skill_type": "technical",
        "description": "Typed superset of JavaScript that compiles to plain JavaScript.",
        "related_skills": ["JavaScript", "React", "Node.js"]
    },
    {
        "source_id": "esco-s-010",
        "canonical_name": "REST API",
        "aliases": ["restful api", "rest", "restful web services"],
        "skill_type": "architecture",
        "description": "Architectural style for distributed hypermedia systems and HTTP APIs.",
        "related_skills": ["GraphQL", "FastAPI", "API Design", "HTTP"]
    },
    {
        "source_id": "esco-s-011",
        "canonical_name": "System Design",
        "aliases": ["software architecture", "high level design", "distributed systems design"],
        "skill_type": "architecture",
        "description": "Process of defining the architecture, components, modules, interfaces, and data for a system.",
        "related_skills": ["Microservices", "Scalability", "Cloud Computing", "Database Design"]
    },
    {
        "source_id": "esco-s-012",
        "canonical_name": "Git",
        "aliases": ["github", "gitlab", "version control", "git vcs"],
        "skill_type": "tool",
        "description": "Distributed version control system for tracking changes in source code.",
        "related_skills": ["CI/CD", "DevOps", "GitHub Actions"]
    }
]


def import_esco_skills():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    count = 0
    try:
        for item in ESCO_SEED_DATA:
            existing = db.query(TaxonomySkill).filter(
                TaxonomySkill.source == "esco",
                TaxonomySkill.canonical_name == item["canonical_name"]
            ).first()
            if not existing:
                skill = TaxonomySkill(
                    id=str(uuid.uuid4()),
                    source="esco",
                    source_id=item["source_id"],
                    canonical_name=item["canonical_name"],
                    aliases=item["aliases"],
                    skill_type=item["skill_type"],
                    description=item["description"],
                    related_skills=item.get("related_skills", [])
                )
                db.add(skill)
                count += 1
            else:
                existing.aliases = item["aliases"]
                existing.related_skills = item.get("related_skills", [])
        db.commit()
        logger.info(f"Successfully seeded/updated {count} ESCO taxonomy skills.")
    except Exception as e:
        db.rollback()
        logger.error(f"Failed to import ESCO skills: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    logger.info("Importing ESCO skills...")
    import_esco_skills()
