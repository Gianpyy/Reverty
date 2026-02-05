from clients.llm_client_abstract import LLMClient
import json


class MockLLMClient(LLMClient):
    def generate(
        self, user_prompt: str, system_prompt: str = None, model: str = "mock"
    ) -> str:
        """
        Generate a hardcoded response.
        """

        user_prompt_lower = user_prompt.lower()
        system_prompt_lower = system_prompt.lower()

        # Hardcoded response for test agent
        if "evaluation" in system_prompt_lower:
            response = json.dumps(
                {
                    "complexity": 5,
                },
                indent=4,
            )
            
            print("[MockLLMClient - Evaluation] ", response)
            return response
        
        # Hardcoded response for architect agent
        if "architect" in system_prompt_lower:
            response = json.dumps(
                {
                    "function_name": "factorial",
                    "args": [{"name": "n", "type": "int"}],
                    "return_type": "int",
                    "docstring": "Calculates factorial of n.",
                    "constraints": ["n >= 0"],
                    "edge_cases": [],
                },
                indent=4,
            )
            print("[MockLLMClient - Architect] ", response)
            return response

        # Hardcoded response for type checking (takes priority over fix, for testing purposes)
        if "type checking" in user_prompt_lower:
            response = json.dumps(
                {
                    "code": """: tni -> (tni: n) factorial fed
                        res : tni = 1
                        : n > 1 elihw
                            res = res * n
                            n = n - 1
                        nruter res
                    """,
                },
                indent=4,
            )
            print("[MockLLMClient - Type Checking] ", response)
            return response

        # Hardcoded response for fix (takes priority over coder)
        if "fix" in user_prompt_lower:
            response = json.dumps(
                {
                    "code": """: tni -> (tni: n) factorial fed
                        res : rts = 1
                        : n>1elihw
                            res=res * n
                            n=n-1
                        nruter res
                    """,
                },
                indent=4,
            )
            print("[MockLLMClient - Fix] ", response)
            return response

        # Hardcoded response for coder agent
        if "esoteric" in system_prompt_lower:
            response = json.dumps(
                {
                    "code": """: tni -> (tni: n) factorial def
                        res = 1
                        : n> 1 elihw
                            res = res * n
                            n = n - 1
                        nruter res
                    """,
                },
                indent=4,
            )
            print("[MockLLMClient - Coder] ", response)
            return response

        # Hardcoded response for tester generator agent
        if "test" in user_prompt_lower or "pytest" in user_prompt_lower:
            return """import pytest
from implementation import factorial


def test_factorial_positive():
    assert factorial(5) == 120
    assert factorial(3) == 6
    assert factorial(1) == 1


def test_factorial_zero():
    assert factorial(0) == 1

            """

        # Hardcoded response for test agent
        if "failures" in system_prompt_lower:
            return """
            "analysis": "Brief explanation of what went wrong",
            "code_failures": "List of code failures (or null if code were not wrong)",
            "test_failures": "List of test failures (or null if test were not wrong)"
            """
        