"""Command-line interface: run the full vacancy -> match -> cover letter pipeline."""
from src.config import settings
from src.vacancy_parser import parse_vacancy, load_vacancy_text
from src.cv_store import load_cv_text
from src.matcher import match_cv_to_vacancy
from src.cover_letter import generate_cover_letter
from src.db import init_db, save_application

def main() -> None:
    init_db()
    
    vacancy_text = load_vacancy_text(settings.vacancy_path)
    vacancy_model = parse_vacancy(vacancy_text)
    
    cv_text = load_cv_text(settings.cv_path)

    match_result = match_cv_to_vacancy(vacancy_model, cv_text)

    print(f"=== MATCH RESULT: {vacancy_model.company_name} — {vacancy_model.position_title} ===")
    print(f"Score: {match_result.match_percentage}% | Good fit: {match_result.is_good_fit}")
    print(f"\nMatched skills: {', '.join(match_result.matched_skills)}")
    print(f"Missing skills: {', '.join(match_result.missing_skills)}")
    
    if match_result.red_flags:
        print(f"\nRed flags:")
        for flag in match_result.red_flags:
            print(f"  - {flag}")

    cover_letter = generate_cover_letter(vacancy_model, match_result)

    print(f"\n=== COVER LETTER ===\n")
    print(cover_letter)

    with open(settings.output_cover_letter_path, "w", encoding="utf-8") as file:
        file.write(cover_letter)
    print(f"\n(saved to {settings.output_cover_letter_path})")

    save_application(
        vacancy_model.company_name,
        vacancy_model.position_title,
        match_result.match_percentage,
        match_result.is_good_fit,
        cover_letter,
    )


if __name__ == "__main__":
    main()