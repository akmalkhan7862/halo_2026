import uuid
from typing import Generator
from sqlalchemy import create_engine, String, JSON
from sqlalchemy.orm import declarative_base, sessionmaker, Session
from sqlalchemy.types import TypeDecorator
from sqlalchemy.dialects.postgresql import UUID as PG_UUID, JSONB as PG_JSONB

from app.core.config import settings


# Cross-dialect UUID type
class GUID(TypeDecorator):
    impl = String(36)
    cache_ok = True

    def load_dialect_impl(self, dialect):
        if dialect.name == "postgresql":
            return dialect.type_descriptor(PG_UUID(as_uuid=True))
        else:
            return dialect.type_descriptor(String(36))

    def process_bind_param(self, value, dialect):
        if value is None:
            return value
        elif dialect.name == "postgresql":
            return str(value)
        else:
            if isinstance(value, uuid.UUID):
                return str(value)
            return str(value)

    def process_result_value(self, value, dialect):
        if value is None:
            return value
        if isinstance(value, uuid.UUID):
            return str(value)
        return str(value)


# Cross-dialect JSONB/JSON type
class CompatibleJSON(TypeDecorator):
    impl = JSON
    cache_ok = True

    def load_dialect_impl(self, dialect):
        if dialect.name == "postgresql":
            return dialect.type_descriptor(PG_JSONB())
        else:
            return dialect.type_descriptor(JSON())


connect_args = {}
if settings.DATABASE_URL.startswith("sqlite"):
    connect_args = {"check_same_thread": False}

engine = create_engine(
    settings.DATABASE_URL,
    connect_args=connect_args,
    echo=False,
    future=True
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def ensure_sqlite_columns():
    if settings.DATABASE_URL.startswith("sqlite"):
        try:
            from sqlalchemy import text
            with engine.connect() as conn:
                res = conn.execute(text("SELECT name FROM sqlite_master WHERE type='table' AND name='analysis_results'")).fetchone()
                if res:
                    col_res = conn.execute(text("PRAGMA table_info(analysis_results)"))
                    existing_cols = {row[1] for row in col_res.fetchall()}
                    if "gap_analysis" not in existing_cols:
                        conn.execute(text("ALTER TABLE analysis_results ADD COLUMN gap_analysis JSON DEFAULT '{}'"))
                    if "learning_roadmap" not in existing_cols:
                        conn.execute(text("ALTER TABLE analysis_results ADD COLUMN learning_roadmap JSON DEFAULT '{}'"))
                    conn.commit()
        except Exception:
            pass

ensure_sqlite_columns()
