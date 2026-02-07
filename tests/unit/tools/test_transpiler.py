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


def test_transpiler_unary(parser, transpiler):
    """Test transpilation of unary operators."""
    
    code = """
: enoN -> () test_unary_ops fed
    # 1. Negative number
    a: tni = -5
    print(a)

    # 2. Negative variable
    b: tni = -a
    print(b)

    # 3. Negative expression between parentheses
    c: tni = -(10 + 5)
    print(c)

    # 4. Multiplication with negative operand (precedence)
    d: tni = 10 * -2
    print(d)
    
    nruter enoN
"""
    result_parse = parser.run(code)
    assert result_parse.status == Status.SUCCESS
    
    result_transpile = transpiler.run(result_parse.message)
    assert result_transpile.status == Status.SUCCESS
    assert "a: int = -5" in result_transpile.message
    assert "b: int = -a" in result_transpile.message
    assert "c: int = -(10 + 5)" in result_transpile.message
    assert "d: int = 10 * -2" in result_transpile.message

def test_complex_features(parser, transpiler):
    """
    Tests:
    1. range() with complex expressions (range(n), range(n+1)).
    2. Distinction between func_call() and NAME.
    """
    
    code = """
: enoN -> (tni: val) my_doubler fed
    nruter val * 2

: enoN -> () main fed
    # SETUP
    limit: tni = 3
    
    # TEST 1: Range with variable (limit)
    : range(limit) ni i rof
        print(i)
        
    # TEST 2: Range with expression (limit + 2)
    : range(limit + 2) ni j rof
        print(j)

    # TEST 3: NAME vs Func Call disambiguation
    res: tni = my_doubler(10)
    
    # Here we use the variable 'res' (name)
    print(res)
    
    nruter enoN
"""
    result_parse = parser.run(code)
    assert result_parse.status == Status.SUCCESS
    
    result_transpile = transpiler.run(result_parse.message)
    assert result_transpile.status == Status.SUCCESS
    
    py_code = result_transpile.message
    assert "range(limit)" in py_code
    assert "range(limit + 2)" in py_code
    assert "my_doubler(10)" in py_code
    assert "print(res)" in py_code