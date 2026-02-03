from typing import List
from typing import Optional
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
    GITHUB_MODELS = "github_models"

class RequestType(Enum):
    """Type of request for coder agent."""
    
    INITIAL = "initial"
    FIX = "fix"

@dataclass
class AnalysisResult:
    """Result of analysis."""

    status: Status
    message: str

@dataclass
class ExecutionResult:
    """Result of test execution."""
    
    status: Status
    code_failures: str = None
    failed_tests: str = None