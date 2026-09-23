import traceback
from sqlalchemy.orm import Session
from app.core.database import SessionLocal
from app.models.resume import Resume
from app.services.resume_parser import ResumeParserService
from app.services.taxonomy_service import TaxonomyService
from app.services.entity_extractor import EntityExtractorService
from app.utils.logger import logger


def process_resume_background(resume_id: str, file_bytes: bytes, filename: str):
    """Asynchronous background worker to parse resume and extract entities."""
    db: Session = SessionLocal()
    try:
        resume = db.query(Resume).filter(Resume.id == resume_id).first()
        if not resume:
            logger.error(f"Background task: Resume {resume_id} not found.")
            return

        parser = ResumeParserService()
        raw_text, ext = parser.extract_raw_text(filename, file_bytes)
        sections = parser.segment_sections(raw_text)

        taxonomy_service = TaxonomyService(db)
        extractor = EntityExtractorService(taxonomy_service)
        parsed_data = extractor.extract_all(sections, raw_text)

        resume.raw_text = raw_text
        resume.parsed_json = parsed_data
        resume.status = "processed"
        db.commit()
        logger.info(f"Background processing complete for resume {resume_id}")
    except Exception as e:
        logger.error(f"Error in background processing of resume {resume_id}: {e}\n{traceback.format_exc()}")
        try:
            resume = db.query(Resume).filter(Resume.id == resume_id).first()
            if resume:
                resume.status = "failed"
                resume.raw_text = resume.raw_text or "Error processing file."
                db.commit()
        except Exception:
            pass
    finally:
        db.close()
