"""SQLAlchemy models and session management for storing application history."""
import logging
from datetime import datetime, timezone

from sqlalchemy import create_engine, String, Integer, Boolean, DateTime, func, Text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, sessionmaker

from src.config import settings

logger = logging.getLogger(__name__)


class Base(DeclarativeBase):
    """SQLAlchemy declarative base class."""


class ApplicationRecord(Base):
    """ORM model representing a job application record stored in the database."""

    __tablename__ = "applications"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    company_name: Mapped[str] = mapped_column(String)
    position_title: Mapped[str] = mapped_column(String)
    match_percentage: Mapped[int] = mapped_column(Integer)
    is_good_fit: Mapped[bool] = mapped_column(Boolean)
    status: Mapped[str] = mapped_column(String, default="new")
    created_at: Mapped[datetime] = mapped_column(
        default=lambda: datetime.now(timezone.utc),
        server_default=func.now(),
    )
    cover_letter_text: Mapped[str] = mapped_column(Text)

engine = create_engine(f"sqlite:///{settings.db_path}")
SessionLocal = sessionmaker(bind=engine)

def init_db() -> None:
    """Create all database tables if they do not already exist."""
    logger.debug("Initializing database at %s", settings.db_path)
    Base.metadata.create_all(engine)

def save_application(
    company_name: str,
    position_title: str,
    match_percentage: int,
    is_good_fit: bool,
    cover_letter_text: str,
) -> None:
    """Persist a job application record to the database.

    Args:
        company_name: Name of the hiring company.
        position_title: Title of the applied position.
        match_percentage: CV-to-vacancy fit score (0–100).
        is_good_fit: Whether the candidate is considered a good fit.
        cover_letter_text: Generated cover letter content.
    """
    with SessionLocal() as session:
        record = ApplicationRecord(
            company_name=company_name,
            position_title=position_title,
            match_percentage=match_percentage,
            is_good_fit=is_good_fit,
            cover_letter_text=cover_letter_text,
        )
        session.add(record)
        session.commit()
        logger.info(
            "Saved application record id=%d for %s — %s",
            record.id,
            company_name,
            position_title,
        )