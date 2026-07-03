"""Parse a vacancy text file into a structured VacancyRequirements model."""
import logging
from pathlib import Path
from typing import cast
from langchain_anthropic import ChatAnthropic
from langchain_core.prompts import ChatPromptTemplate

from src.config import settings
from src.models import VacancyRequirements
from src.prompts import VACANCY_PARSER_HUMAN, VACANCY_PARSER_SYSTEM
from src.llm_utils import invoke_chain_safely

logger = logging.getLogger(__name__)

llm = ChatAnthropic(
    model=settings.anthropic_model, # type: ignore
    api_key=settings.anthropic_api_key,
    temperature=0,
)

structured_llm = llm.with_structured_output(VacancyRequirements)

prompt = ChatPromptTemplate.from_messages([
    ("system", VACANCY_PARSER_SYSTEM),
    ("human", VACANCY_PARSER_HUMAN),
])

chain = prompt | structured_llm

def parse_vacancy(text: str) -> VacancyRequirements:
    """Send vacancy text to the LLM and return structured requirements."""
    logger.info("Parsing vacancy text (%d chars)", len(text))
    result = invoke_chain_safely(
        lambda: chain.invoke({"vacancy_text": text}),
        context="parsing vacancy",
    )

    vacancy = cast(VacancyRequirements, result)
    logger.info("Parsed vacancy: %s — %s", vacancy.company_name, vacancy.position_title)
    return vacancy

def load_vacancy_text(path: Path) -> str:
    """Read and return the vacancy file contents as a string."""
    logger.debug("Loading vacancy text from %s", path)
    with open(path, "r", encoding="utf-8") as file:
        return file.read()

if __name__ == "__main__":
    vacancy_text = load_vacancy_text(settings.vacancy_path)
    result = parse_vacancy(vacancy_text)
    print(result.model_dump_json(indent=2))