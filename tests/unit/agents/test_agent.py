import pytest
from agents.agent import Agent
from unittest.mock import MagicMock

# Fixture leggera per istanziare l'agente senza dipendenze vere
@pytest.fixture
def agent():
    mock_client = MagicMock()
    return Agent(client=mock_client)

@pytest.mark.parametrize("input_str, expected_key, expected_value", [
    # JSON
    ('{"complexity": 5}', "complexity", 5),
    
    # Markdown JSON
    (' Ecco il codice:\n```json\n{"complexity": 3}\n```', "complexity", 3),
    
    # Custom formats (TOON)
    ('```toon\ncomplexity: 2\n```', "complexity", 2),
    
    # "Dirty" (Text before and after)
    ('Certo! Ecco la risposta: {"complexity": 1} Spero aiuti.', "complexity", 1),
    
    # Reverty
    ('```reverty\ncode_here\n```', "code", "code_here"),
    
    # Python
    ('```python\ndef test(): pass\n```', "code", "def test(): pass"),
])
def test_extract_response(agent, input_str, expected_key, expected_value):
    """Testa che tutte le strategie di estrazione funzionino correttamente."""
    result = agent.extract_response(input_str)
    
    assert isinstance(result, dict)
    assert result.get(expected_key) == expected_value
    