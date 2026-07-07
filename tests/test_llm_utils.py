"""Tests for LLM retry and error-translation behavior in llm_utils."""
from unittest.mock import MagicMock
import pytest

from anthropic import RateLimitError, APIConnectionError, APIError
from langchain_core.exceptions import OutputParserException

from src.llm_utils import invoke_chain_safely
from src.exceptions import (
    LLMRateLimitError,
    LLMConnectionError,
    LLMOutputError,
    LLMCallError,
)


def make_rate_limit_error() -> RateLimitError:
    """Build a minimal valid RateLimitError instance for testing."""
    mock_response = MagicMock()
    mock_response.status_code = 429
    return RateLimitError(
        message="rate limit hit",
        response=mock_response,
        body=None,
    )


def raise_rate_limit_error(*args, **kwargs):
    """Side-effect helper: raises a fresh RateLimitError on every call."""
    raise make_rate_limit_error()


def make_connection_error() -> APIConnectionError:
    """Build a minimal valid APIConnectionError instance for testing."""
    mock_request = MagicMock()
    return APIConnectionError(message="connection failed", request=mock_request)


def raise_connection_error(*args, **kwargs):
    """Side-effect helper: raises a fresh APIConnectionError on every call."""
    raise make_connection_error()


def make_api_error() -> APIError:
    """Build a minimal valid APIError instance for testing."""
    mock_request = MagicMock()
    return APIError(message="unexpected api error", request=mock_request, body=None)


def test_retries_and_eventually_succeeds():
    """Should retry after RateLimitError and eventually return the successful result."""
    mock_fn = MagicMock(
        side_effect=[
            make_rate_limit_error(),
            make_rate_limit_error(),
            "success",
        ]
    )
    result = invoke_chain_safely(mock_fn, "test context")
    assert result == "success"
    assert mock_fn.call_count == 3


def test_raises_domain_error_after_exhausting_retries():
    """After exhausting all retry attempts, should raise LLMRateLimitError, not the raw one."""
    mock_fn = MagicMock(side_effect=raise_rate_limit_error)
    with pytest.raises(LLMRateLimitError):
        invoke_chain_safely(mock_fn, "test context")
    assert mock_fn.call_count == 3


def test_connection_error_retries_and_translates():
    """APIConnectionError should also be retried, then translated to LLMConnectionError."""
    mock_fn = MagicMock(side_effect=raise_connection_error)
    with pytest.raises(LLMConnectionError):
        invoke_chain_safely(mock_fn, "test context")
    assert mock_fn.call_count == 3


def test_output_parser_exception_translated_without_retry():
    """OutputParserException should NOT be retried — it's translated immediately."""
    mock_fn = MagicMock(side_effect=OutputParserException("invalid structured output"))
    with pytest.raises(LLMOutputError):
        invoke_chain_safely(mock_fn, "test context")
    assert mock_fn.call_count == 1


def test_unexpected_api_error_translated_without_retry():
    """A generic APIError should NOT be retried — it's translated to LLMCallError immediately."""
    mock_fn = MagicMock(side_effect=make_api_error())
    with pytest.raises(LLMCallError):
        invoke_chain_safely(mock_fn, "test context")
    assert mock_fn.call_count == 1