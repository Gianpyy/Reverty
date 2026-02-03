
from typing import List
import json
from typing import Dict, Any

"""
Helper functions for generating user requests from user prompts.
"""


def generate_architect_request(user_prompt: str) -> str:
    """
    Generates a request for the architect agent.
    """
    
    return f"""User request: {user_prompt}
    Design a technical specification (contract) for this function. 
    IMPORTANT: Focus ONLY on the 'User Request' above.

    You MUST respond with ONLY a valid JSON object, nothing else.

    Required JSON format:
    {{
        "function_name": "name_of_function",
        "args": [
            {{"name": "param1", "type": "str"}},
            {{"name": "param2", "type": "int"}}
        ],
        "return_type": "return_type",
        "docstring": "Brief description of what the function does",
        "requirements_list": [
            "Requirement 1 (from user prompt)",
            "Requirement 2 (from user prompt)"
        ],
        "constraints": [
            "constraint 1",
            "constraint 2"
        ],
        "edge_cases": [
            "edge case 1",
            "edge case 2"
        ]
    }}

    IMPORTANT: Return ONLY the JSON object above, with no additional text, no markdown, no explanations."""


def generate_static_fix_request(reverty_code: str, errors: str, error_type: str) -> str:
    """
    Generates a request for the fix agent.
    """

    fix_parsing_prompt = f"""Your code has {error_type} errors:

                        Code:
                        {reverty_code}

                        Errors:
                        {errors}

                        Fix these {error_type} errors and return only the corrected code.
                    """

    return fix_parsing_prompt


def generate_test_fix_request(contract: Dict[str, Any], reverty_code: str, python_code: str, errors: str) -> str:
    """
    Generates a request for the fix agent.
    """

    fix_parsing_prompt = f"""Contract (The Specification):
                        {json.dumps(contract, indent=2)}

                        Reverty Code:
                        {reverty_code}

                        Equivalent Python Code:
                        {python_code}

                        Test Execution Output (Failures):
                        {errors}

                        Analyze the failures. The contract is the single source of truth.
                        Either the code violates the contract, or the tests make incorrect assumptions.

                        Return JSON:
                        {{
                        "analysis": "explanation of root cause",
                        "fixed_code": "corrected code if code was wrong, else null",
                        "fixed_tests": "corrected tests if tests were wrong, else null"
                        }}"""

    return fix_parsing_prompt


def generate_coder_request(contract: Dict[str, Any]) -> str:
    """
    Generates a request for the coder agent.
    """
    coder_prompt = f"""Contract Specification: {json.dumps(contract, indent=2)}
                          Implement the function according to this contract.
                    """

    return coder_prompt


def generate_test_generator_request(contract: Dict[str, Any], code: str) -> str:
    """
    Generates a request for the test generator agent.
    """
    test_prompt = f"""Contract Specification:
                    {json.dumps(contract, indent=2)}

                    Implementation Code:
                    {code}

                    Write comprehensive pytest tests for this implementation based on the contract."""

    return test_prompt


def generate_tester_request(contract: Dict[str, Any], python_code: str, reverty_code: str, tests: str, failed_tests: str, error_output: str) -> str:
    """
    Generates a prompt for the tester agent.
    """
    tester_prompt = f"""Contract (The Specification):
            {json.dumps(contract, indent=2)}

            Reverty Code:
            {reverty_code}

            Equivalent Python Code:
            {python_code}

            Current Tests:
            {tests}

            Test Execution Output (Failures):
            {error_output}

            Failed Tests:
            {failed_tests}

            Analyze the failures. The contract is the single source of truth.
            Either the code violates the contract, or the tests make incorrect assumptions.

            """

    return tester_prompt
