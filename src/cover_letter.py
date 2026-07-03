"""Generate a personalized cover letter based on vacancy requirements and match result."""
import logging

from langchain_anthropic import ChatAnthropic
from langchain_core.prompts import ChatPromptTemplate

from src.config import settings
from src.models import VacancyRequirements, MatchResult
from src.prompts import COVER_LETTER_HUMAN, COVER_LETTER_SYSTEM
from src.llm_utils import invoke_chain_safely

logger = logging.getLogger(__name__)

llm = ChatAnthropic(
    model=settings.anthropic_model, # type: ignore
    api_key=settings.anthropic_api_key,
    temperature=0.7,
)

prompt = ChatPromptTemplate.from_messages([
    ("system", COVER_LETTER_SYSTEM),
    ("human", COVER_LETTER_HUMAN),
])

chain = prompt | llm


def generate_cover_letter(vacancy: VacancyRequirements, match_result: MatchResult) -> str:
    """Generate a personalized cover letter based on the vacancy and match analysis.

    Args:
        vacancy: Structured vacancy requirements extracted from the job posting.
        match_result: Result of matching the CV against the vacancy.

    Returns:
        The cover letter as a plain string.

    Raises:
        ValueError: If the LLM response content is not a plain string.
    """
    logger.info("Generating cover letter for %s — %s", vacancy.company_name, vacancy.position_title)
    vacancy_text = vacancy.model_dump_json(indent=2)

    result = invoke_chain_safely(
        lambda: chain.invoke({"vacancy_text": vacancy_text, "match_text" : match_result.model_dump_json(indent=2)}),
        context="generating cover letter",
    )
    content = result.content
    if not isinstance(content, str):
        logger.error("Expected str response from cover letter chain, got %s", type(content))
        raise ValueError(f"Expected str response, got {type(content)}")
    logger.info("Generated cover letter (%d chars)", len(content))
    return content


if __name__ == "__main__":
    from src.vacancy_parser import parse_vacancy, load_vacancy_text
    from src.cv_store import load_cv_text
    from src.matcher import match_cv_to_vacancy

    vacancy_text = load_vacancy_text(settings.vacancy_path)
    vacancy = parse_vacancy(vacancy_text)
    cv_text = load_cv_text(settings.cv_path)
    match_result = match_cv_to_vacancy(vacancy, cv_text)

    letter = generate_cover_letter(vacancy, match_result)
    print(letter)