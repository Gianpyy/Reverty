import pytest
import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))) # Add project root to path
from tools.parser import Parser
from helpers.utils import load_grammar
from clients.llm_client_abstract import LLMClient
from typing import List

@pytest.fixture
def grammar():
    """Loads the grammar."""
    return load_grammar()

@pytest.fixture
def parser(grammar):
    """Returns a Parser instance."""
    return Parser(grammar)

@pytest.fixture
def mock_llm():
    class SequentialMockLLM(LLMClient):
        """
        MockLLM that returns a sequence of predefined responses.
        """

        def __init__(self, responses: List[str]):
            self.responses = responses
            self.call_count = 0

        def generate(self, user_prompt: str, system_prompt: str = None, model: str = "mock") -> str:
            # Get the current response and advance the index
            if self.call_count < len(self.responses):
                response = self.responses[self.call_count]
                self.call_count += 1
                return response
            
            # If the responses run out, return the last one (or an empty one)
            return self.responses[-1]
    
    return SequentialMockLLM