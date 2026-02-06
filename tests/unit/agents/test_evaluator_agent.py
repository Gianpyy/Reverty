import pytest
from agents.evaluator_agent import EvaluatorAgent

@pytest.fixture
def SequentialMockLLM(mock_llm):
    return mock_llm

def test_evaluator_success(SequentialMockLLM):
    """Test evaluator success case."""
    
    # Prepare the response
    response = """```toon
    complexity: 3
    detected_logic: Simple logic
    reasoning: Simple reasoning
    ```"""
    
    # Create the agent with our Sequential Mock
    mock_client = SequentialMockLLM(responses=[response])
    agent = EvaluatorAgent(client=mock_client)

    # Execute
    result = agent.evaluate_request("s1mple task")
    assert result["complexity"] == 3
    assert mock_client.call_count == 1

def test_evaluator_retry(SequentialMockLLM):
    """Test evaluator retry logic."""
    
    # Wrong response
    bad_response = """```toon
    complexity: high
    ```"""
    # Correct response
    good_response = """```toon
    complexity: 5
    ```"""
    
    # Load the sequence
    mock_client = SequentialMockLLM(responses=[bad_response, good_response])
    agent = EvaluatorAgent(client=mock_client)

    # Execute
    result = agent.evaluate_request("medium task")
    assert result["complexity"] == 5
    assert mock_client.call_count == 2

def test_evaluator_max_retries_exceeded(SequentialMockLLM):
    """Test evaluator max retries exceeded case."""
    
    # Wrong response
    bad_response = """```toon
    complexity: unknown
    ```"""
    
    # Put enough wrong responses to exceed the retries
    mock_client = SequentialMockLLM(responses=[bad_response, bad_response, bad_response, bad_response])
    agent = EvaluatorAgent(client=mock_client)

    # Execute with max_retries=2 to make it faster
    result = agent.evaluate_request("task difficile", max_retries=2)
    assert result["complexity"] == 5
    assert mock_client.call_count >= 3 

def test_evaluator_broken_response(SequentialMockLLM):
    """Test evaluator broken response case."""
    
    garbage = "Garbage request"
    mock_client = SequentialMockLLM(responses=[garbage, garbage, garbage])
    agent = EvaluatorAgent(client=mock_client)

    result = agent.evaluate_request("test")
    assert result == {"complexity": 5}
