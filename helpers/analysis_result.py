from enum import Enum


class Status(Enum):
    SUCCESS = "SUCCESS"
    ERROR = "ERROR"


class AnalysisResult:
    """Result of static analysis."""

    status: Status
    message: str
