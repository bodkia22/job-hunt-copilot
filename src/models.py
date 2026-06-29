"""Pydantic data models for vacancies, CV chunks, and match results."""
from typing import Literal
from pydantic import BaseModel

class VacancyRequirements(BaseModel):
    company_name: str
    position_title: str
    seniority_level: Literal["junior", "junior+", "middle", "senior"]
    work_format: Literal["remote", "office", "hybrid", "remote_or_office"]
    company_domain: str
    company_type: Literal["product", "outsource", "outstaff", "agency", "other"]
    required_skills: list[str]
    nice_to_have_skills: list[str]
    required_languages: dict[str, str]

    min_experience_years: float | None = None