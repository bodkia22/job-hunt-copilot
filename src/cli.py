"""Command-line interface: run the full vacancy -> match -> cover letter pipeline."""
import logging

from src.config import settings
from src.vacancy_parser import parse_vacancy, load_vacancy_text
from src.cv_store import load_cv_text
from src.matcher import match_cv_to_vacancy
from src.cover_letter import generate_cover_letter
from src.db import init_db, save_application
from src.exceptions import LLMRateLimitError, LLMConnectionError, LLMOutputError, LLMCallError

logger = logging.getLogger(__name__)


def main() -> None:
    """Run the full pipeline: parse vacancy, match CV, generate and save cover letter."""
    try:
        logger.info("=== JOB HUNT COPILOT ===")
        init_db()

        vacancy_text = load_vacancy_text(settings.vacancy_path)
        vacancy_model = parse_vacancy(vacancy_text)

        cv_text = load_cv_text(settings.cv_path)

        match_result = match_cv_to_vacancy(vacancy_model, cv_text)

        logger.info("Matched skills: %s", ", ".join(match_result.matched_skills))
        logger.info("Missing skills: %s", ", ".join(match_result.missing_skills))

        if match_result.red_flags:
            logger.warning("Red flags:")
            for flag in match_result.red_flags:
                logger.warning("  - %s", flag)

        cover_letter = generate_cover_letter(vacancy_model, match_result, cv_text)

        logger.info("=== COVER LETTER ===")
        logger.info("\n%s", cover_letter)

        with open(settings.output_cover_letter_path, "w", encoding="utf-8") as file:
            file.write(cover_letter)
        logger.info("Saved to %s", settings.output_cover_letter_path)

        save_application(
            vacancy_model.company_name,
            vacancy_model.position_title,
            match_result.match_percentage,
            match_result.is_good_fit,
            cover_letter,
        )

    except LLMRateLimitError as e:
        logger.error(e)
    except LLMConnectionError as e:
        logger.error(e)
    except LLMOutputError as e:
        logger.error(e)
    except LLMCallError as e:
        logger.error("Unexpected LLM error: %s", e)
    except FileNotFoundError as e:
        logger.error("File not found: %s", e)
    except Exception as e:
        logger.exception("Something went wrong: %s", e)


if __name__ == "__main__":
    main()