"""Entry point for the Job Hunt Copilot CLI."""
import logging

from rich.logging import RichHandler

from src.cli import main


def configure_logging() -> None:
    """Set up root logging with a colorized Rich console handler."""
    handler = RichHandler(
        show_path=False,
        omit_repeated_times=False,
        markup=False,
        rich_tracebacks=True,
    )
    logging.basicConfig(
        level=logging.INFO,
        format="%(name)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
        handlers=[handler],
    )


configure_logging()

if __name__ == "__main__":
    main()