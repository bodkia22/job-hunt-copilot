"""Tests for the matcher module."""
from unittest.mock import patch
from src.matcher import match_cv_to_vacancy
from src.models import VacancyRequirements, MatchResult

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
FAKE_MATCH = MatchResult(
    match_percentage=75,
    is_good_fit=True,
    matched_skills=["Python"],
    missing_skills=[],
    red_flags=[],
)

def test_match_returns_match_result():
    with patch("src.matcher.chain") as mock_chain:
        mock_chain.invoke.return_value = FAKE_MATCH
        res = match_cv_to_vacancy(FAKE_VACANCY, "Some CV text")
        assert isinstance(res, MatchResult)
        assert res.match_percentage == 75
        pass
