from enum import Enum
from dataclasses import dataclass


class Status(Enum):
    """Status of the analysis."""

    SUCCESS = "SUCCESS"
    ERROR = "ERROR"


class ErrorType(Enum):
    """Type of error."""

    PARSING = "parsing"
    TRANSPILATION = "transpilation"
    LINTING = "linting"
    TYPE_CHECKING = "type checking"


class LLMClientType(Enum):
    """Type of LLM client."""
    
    MOCK = "mock"
    OLLAMA = "ollama"


@dataclass
class AnalysisResult:
    """Result of static analysis."""

    status: Status
    message: str
