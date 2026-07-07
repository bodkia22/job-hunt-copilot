"""Utilities for safely invoking LangChain chains."""
import logging
from typing import Callable, Any

from anthropic import APIError, RateLimitError, APIConnectionError
from langchain_core.exceptions import OutputParserException
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

from src.exceptions import LLMCallError, LLMRateLimitError, LLMConnectionError, LLMOutputError

logger = logging.getLogger(__name__)


@retry(
    retry=retry_if_exception_type((RateLimitError, APIConnectionError)),
    wait=wait_exponential(multiplier=1, min=2, max=10),
    stop=stop_after_attempt(3),
    reraise=True,
)
def _invoke_with_retry(chain_invoke_fn: Callable[[], Any]) -> Any:
    """Call the chain, letting tenacity see the raw library exceptions.

    This function must NOT catch or translate any exceptions — tenacity's
    retry_if_exception_type check only works on what actually propagates out
    of the decorated function. If we caught RateLimitError here and re-raised
    it as a domain exception, tenacity would never see RateLimitError again.
    """
    return chain_invoke_fn()


def invoke_chain_safely(chain_invoke_fn: Callable[[], Any], context: str) -> Any:
    """Invoke a LangChain chain and translate low-level errors into clear exceptions.

    Args:
        chain_invoke_fn: A zero-arg callable that performs the chain.invoke() call.
        context: Human-readable description of what's being processed.

    Returns:
        The result of the chain invocation.

    Raises:
        LLMRateLimitError: If the Anthropic API rate limit is exceeded after retries.
        LLMConnectionError: If the connection to the Anthropic API fails after retries.
        LLMOutputError: If the LLM returns invalid structured output.
        LLMCallError: For any other unexpected API error.
    """
    logger.debug("Invoking LLM chain while %s", context)
    try:
        return _invoke_with_retry(chain_invoke_fn)
    except RateLimitError as e:
        logger.warning("Rate limit exceeded while %s: %s", context, e)
        raise LLMRateLimitError(f"Rate limit exceeded while {context}. Try again later.") from e
    except APIConnectionError as e:
        logger.error("Could not connect to Anthropic API while %s: %s", context, e)
        raise LLMConnectionError(f"Could not connect to Anthropic API while {context}.") from e
    except OutputParserException as e:
        logger.error("LLM returned invalid structured output while %s: %s", context, e)
        raise LLMOutputError(f"LLM returned invalid structured output while {context}: {e}") from e
    except APIError as e:
        logger.error("Unexpected API error while %s: %s", context, e)
        raise LLMCallError(f"Unexpected API error while {context}: {e}") from e