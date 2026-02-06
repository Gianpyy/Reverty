import pytest
from agents.coder_agent import CoderAgent
from helpers.enums import Status


@pytest.fixture
def SequentialMockLLM(mock_llm):
    return mock_llm

def test_validation_loop_recovery(SequentialMockLLM, grammar):
    """
    Test a full validation loop where:
    1. Initial code has syntax error (parser fails).
    2. Fixed code has linting error (variable unused).
    3. Final code is correct.
    """
    
    # Invalid Syntax
    code_syntax_error = """
: tni -> (tni : x) broken fed
    nruter x
    # Missing end of function or bad something? 
    # Actually let's make it clearly broken for parser
    invalid_token!!!!!!!!
"""
    
    # Valid Syntax but Lint Error (Unused import/var)
    code_lint_error = """
: tni -> (tni : x) lint_fail fed
    unused = 10
    nruter x
"""
    
    # Valid Code
    code_valid = """
: tni -> (tni : x) success fed
    nruter x
"""
    
    mock_client = SequentialMockLLM(responses=[code_syntax_error, code_lint_error, code_valid])
    agent = CoderAgent(client=mock_client, grammar=grammar)
    
    contract = {
        "function_name": "test_func",
        "args": [{"name": "x", "type": "int"}],
        "return_type": "int"
    }
    
    reverty_code, python_code, result = agent.build_initial_code(contract)
    
    # Verify success
    assert result.status == Status.SUCCESS, f"Failed with message: {result.message}"
    assert "success" in reverty_code
    
    # Verify the loop happened
    assert mock_client.call_count == 3
