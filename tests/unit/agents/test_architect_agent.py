import pytest
from agents.architect_agent import ArchitectAgent

@pytest.fixture
def SequentialMockLLM(mock_llm):
    return mock_llm

def test_architect_simple_contract(SequentialMockLLM):
    """Test creation of contract for simple complexity."""
    
    response = """```toon
    function_name: add
    args[2]{name, type}: 
        a, int
        b, int
    return_type: int
    complexity: 3
    requirements[2]:
        very simple function
        not really that hard
    ```"""
    
    mock_client = SequentialMockLLM(responses=[response])
    agent = ArchitectAgent(client=mock_client)
    
    result = agent.create_contract("Sum two numbers", complexity=3)
    
    assert result["function_name"] == "add"
    assert mock_client.call_count == 1


def test_architect_complex_contract(SequentialMockLLM):
    """Test creation of contract for complex complexity."""
    
    response = """```toon
    function_name: process_data
    args[2]{name, type}: 
        a, int
        b, int
    return_type: int
    complexity: 8
    requirements[5]:
        the parameters are two integers
        but the function is very complex
        REAAAAAAALLY complex
        hi professor costagliola!
        life is 42
    constraints[1]:
        the function must be very complex
    edge_cases[1]:
        the function must be very complex
    ```"""
    
    mock_client = SequentialMockLLM(responses=[response])
    agent = ArchitectAgent(client=mock_client)
    
    result = agent.create_contract("Do heavy lifting", complexity=8)
    assert result["function_name"] == "process_data"

def test_architect_retry_on_bad_response(SequentialMockLLM):
    """Test handling of invalid response."""
    
    bad_response = "Fail fast!" # TODO: corretto far failare fast il contratto oppure rigeneriamo?
    valid_response = """```toon
    function_name: retry_success
    ```"""
    
    mock_client = SequentialMockLLM(responses=[bad_response, valid_response])
    agent = ArchitectAgent(client=mock_client)

    result = agent.create_contract("Bad prompt", complexity=1)
    assert result == {"code": "Fail fast!"}
