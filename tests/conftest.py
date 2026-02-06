import pytest
import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))) # Add project root to path
from unittest.mock import MagicMock
from tools.parser import Parser
from helpers.utils import load_grammar

# Mock toon_format before importing modules that use it
mock_toon = MagicMock()
mock_toon.DecodeOptions = MagicMock
mock_toon.encode = MagicMock(return_value="encoded")
mock_toon.decode = MagicMock(return_value={})
sys.modules["toon_format"] = mock_toon

# Mock streamlit before importing modules that use it
mock_st = MagicMock()
sys.modules["streamlit"] = mock_st

@pytest.fixture
def grammar():
    """Loads the grammar."""
    return load_grammar()

@pytest.fixture
def parser(grammar):
    """Returns a Parser instance."""
    return Parser(grammar)
