"""Pydantic data models for vacancies, CV chunks, and match results."""
from typing import Literal
from pydantic import BaseModel, Field


class VacancyRequirements(BaseModel):
    company_name: str = Field(
        description="The hiring company's name, exactly as stated in the posting."
    )
    position_title: str = Field(
        description="The job title as stated in the posting, e.g. 'Junior AI Engineer'."
    )
    seniority_level: Literal["junior", "junior+", "middle", "senior"] = Field(
        description="Seniority level explicitly stated or clearly implied in the posting."
    )
    work_format: Literal["remote", "office", "hybrid", "remote_or_office"] = Field(
        description="Work arrangement explicitly stated, e.g. fully remote, office-only, "
        "hybrid, or remote-or-office choice."
    )
    company_domain: str = Field(
        description="Short description (5-10 words) of the company's industry and what "
        "it does, e.g. 'marketing agency providing digital services to clients'."
    )
    company_type: Literal["product", "outsource", "outstaff", "agency", "other"] = Field(
        description="Business model of the company: builds its own product, outsources "
        "development for clients, provides staff to clients (outstaff), runs services as "
        "an agency for clients, or none of these clearly apply (other)."
    )
    required_skills: list[str] = Field(
        description="Skills, tools, and technologies explicitly listed as required or "
        "important (e.g. under headings like 'must have', 'required', 'what matters to us'). "
        "Do not include skills only mentioned as a bonus or plus."
    )
    nice_to_have_skills: list[str] = Field(
        description="Skills, tools, and technologies explicitly listed as a bonus, plus, "
        "or optional advantage (e.g. under headings like 'nice to have', 'will be a plus'). "
        "Do not include skills listed as required."
    )
    required_languages: dict[str, str] = Field(
        description="Spoken/written language requirements as a mapping of language name "
        "(lowercase, e.g. 'english') to the proficiency level exactly as stated in the "
        "posting (e.g. 'B1', 'native')."
    )
    min_experience_years: float | None = Field(
        default=None,
        description="Minimum years of professional experience explicitly required, if "
        "stated. Use the most relevant/primary skill's required years if multiple are "
        "listed. Null if not specified.",
    )

class MatchResult(BaseModel):
    match_percentage: int = Field(
        ge=0, le=100,
        description="Overall fit score from 0 to 100, based on how well the candidate's "
        "CV matches the vacancy's required and nice-to-have skills."
    )
    is_good_fit: bool = Field(
        description="Whether the candidate is realistically a good fit for this position, "
        "considering both matched skills and any disqualifying gaps."
    )
    matched_skills: list[str] = Field(
        description="Skills/technologies from the vacancy's requirements that are clearly "
        "present in the candidate's CV."
    )
    missing_skills: list[str] = Field(
        description="Skills/technologies required or preferred by the vacancy that are NOT "
        "found in the candidate's CV."
    )
    red_flags: list[str] = Field(
        default_factory=list,
        description="Hard disqualifiers explicitly stated in the vacancy that the candidate "
        "clearly does not meet, e.g. a required language level, a mandatory certification, "
        "or a minimum years-of-experience threshold the candidate falls short of."
    )
