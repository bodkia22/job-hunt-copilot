"""Generate a personalized cover letter based on vacancy requirements and match result."""
from langchain_anthropic import ChatAnthropic
from langchain_core.prompts import ChatPromptTemplate

from src.config import settings
from src.models import VacancyRequirements, MatchResult


llm = ChatAnthropic(
    model=settings.anthropic_model, # type: ignore
    api_key=settings.anthropic_api_key,
    temperature=0.7,
)

prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a job applicant writing a cover letter for a position you are "
     "genuinely interested in. Write in first person, as the candidate. Keep the tone "
     "professional but warm, not generic or robotic. Length: 3-4 short paragraphs. "
     "Focus on the candidate's matched skills and relevant experience — do not mention "
     "missing skills or weaknesses directly, but you may briefly acknowledge a learning "
     "mindset if there are notable gaps. Do not invent experience, projects, or skills "
     "that are not present in the provided context. Do not use placeholder brackets like "
     "[Company Name] — use the actual company name and position title provided."),
    ("human", "Vacancy:\n{vacancy_text}\n\n"
     "Match analysis (matched skills, gaps, and overall fit):\n{match_text}\n\n"
     "Write a cover letter for this position."),
])

chain = prompt | llm


def generate_cover_letter(vacancy: VacancyRequirements, match: MatchResult) -> str:
    vacancy_text = vacancy.model_dump_json(indent=2)

    result = chain.invoke({"vacancy_text": vacancy_text, "match_text" : match})
    return result.content # type: ignore


if __name__ == "__main__":
    from src.vacancy_parser import parse_vacancy, load_vacancy_text
    from src.cv_store import load_cv_text
    from src.matcher import match_cv_to_vacancy

    vacancy_text = load_vacancy_text(settings.vacancy_path)
    vacancy = parse_vacancy(vacancy_text)
    cv_text = load_cv_text(settings.cv_path)
    match = match_cv_to_vacancy(vacancy, cv_text)

    letter = generate_cover_letter(vacancy, match)
    print(letter)