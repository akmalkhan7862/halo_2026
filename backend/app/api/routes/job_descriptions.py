import uuid
from typing import Optional
from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.exceptions import ResourceNotFoundException, FileValidationError
from app.models.user import User
from app.models.job_description import JobDescription
from app.repositories.jd_repo import JobDescriptionRepository
from app.schemas.job_description import JDCreate, JDResponse
from app.api.deps import get_current_user, get_taxonomy_service
from app.services.taxonomy_service import TaxonomyService
from app.services.jd_parser import JobDescriptionParserService
from app.services.resume_parser import ResumeParserService

router = APIRouter(prefix="/job-descriptions", tags=["Job Descriptions"])


@router.post("", response_model=JDResponse, status_code=status.HTTP_201_CREATED)
async def create_job_description(
    title: Optional[str] = Form(None),
    company: Optional[str] = Form(None),
    raw_text: Optional[str] = Form(None),
    url: Optional[str] = Form(None),
    file: Optional[UploadFile] = File(None),
    db: Session = Depends(get_db),
    taxonomy_service: TaxonomyService = Depends(get_taxonomy_service),
    current_user: Optional[User] = Depends(get_current_user)
):
    """
    Creates and parses a Job Description from raw text, file upload, or public URL.
    """
    jd_parser = JobDescriptionParserService(taxonomy_service)
    text_content = ""

    if raw_text and raw_text.strip():
        text_content = raw_text.strip()
    elif url and url.strip():
        text_content = await jd_parser.fetch_url_content(url.strip())
    elif file:
        file_bytes = await file.read()
        filename = file.filename or "job_description.txt"
        parser = ResumeParserService()
        text_content, _ = parser.extract_raw_text(filename, file_bytes)
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You must provide either raw_text, a valid url, or a document file."
        )

    parsed_jd = jd_parser.parse(text_content, title=title, company=company)
    resolved_title = parsed_jd.get("job_title", title or "Target Role")

    jd_id = str(uuid.uuid4())
    user_id = current_user.id if current_user else None

    jd = JobDescription(
        id=jd_id,
        user_id=user_id,
        title=resolved_title,
        company=company or parsed_jd.get("company"),
        raw_text=text_content,
        parsed_json=parsed_jd
    )

    repo = JobDescriptionRepository(db)
    created = repo.create(jd)
    return created


@router.get("/{jd_id}", response_model=JDResponse)
def get_job_description(jd_id: str, db: Session = Depends(get_db)):
    repo = JobDescriptionRepository(db)
    jd = repo.get(jd_id)
    if not jd:
        raise ResourceNotFoundException("JobDescription", jd_id)
    return jd
