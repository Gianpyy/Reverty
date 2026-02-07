import pytest
from agents.coder_agent import CoderAgent
from helpers.enums import Status

@pytest.fixture
def SequentialMockLLM(mock_llm):
    return mock_llm

def test_coder_initial_code_success(SequentialMockLLM, grammar):
    """Test initial code generation that works on first try."""
    
    contract = {
        "function_name": "add",
        "args": [{"name": "a", "type": "int"}, {"name": "b", "type": "int"}],
        "return_type": "int"
    }
    
    reverty_code = """
: tni -> (tni : a, tni : b) add fed
    nruter a + b
"""
    
    # Mock LLM
    mock_client = SequentialMockLLM(responses=[reverty_code])
    agent = CoderAgent(client=mock_client, grammar=grammar)
    
    code, py_code, result = agent.build_initial_code(contract)
    assert result.status == Status.SUCCESS
    assert "def add(a: int, b: int) -> int:" in py_code
    assert mock_client.call_count == 1

def test_coder_initial_code_fail(SequentialMockLLM, grammar):
    """Test initial code generation that fails."""
    
    contract = {"function_name": "foo"}
    
    # Invalid Reverty code
    invalid_code = ": tni -> () foo fed\n broken syntax"
    
    # Mock LLM
    mock_client = SequentialMockLLM(responses=[invalid_code, invalid_code, invalid_code])
    agent = CoderAgent(client=mock_client, grammar=grammar)
    
    code, py_code, result = agent.build_initial_code(contract)
    assert result.status == Status.ERROR
    assert mock_client.call_count == 3

def test_coder_validation_loop(SequentialMockLLM, grammar):
    """Test code generation with a syntax error fixed in validation loop."""
    
    contract = {"function_name": "foo"}
    
    # Invalid Reverty code (syntax error)
    invalid_code = ": tni -> () foo fed\n broken syntax"
    
    # Valid Reverty code
    valid_code = ": tni -> () foo fed\n nruter 0"
    
    # Mock LLM
    mock_client = SequentialMockLLM(responses=[invalid_code, valid_code])
    agent = CoderAgent(client=mock_client, grammar=grammar)
        
    code, py_code, result = agent.build_initial_code(contract)
    assert result.status == Status.SUCCESS
    assert "nruter 0" in code
    assert mock_client.call_count == 2

def test_coder_fix_code_success(SequentialMockLLM, grammar):
    """Test fix code generation that works on first try."""
    
    contract = {"function_name": "foo"}

    errors = "Syntax error"
    
    # Invalid Reverty code (syntax error)
    invalid_code = ": tni -> () foo fed\n broken syntax"
    
    # Valid Reverty code
    valid_code = ": tni -> () foo fed\n nruter 0"
    
    # Mock LLM
    mock_client = SequentialMockLLM(responses=[valid_code])
    agent = CoderAgent(client=mock_client, grammar=grammar)
        
    code, py_code, result = agent.fix_code(contract, invalid_code, "", errors)
    assert result.status == Status.SUCCESS
    assert "nruter 0" in code

def text_coder_fix_code_fail(SequentialMockLLM, grammar):
    """Test fix code generation that fails."""
    
    contract = {"function_name": "foo"}

    errors = "Syntax error"
    
    # Invalid Reverty code (syntax error)
    invalid_code = ": tni -> () foo fed\n broken syntax"
    
    # Mock LLM
    mock_client = SequentialMockLLM(responses=[invalid_code, invalid_code, invalid_code])
    agent = CoderAgent(client=mock_client, grammar=grammar)
        
    code, py_code, result = agent.fix_code(contract, invalid_code, "", errors)
    assert result.status == Status.ERROR
    assert mock_client.call_count == 3