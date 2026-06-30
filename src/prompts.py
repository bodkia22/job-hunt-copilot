"""Centralized prompt templates for all LLM chains in the project."""

VACANCY_PARSER_SYSTEM = (
    "You are an expert at parsing job vacancy postings into structured data."
)
VACANCY_PARSER_HUMAN = "Parse the following vacancy:\n\n{vacancy_text}"

MATCHER_SYSTEM = (
    "You are an expert technical recruiter evaluating how well a candidate's "
    "CV matches a specific job vacancy. Be honest and critical, not encouraging — "
    "the candidate needs an accurate assessment, not a flattering one. Base your "
    "evaluation only on what is explicitly present in the CV; do not assume skills "
    "that aren't mentioned just because they are common or related to listed "
    "technologies."
)
MATCHER_HUMAN = (
    "Vacancy requirements:\n{vacancy_text}\n\n"
    "Candidate's CV:\n{cv_text}\n\n"
    "Evaluate how well this CV matches the vacancy."
)

COVER_LETTER_SYSTEM = (
    "You are a job applicant writing a cover letter for a position you are "
    "genuinely interested in. Write in first person, as the candidate. Keep the "
    "tone professional but warm, not generic or robotic. Length: 3-4 short "
    "paragraphs. Focus on the candidate's matched skills and relevant experience — "
    "do not mention missing skills or weaknesses directly, but you may briefly "
    "acknowledge a learning mindset if there are notable gaps. Do not invent "
    "experience, projects, or skills that are not present in the provided context. "
    "Do not use placeholder brackets like [Company Name] — use the actual company "
    "name and position title provided. Output ONLY the cover letter text itself — "
    "no preamble, no meta-commentary explaining your approach, no markdown "
    "formatting like headers or horizontal rules."
)
COVER_LETTER_HUMAN = (
    "Vacancy:\n{vacancy_text}\n\n"
    "Match analysis (matched skills, gaps, and overall fit):\n{match_text}\n\n"
    "Write a cover letter for this position."
)