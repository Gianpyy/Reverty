import pytest
from tools.linter import Linter
from helpers.enums import Status
import subprocess

@pytest.fixture
def linter():
    return Linter()

def test_linter_valid_code(linter):
    """Test linting of valid Python code."""

    code = """
def add(a, b):
    return a + b
"""
    result = linter.run(code)
    assert result.status == Status.SUCCESS

def test_linter_invalid_code(linter):
    """Test linting of code with style/syntax errors."""
    
    code = """
import os

def foo():
    x = y + 1 
"""
    result = linter.run(code)
    assert result.status == Status.ERROR
    assert "Line " in str(result.message) # Linter replaces filename with "Line "

def test_linter_missing_flake8(linter, monkeypatch):
    """Test handling if flake8 is missing."""
    
    # Mock subprocess.run to raise an error or return stderr "No module named flake8"
    def mock_run(*args, **kwargs):
        class MockResult:
            returncode = 1
            stderr = "No module named flake8"
            stdout = ""
        return MockResult()

    monkeypatch.setattr(subprocess, "run", mock_run)
    result = linter.run("pass")
    assert result.status == Status.ERROR
    assert "Flake8 not installed" in result.message
