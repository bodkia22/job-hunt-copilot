"""SQLAlchemy models and session management for storing application history."""
from datetime import datetime
from pathlib import Path

from sqlalchemy import create_engine, String, Integer, Boolean, DateTime
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, sessionmaker

from src.config import settings
from sqlalchemy import Text


class Base(DeclarativeBase):
    pass


class ApplicationRecord(Base):
    __tablename__ = "applications"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    company_name: Mapped[str] = mapped_column(String)
    position_title: Mapped[str] = mapped_column(String)
    match_percentage: Mapped[int] = mapped_column(Integer)
    is_good_fit: Mapped[bool] = mapped_column(Boolean)
    status: Mapped[str] = mapped_column(String, default="new")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    cover_letter_text: Mapped[str] = mapped_column(Text)



engine = create_engine(f"sqlite:///{settings.db_path}")

Base.metadata.create_all(engine)

SessionLocal = sessionmaker(bind=engine)

def save_application(
    company_name: str,
    position_title: str,
    match_percentage: int,
    is_good_fit: bool,
    cover_letter_text: str,
) -> None:
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