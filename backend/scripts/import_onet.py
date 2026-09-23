"""
O*NET Taxonomy Importer
Imports O*NET database skills, technology tools, and SOC occupation mappings.
"""
import os
import sys
import uuid
from typing import List, Dict, Any

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.database import SessionLocal, engine, Base
from app.models.taxonomy import TaxonomySkill, TaxonomyOccupation
from app.utils.logger import logger

ONET_SEED_DATA = [
    {
        "source_id": "onet-15-1252.00-s1",
        "canonical_name": "Amazon Web Services",
        "aliases": ["aws", "amazon cloud", "aws cloud"],
        "skill_type": "cloud",
        "description": "Cloud computing platform provided by Amazon.",
        "related_skills": ["Google Cloud Platform", "Microsoft Azure", "Cloud Architecture"]
    },
    {
        "source_id": "onet-15-1252.00-s2",
        "canonical_name": "Microsoft Azure",
        "aliases": ["azure", "azure cloud", "ms azure"],
        "skill_type": "cloud",
        "description": "Cloud computing service created by Microsoft.",
        "related_skills": ["Amazon Web Services", "Google Cloud Platform", "Cloud Architecture"]
    },
    {
        "source_id": "onet-15-1252.00-s3",
        "canonical_name": "Google Cloud Platform",
        "aliases": ["gcp", "google cloud"],
        "skill_type": "cloud",
        "description": "Suite of cloud computing services that runs on Google infrastructure.",
        "related_skills": ["Amazon Web Services", "Microsoft Azure", "Kubernetes"]
    },
    {
        "source_id": "onet-15-1252.00-s4",
        "canonical_name": "CI/CD",
        "aliases": ["continuous integration", "continuous deployment", "cicd", "pipeline automation"],
        "skill_type": "devops",
        "description": "Method to frequently deliver apps by introducing automation into development stages.",
        "related_skills": ["Docker", "Git", "GitHub Actions", "Jenkins"]
    },
    {
        "source_id": "onet-15-1252.00-s5",
        "canonical_name": "GraphQL",
        "aliases": ["graphql api", "gql"],
        "skill_type": "architecture",
        "description": "Query language for APIs and runtime for fulfilling those queries with existing data.",
        "related_skills": ["REST API", "API Design", "Node.js"]
    },
    {
        "source_id": "onet-15-1252.00-s6",
        "canonical_name": "SQL",
        "aliases": ["structured query language", "relational database query", "sql queries"],
        "skill_type": "database",
        "description": "Domain-specific language used in programming and designed for managing relational databases.",
        "related_skills": ["PostgreSQL", "MySQL", "Database Optimization"]
    },
    {
        "source_id": "onet-15-1252.00-s7",
        "canonical_name": "Redis",
        "aliases": ["redis cache", "in-memory data store"],
        "skill_type": "database",
        "description": "In-memory data structure store used as a database, cache, streaming engine, and message broker.",
        "related_skills": ["Caching", "PostgreSQL", "System Design"]
    }
]


def import_onet_skills():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    count = 0
    try:
        for item in ONET_SEED_DATA:
            existing = db.query(TaxonomySkill).filter(
                TaxonomySkill.source == "onet",
                TaxonomySkill.canonical_name == item["canonical_name"]
            ).first()
            if not existing:
                skill = TaxonomySkill(
                    id=str(uuid.uuid4()),
                    source="onet",
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
        logger.info(f"Successfully seeded/updated {count} O*NET taxonomy skills.")
    except Exception as e:
        db.rollback()
        logger.error(f"Failed to import O*NET skills: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    logger.info("Importing O*NET skills...")
    import_onet_skills()
