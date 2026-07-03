"""Custom exceptions for LLM chain invocation failures."""


class LLMCallError(Exception):
    """Base exception for all LLM invocation failures."""


class LLMRateLimitError(LLMCallError):
    """Raised when the Anthropic API rate limit is exceeded."""


class LLMConnectionError(LLMCallError):
    """Raised when the connection to the Anthropic API fails."""


class LLMOutputError(LLMCallError):
    """Raised when the LLM returns output that fails structured parsing."""