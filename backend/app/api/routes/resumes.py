import uuid
from typing import Optional
from fastapi import APIRouter, Depends, UploadFile, File, BackgroundTasks, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.exceptions import ResourceNotFoundException, FileValidationError
from app.models.user import User
from app.models.resume import Resume
from app.repositories.resume_repo import ResumeRepository
from app.schemas.resume import ResumeUploadResponse, ResumeDetailResponse, ResumeStatusResponse
from app.api.deps import get_current_user
from app.services.resume_parser import ResumeParserService
from app.services.taxonomy_service import TaxonomyService
from app.services.entity_extractor import EntityExtractorService
from app.workers.background_tasks import process_resume_background

router = APIRouter(prefix="/resumes", tags=["Resumes"])


@router.post("/upload", response_model=ResumeUploadResponse, status_code=status.HTTP_202_ACCEPTED)
async def upload_resume(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    async_processing: bool = False,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user)
):
    """
    Accepts PDF or DOCX resume. Validates file, creates record, and triggers parsing.
    If async_processing is True, runs via BackgroundTasks; otherwise processes inline.
    """
    file_bytes = await file.read()
    filename = file.filename or "uploaded_resume.pdf"

    parser = ResumeParserService()
    ext = parser.validate_file(filename, file_bytes)

    resume_id = str(uuid.uuid4())
    user_id = current_user.id if current_user else None

    if async_processing:
        # Create pending record
        resume = Resume(
            id=resume_id,
            user_id=user_id,
            original_filename=filename,
            file_type=ext,
            raw_text="Processing...",
            status="processing"
        )
        db.add(resume)
        db.commit()

        background_tasks.add_task(process_resume_background, resume_id, file_bytes, filename)
        return {
            "resume_id": resume_id,
            "original_filename": filename,
            "file_type": ext,
            "status": "processing",
            "message": "Resume uploaded. Parsing running asynchronously in background."
        }
    else:
        # Synchronous parsing for immediate reactivity
        raw_text, _ = parser.extract_raw_text(filename, file_bytes)
        sections = parser.segment_sections(raw_text)

        taxonomy_service = TaxonomyService(db)
        extractor = EntityExtractorService(taxonomy_service)
        parsed_data = extractor.extract_all(sections, raw_text)

        resume = Resume(
            id=resume_id,
            user_id=user_id,
            original_filename=filename,
            file_type=ext,
            raw_text=raw_text,
            parsed_json=parsed_data,
            status="processed"
        )
        db.add(resume)
        db.commit()

        return {
            "resume_id": resume_id,
            "original_filename": filename,
            "file_type": ext,
            "status": "processed",
            "message": "Resume parsed successfully."
        }


@router.get("/{resume_id}", response_model=ResumeDetailResponse)
def get_resume(resume_id: str, db: Session = Depends(get_db)):
    repo = ResumeRepository(db)
    resume = repo.get(resume_id)
    if not resume:
        raise ResourceNotFoundException("Resume", resume_id)
    return resume


@router.get("/{resume_id}/status", response_model=ResumeStatusResponse)
def get_resume_status(resume_id: str, db: Session = Depends(get_db)):
    repo = ResumeRepository(db)
    resume = repo.get(resume_id)
    if not resume:
        raise ResourceNotFoundException("Resume", resume_id)
    return {
        "id": resume.id,
        "status": resume.status,
        "filename": resume.original_filename
    }
