import pytest
from tools.test_executor import TestExecutor
from helpers.enums import Status

@pytest.fixture
def test_executor():
    return TestExecutor()

def test_executor_passing_tests(test_executor):
    """Test executing passing tests."""

    py_code = """
def add(a, b):
    return a + b
"""
    test_code = """
from implementation import add
def test_add():
    assert add(1, 2) == 3
"""

    result = test_executor.run_tests(py_code, test_code)
    assert result.status == Status.SUCCESS
    assert result.failed_tests == []

def test_executor_failing_tests(test_executor):
    """Test executing failing tests."""

    py_code = """
def add(a, b):
    return a + b
"""
    test_code = """
from implementation import add
def test_add_fail():
    assert add(1, 2) == 4
"""

    result = test_executor.run_tests(py_code, test_code)
    assert result.status == Status.ERROR
    assert "test_add_fail" in result.failed_tests

def test_executor_syntax_error_in_tests(test_executor):
    """Test syntax error in test code."""
    
    py_code = "pass"
    test_code = "def test_fail(): syntax error"
    
    result = test_executor.run_tests(py_code, test_code)
    assert result.status == Status.ERROR
    assert "SyntaxError" in result.code_failures or "SyntaxError" in result.failed_tests or result.code_failures
