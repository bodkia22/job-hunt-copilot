"""Match a parsed vacancy against the candidate's CV using a single LLM call."""
from typing import cast

from langchain_anthropic import ChatAnthropic
from langchain_core.prompts import ChatPromptTemplate

from src.config import settings
from src.cv_store import load_cv_text
from src.models import VacancyRequirements, MatchResult
from src.prompts import MATCHER_HUMAN, MATCHER_SYSTEM

llm = ChatAnthropic(
    model=settings.anthropic_model, # type: ignore
    api_key=settings.anthropic_api_key,
    temperature=0,
)
structured_llm = llm.with_structured_output(MatchResult)

prompt = ChatPromptTemplate.from_messages([
    ("system", MATCHER_SYSTEM),
    ("human", MATCHER_HUMAN),
])

chain = prompt | structured_llm


def match_cv_to_vacancy(vacancy: VacancyRequirements, cv_text: str) -> MatchResult:
    """Evaluate how well the candidate's CV matches the given vacancy requirements.

    Args:
        vacancy: Structured vacancy requirements extracted from the job posting.
        cv_text: Full text of the candidate's CV.

    Returns:
        A MatchResult with fit score, matched/missing skills, and red flags.
    """
    vacancy_text = vacancy.model_dump_json(indent=2)
    result = chain.invoke({"vacancy_text": vacancy_text, "cv_text": cv_text})

    return cast(MatchResult, result) 


if __name__ == "__main__":
    from src.vacancy_parser import parse_vacancy, load_vacancy_text

    vacancy_text = load_vacancy_text(settings.vacancy_path)
    vacancy = parse_vacancy(vacancy_text)
    cv_text = load_cv_text(settings.cv_path)

    result = match_cv_to_vacancy(vacancy, cv_text)
    print(result.model_dump_json(indent=2))