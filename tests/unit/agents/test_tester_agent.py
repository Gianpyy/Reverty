import json
import pytest
from agents.tester_agent import TesterAgent
from helpers.enums import Status, ExecutionResult
from unittest.mock import MagicMock

@pytest.fixture
def SequentialMockLLM(mock_llm):
    return mock_llm

def test_tester_agent_success(SequentialMockLLM):
    """Test valid tests execution."""
    
    mock_client = SequentialMockLLM(responses=[])
    agent = TesterAgent(client=mock_client)
    
    # Mock TestExecutor to succeed
    agent.executor = MagicMock()
    agent.executor.run_tests.return_value = ExecutionResult(
        status=Status.SUCCESS,
        code_failures=None,
        failed_tests=[]
    )
    
    result = agent.test({}, "code", "reverty", "tests")
    
    assert result["status"] == Status.SUCCESS.value
    agent.executor.run_tests.assert_called_once()
    assert mock_client.call_count == 0

def test_tester_agent_failure(SequentialMockLLM):
    """Test failure analysis when tests fail."""
    
    analysis_json = json.dumps({
        "status": Status.ERROR.value,
        "code_failures": "SyntaxError",
        "test_failures": None
    })
    
    mock_client = SequentialMockLLM(responses=[analysis_json])
    agent = TesterAgent(client=mock_client)
    
    # Mock TestExecutor to fail
    agent.executor = MagicMock()
    agent.executor.run_tests.return_value = ExecutionResult(
        status=Status.ERROR,
        code_failures="SyntaxError at line 1",
        failed_tests=[]
    )
    
    result = agent.test({}, "code", "reverty", "tests")
    
    assert result["status"] == Status.ERROR.value
    assert result["code_failures"] == "SyntaxError"
    assert mock_client.call_count == 1
