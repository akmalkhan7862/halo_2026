import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Text, DateTime, ForeignKey, Index
from sqlalchemy.orm import relationship

from app.models.base import Base, GUID, CompatibleJSON


class TaxonomySkill(Base):
    __tablename__ = "taxonomy_skills"

    id = Column(GUID, primary_key=True, default=lambda: str(uuid.uuid4()))
    source = Column(String(50), nullable=False, default="custom")  # 'esco', 'onet', 'custom'
    source_id = Column(String(255), nullable=True, index=True)
    canonical_name = Column(String(255), nullable=False, index=True)
    aliases = Column(CompatibleJSON, nullable=False, default=list)  # list of strings
    skill_type = Column(String(100), nullable=True, default="technical")  # knowledge, skill, tool, soft_skill
    description = Column(Text, nullable=True)
    parent_id = Column(GUID, ForeignKey("taxonomy_skills.id"), nullable=True)
    embedding = Column(CompatibleJSON, nullable=True)  # vector representation as list or pgvector
    related_skills = Column(CompatibleJSON, nullable=True, default=list)  # list of transferable/related skill names
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    children = relationship("TaxonomySkill", backref="parent", remote_side=[id])

    __table_args__ = (
        Index("idx_taxonomy_canonical_lower", canonical_name),
    )


class TaxonomyOccupation(Base):
    __tablename__ = "taxonomy_occupations"

    id = Column(GUID, primary_key=True, default=lambda: str(uuid.uuid4()))
    source = Column(String(50), nullable=False, default="esco")
    source_id = Column(String(255), nullable=True, index=True)
    title = Column(String(255), nullable=False, index=True)
    description = Column(Text, nullable=True)
    required_skills = Column(CompatibleJSON, nullable=False, default=list)
    optional_skills = Column(CompatibleJSON, nullable=False, default=list)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)


class CustomSkill(Base):
    __tablename__ = "custom_skills"

    id = Column(GUID, primary_key=True, default=lambda: str(uuid.uuid4()))
    canonical_name = Column(String(255), nullable=False, unique=True, index=True)
    aliases = Column(CompatibleJSON, nullable=False, default=list)
    skill_type = Column(String(100), nullable=True, default="framework")
    description = Column(Text, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
