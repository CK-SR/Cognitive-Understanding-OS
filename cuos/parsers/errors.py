class ParserError(Exception):
    """Base parser error."""


class ParserDependencyError(ParserError):
    """Raised when parser runtime dependency is unavailable."""


class ParserExecutionError(ParserError):
    """Raised when parser execution fails."""


class ParserOutputError(ParserError):
    """Raised when parser output cannot be normalized."""
