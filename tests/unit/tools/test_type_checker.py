import pytest
from tools.type_checker import TypeChecker
from helpers.enums import Status
import subprocess

@pytest.fixture
def type_checker():
    return TypeChecker()

def test_type_checker_valid(type_checker):
    """Test type checking on valid typed code."""

    code = """
def add(a: int, b: int) -> int:
    return a + b
"""
    result = type_checker.run(code)
    assert result.status == Status.SUCCESS

def test_type_checker_invalid(type_checker):
    """Test type checking on code with type errors."""

    code = """
def add(a: int, b: int) -> int:
    return "string"
"""
    result = type_checker.run(code)
    assert result.status == Status.ERROR
    assert "Line " in str(result.message)

def test_type_checker_missing_mypy(type_checker, monkeypatch):
    """Test handling if mypy is missing."""

    def mock_run(*args, **kwargs):
        class MockResult:
            returncode = 1
            stderr = "No module named mypy"
            stdout = ""
        return MockResult()
    
    monkeypatch.setattr(subprocess, "run", mock_run)
    result = type_checker.run("pass")
    assert result.status == Status.ERROR
    assert "MyPy not installed" in str(result.message)
