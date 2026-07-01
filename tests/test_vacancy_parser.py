"""Tests for the vacancy parser module."""
from unittest.mock import patch, MagicMock
from src.vacancy_parser import parse_vacancy
from src.models import VacancyRequirements

FAKE_VACANCY = VacancyRequirements(
    company_name="TestCorp",
    position_title="Junior Python Developer",
    seniority_level="junior",
    work_format="remote",
    company_domain="Software development agency",
    company_type="product",
    required_skills=["Python", "FastAPI"],
    nice_to_have_skills=["Docker"],
    required_languages={"english": "B2"},
    min_experience_years=1.0,
)

def test_parse_vacancy_returns_vacancy_requirements():
    with patch("src.vacancy_parser.chain") as mock_chain:
        mock_chain.invoke.return_value = FAKE_VACANCY
        res = parse_vacancy("Some vacancy text")
        assert isinstance(res, VacancyRequirements)
        assert res.company_name == "TestCorp"
        assert res.position_title == "Junior Python Developer"
        assert res.seniority_level == "junior"
        assert res.required_skills == ["Python", "FastAPI"]
        pass
