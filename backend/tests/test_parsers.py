import os
import pytest
from app.services.resume_parser import ResumeParserService
from app.services.taxonomy_service import TaxonomyService
from app.services.entity_extractor import EntityExtractorService
from app.core.database import SessionLocal

FIXTURES_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "fixtures")


def test_parse_clean_pdf():
    parser = ResumeParserService()
    pdf_path = os.path.join(FIXTURES_DIR, "clean_resume.pdf")
    with open(pdf_path, "rb") as f:
        bytes_data = f.read()

    text, ext = parser.extract_raw_text("clean_resume.pdf", bytes_data)
    assert ext == "pdf"
    assert "Alex Morgan" in text
    assert "FastAPI" in text
    assert "PostgreSQL" in text

    sections = parser.segment_sections(text)
    assert "skills" in sections or "body" in sections


def test_parse_clean_docx():
    parser = ResumeParserService()
    docx_path = os.path.join(FIXTURES_DIR, "clean_resume.docx")
    with open(docx_path, "rb") as f:
        bytes_data = f.read()

    text, ext = parser.extract_raw_text("clean_resume.docx", bytes_data)
    assert ext == "docx"
    assert "Taylor Reed" in text
    assert "React" in text


def test_entity_extraction_with_evidence():
    parser = ResumeParserService()
    pdf_path = os.path.join(FIXTURES_DIR, "clean_resume.pdf")
    with open(pdf_path, "rb") as f:
        bytes_data = f.read()

    text, _ = parser.extract_raw_text("clean_resume.pdf", bytes_data)
    sections = parser.segment_sections(text)

    db = SessionLocal()
    try:
        taxonomy = TaxonomyService(db)
        extractor = EntityExtractorService(taxonomy)
        data = extractor.extract_all(sections, text)

        assert data["contact"]["email"] == "alex.morgan@example.com"
        assert len(data["skills"]) > 0

        skill_names = [s["canonical_skill"] for s in data["skills"]]
        assert "FastAPI" in skill_names or "Python" in skill_names

        # Verify evidence retention
        for s in data["skills"]:
            assert "evidence" in s
            assert len(s["evidence"]) > 0
    finally:
        db.close()
