import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Text, DateTime, Index
from app.models.base import Base, GUID, CompatibleJSON


class RoleProfile(Base):
    __tablename__ = "role_profiles"

    id = Column(GUID, primary_key=True, default=lambda: str(uuid.uuid4()))
    role_key = Column(String(100), unique=True, index=True, nullable=False)
    display_name = Column(String(255), nullable=False)
    seniority = Column(String(50), nullable=False, default="mid")
    domain = Column(String(100), nullable=False, default="software_engineering")
    description = Column(Text, nullable=True)
    sources = Column(CompatibleJSON, nullable=False, default=list)  # list of source objects (ESCO, O*NET)
    required_skills = Column(CompatibleJSON, nullable=False, default=list)  # list of canonical skill names
    preferred_skills = Column(CompatibleJSON, nullable=False, default=list)  # list of canonical skill names
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)

    __table_args__ = (
        Index("idx_role_profiles_domain", domain),
    )
