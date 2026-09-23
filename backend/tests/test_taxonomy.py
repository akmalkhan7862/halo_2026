import pytest
from app.core.database import SessionLocal
from app.services.taxonomy_service import TaxonomyService


def test_taxonomy_exact_resolution():
    db = SessionLocal()
    try:
        service = TaxonomyService(db)
        res = service.resolve_skill("Python")
        assert res["canonical_skill"] == "Python"
        assert res["confidence"] == 1.0
    finally:
        db.close()


def test_taxonomy_alias_resolution():
    db = SessionLocal()
    try:
        service = TaxonomyService(db)
        # Test alias resolution
        res_k8s = service.resolve_skill("k8s")
        assert res_k8s["canonical_skill"] == "Kubernetes"

        res_react = service.resolve_skill("reactjs")
        assert res_react["canonical_skill"] == "React"

        res_pg = service.resolve_skill("postgres")
        assert res_pg["canonical_skill"] == "PostgreSQL"
    finally:
        db.close()


def test_taxonomy_transferable_relationship():
    db = SessionLocal()
    try:
        service = TaxonomyService(db)
        is_rel, desc = service.are_skills_related("Flask", "FastAPI")
        assert is_rel is True

        is_rel, desc = service.are_skills_related("PostgreSQL", "MySQL")
        assert is_rel is True

        is_rel, desc = service.are_skills_related("Python", "Kubernetes")
        assert is_rel is False
    finally:
        db.close()
