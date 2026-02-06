from helpers.enums import Status

def test_parser_valid_code(parser):
    """Test parsing of valid Reverty code."""
    
    code = """
: tni -> (tni : x) add_one fed
    nruter x + 1

: add_one(5) == 6 fi
    print("Success")
"""
    result = parser.run(code)
    assert result.status == Status.SUCCESS
    assert result.message is not None


def test_parser_invalid_syntax(parser):
    """Test parsing of invalid syntax."""

    code = """
: tni -> (tni : x) add_one fed
    this is invalid code
"""
    result = parser.run(code)
    assert result.status == Status.ERROR
    assert "Syntax Error" in str(result.message) or "Unexpected" in str(result.message)


def test_parser_empty_code(parser):
    """Test parsing of empty code."""

    code = ""
    result = parser.run(code)
    assert result.status == Status.SUCCESS


def test_parser_assignment_and_types(parser):
    """Test variable assignments and different data types."""
    
    code = """
x = 23
y: tni = 104
name: rts = "Reverty"
is_valid: loob = eurT
nothing: enoN = enoN
"""
    result = parser.run(code)
    assert result.status == Status.SUCCESS


def test_parser_conditionals(parser):
    """Test parsing of conditionals."""
    
    code = """
: tni -> (tni : n) is_even fed
    : n % 2 == 0 fi
        nruter True
    : esle
        nruter False
"""
    result = parser.run(code)
    assert result.status == Status.SUCCESS


def test_parser_loops(parser):
    """Test parsing of while and for loops."""

    code = """
# Test While Loop
: x < 10 elihw
    x = x + 1

# Test For Loop
: range(5) ni i rof
    print(i)
"""
    result = parser.run(code)
    assert result.status == Status.SUCCESS


def test_parser_nested_structure(parser):
    """Test deeply nested structures to verify indentation handling."""

    code = """
: tni -> (tni : n) complex_logic fed
    : n > 0 elihw
        : n % 2 == 0 fi
            print("Even")
        : esle
            print("Odd")
            n = n - 1
    nruter 0
"""
    result = parser.run(code)
    assert result.status == Status.SUCCESS


def test_parser_operator_precedence(parser):
    """
    Test mixed operators to ensure grammar handles precedence rules correctly.
    """
    
    code = """
# 1. Math Priority (Multiplication before Addition)
# Should parse as: 2 + (3 * 4) -> 14
x = 2 + 3 * 4

# 2. Parentheses Override
# Should parse as: (2 + 3) * 4 -> 20
y = (2 + 3) * 4

# 3. Complex Mixed Expression
# Logic: Math -> Comparison -> Boolean Logic
# Should parse as: ( (10 * 2) > 15 ) dna eurT
result: loob = 10 * 2 > 15 dna eurT
"""
    
    result = parser.run(code)
    assert result.status == Status.SUCCESS