import json
import pytest
from agents.test_generator_agent import TestGeneratorAgent

@pytest.fixture
def SequentialMockLLM(mock_llm):
    return mock_llm

def test_test_generator_build_tests(SequentialMockLLM):
    """Test generating tests from contract."""
    
    contract = {"function_name": "add"}
    python_code = "def add(a, b): return a + b"
    
    expected_tests = "def test_add(): assert add(1, 1) == 2"
    response = json.dumps({"code": expected_tests})
    
    mock_client = SequentialMockLLM(responses=[response])
    agent = TestGeneratorAgent(client=mock_client)
    
    tests = agent.build_tests(contract, python_code)
    assert expected_tests in tests
    assert mock_client.call_count == 1

def test_test_generator_fix_tests(SequentialMockLLM):
    """Test fixing tests."""
    
    contract = {"function_name": "add"}
    python_code = "def add(a, b): return a + b"
    errors = "AssertionError"
    
    expected_tests = "def test_add_fixed(): assert add(1, 1) == 2"
    response_json = json.dumps({"code": expected_tests})
    
    mock_client = SequentialMockLLM(responses=[response_json])
    agent = TestGeneratorAgent(client=mock_client)
    
    tests = agent.fix_tests(contract, python_code, errors)
    assert expected_tests in tests
    assert mock_client.call_count == 1
