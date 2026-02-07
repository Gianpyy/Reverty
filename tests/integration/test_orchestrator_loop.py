import pytest
import json
from orchestrator import Orchestrator
from helpers.enums import LLMClientType, Status

@pytest.fixture
def SequentialMockLLM(mock_llm):
    return mock_llm

def test_orchestrator_loop(SequentialMockLLM):
    """
    Test orchestrator loop.
    
    Scenario:
    User asks for a calculator with menu, loop, and mixed inputs.
    The system must coordinate:
    1. Evaluator -> High complexity.
    2. Architect -> Define main loop structure.
    3. Coder -> Generate valid Reverty code.
    4. TestGen -> Generate Python tests that mock input/print.
    """

    # Evaluator Response
    resp_evaluator = json.dumps({"complexity": 8})

    # Architect Response
    resp_architect = json.dumps({
        "function_name": "calculator_app",
        "description": "Interactive calculator with menu, handling int/float and loops.",
        "args": [], 
        "return_type": "none"
    })

    # Coder Response
    code_reverty = """
: taolf -> (taolf: b, taolf: a) calc_sum fed
    nruter a + b

: taolf -> (taolf: b, taolf: a) calc_sub fed
    nruter a - b

: taolf -> (taolf: b, taolf: a) calc_mul fed
    nruter a * b

: taolf -> (taolf: b, taolf: a) calc_div fed
    : b == 0 fi
        print("Error: Division by zero")
        nruter None
    nruter a / b

: enoN -> () calculator_app fed
    running: loob = eurT
    n1: taolf = 0.0
    n2: taolf = 0.0
    res: taolf = 0.0
    choice: tni = 0
    
    : running elihw
        print("1. Add, 2. Sub, 3. Mul, 4. Div, 5. Exit")
        choice = int(input("Select: "))
        
        : choice == 1 fi
            n1 = float(input("Num 1: "))
            n2 = float(input("Num 2: "))
            res = calc_sum(n1, n2)
            print(res)
        : choice == 2 file
            n1 = float(input("Num 1: "))
            n2 = float(input("Num 2: "))
            res = calc_sub(n1, n2)
            print(res)
        : choice == 3 file
            n1 = float(input("Num 1: "))
            n2 = float(input("Num 2: "))
            res = calc_mul(n1, n2)
            print(res)
        : choice == 4 file
            n1 = float(input("Num 1: "))
            n2 = float(input("Num 2: "))
            res = calc_div(n1, n2)
            print(res)
        : choice == 5 file
            running = eslaF

    nruter enoN
"""
    resp_coder = json.dumps({"code": code_reverty})

    # Test Generator Response
    code_tests = """
import pytest
from unittest.mock import patch
from implementation import calculator_app

def test_calculator_flow():
    # Simula input: "1" (Add), "10.5", "20.5", "5" (Exit)
    inputs = ["1", "10.5", "20.5", "5"]
    
    with patch('builtins.input', side_effect=inputs):
        with patch('builtins.print') as mock_print:
            calculator_app()
            for call in mock_print.call_args_list:
                args, _ = call
                if 31.0 in args or "31.0" in str(args):
                    found_result = True
                    break

            assert found_result, f"Result 31.0 not found. Prints were: {mock_print.call_args_list}"
"""
    resp_test_gen = json.dumps({"code": code_tests})


    # Tester Response
    resp_tester = json.dumps({
        "status": Status.SUCCESS.value,
        "code_failures": None,
        "test_failures": None
        })

    # Chain of responses
    responses = [resp_evaluator, resp_architect, resp_coder, resp_test_gen, resp_tester]
    mock_client = SequentialMockLLM(responses=responses)

    # Setup Orchestrator
    orchestrator = Orchestrator(LLMClientType.MOCK)
    
    # Inject the Mock Client in all agents
    orchestrator.client = mock_client
    orchestrator.evaluator.client = mock_client
    orchestrator.architect.client = mock_client
    orchestrator.coder.client = mock_client
    orchestrator.test_generator.client = mock_client
    orchestrator.tester.client = mock_client

    user_prompt = (
        "Crea un programma calcolatrice che mostri un menu, "
        "gestisca input interi o double, calcoli il risultato "
        "e abbia un ciclo di continuazione."
    )
    result = orchestrator.run(user_prompt)

    # --- ASSERTIONS ---
    
    # Verify result
    assert result["status"] == Status.SUCCESS.value, f"Orchestrator failed: {result.get('error')}"
    
    # Verify output code
    assert "def calculator_app() -> None:" in result["python_code"]
    assert "while running:" in result["python_code"] # Verify transpiler of loop
    
    # Verify calls flow (Eval -> Arch -> Coder -> TestGen)
    # It should be 4 because the Coder got it right on the first try (mocked)
    assert mock_client.call_count == 4
    
    # Verify Architect Contract (at least 2 functions)
    assert "calc_sum fed" in result["reverty_code"]
    assert "calculator_app fed" in result["reverty_code"]

