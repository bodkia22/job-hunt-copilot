"""Parse a vacancy text file into a structured VacancyRequirements model."""
from pathlib import Path
from typing import cast
from langchain_anthropic import ChatAnthropic
from langchain_core.prompts import ChatPromptTemplate

from src.config import settings
from src.models import VacancyRequirements
from src.prompts import VACANCY_PARSER_HUMAN, VACANCY_PARSER_SYSTEM

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
    return cast(VacancyRequirements, chain.invoke({"vacancy_text": text}))

def load_vacancy_text(path: Path) -> str:
    """Read and return the vacancy file contents as a string."""
    with open(path, "r", encoding="utf-8") as file:
        return file.read()

if __name__ == "__main__":
    vacancy_text = load_vacancy_text(settings.vacancy_path)
    result = parse_vacancy(vacancy_text)
    print(result.model_dump_json(indent=2))