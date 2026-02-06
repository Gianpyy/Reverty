import pytest
from tools.transpiler import Transpiler
from helpers.enums import Status

@pytest.fixture
def transpiler():
    return Transpiler()

def test_transpiler_function(parser, transpiler):
    """Test transpilation of a simple function."""

    code = """
: tni -> (tni : x) add_one fed
    nruter -1
"""
    result_parse = parser.run(code)
    assert result_parse.status == Status.SUCCESS
    
    result_transpile = transpiler.run(result_parse.message)
    assert result_transpile.status == Status.SUCCESS
    expected = "def add_one(x: int) -> int:\n    return -1"
    assert expected in result_transpile.message

def test_transpiler_conditionals(parser, transpiler):
    """Test transpilation of conditionals."""

    code = """
: tni -> (tni : x) check fed
    : x > 0 fi
        nruter 1
    : x < 0 file
        nruter -1
    : esle
        nruter 0
"""
    result_parse = parser.run(code)
    assert result_parse.status == Status.SUCCESS
    
    result_transpile = transpiler.run(result_parse.message)
    assert result_transpile.status == Status.SUCCESS
    assert "if x > 0:" in result_transpile.message
    assert "elif x < 0:" in result_transpile.message
    assert "else:" in result_transpile.message

def test_transpiler_loops(parser, transpiler):
    """Test transpilation of loops."""
    
    code = """
: tni -> () loops fed
    : x < 10 elihw
        x = x + 1
    
    : range(5) ni i rof
        print(i)
"""
    result_parse = parser.run(code)
    assert result_parse.status == Status.SUCCESS
    
    result_transpile = transpiler.run(result_parse.message)
    assert result_transpile.status == Status.SUCCESS
    assert "while x < 10:" in result_transpile.message
    assert "for i in range(5):" in result_transpile.message
