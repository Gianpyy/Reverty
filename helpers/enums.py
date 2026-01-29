from enum import Enum


class Status(Enum):
    """Status of the analysis."""

    SUCCESS = "SUCCESS"
    ERROR = "ERROR"


class ErrorType(Enum):
    """Type of error."""

    PARSING = "parsing"
    TRANSPILATION = "transpilation"
    LINTING = "linting"


class AnalysisResult:
    """Result of static analysis."""

    status: Status
    message: str
