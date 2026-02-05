import json
from typing import Dict, Any

"""
Helper functions for generating user requests from user prompts.
"""


def generate_architect_request(user_prompt: str, complexity: int) -> str:
    """
    Generates a request for the architect agent.
    """

    return f"""User request: {user_prompt}
    Design a technical specification (contract) for this function. 
    IMPORTANT: Focus ONLY on the 'User Request' above.
    IMPORTANT: Complexity rating is {complexity}. 
    IMPORTANT: If the complexity is lower than 6, do not add docstrings or any other text if not explicitly mentioned in the user prompt.
    IMPORTANT: The techical specification must be in line with the complexity rating. DO NOT OVERCOMPLICATE THE TECHNICAL SPECIFICATION FOR COMPLEXITY LOWER THAN 6.

    You MUST respond with ONLY a valid JSON object, nothing else.

    IMPORTANT: Return ONLY the JSON object above, with no additional text, no markdown, no explanations."""


def generate_static_fix_request(reverty_code: str, errors: str, error_type: str, contract: Dict[str, Any]) -> str:
    """
    Generates a request for the fix agent.
    """

    fix_parsing_prompt = f"""
                        Contract:
                        {json.dumps(contract, indent=2)}

                        Code:
                        {reverty_code}

                        Errors:
                        {errors}

                        I have a broken Reverty code that needs fixing based on the Static Analysis errors.
                        Fix these {error_type} errors and return only the corrected code.
                        Check closely the contract and the errors in order to understand where the errors come from.
                        Do not add any extra text, no markdown, no explanations.
                    """

    return fix_parsing_prompt


def generate_test_fix_request(contract: Dict[str, Any], reverty_code: str, python_code: str, errors: str) -> str:
    """
    Generates a request for the fix agent.
    """

    fix_parsing_prompt = f"""
                        Contract (The Specification):
                        {json.dumps(contract, indent=2)}

                        Reverty Code:
                        {reverty_code}

                        Equivalent Python Code:
                        {python_code}

                        Test Execution Output (Failures):
                        {errors}

                        Analyze the failures. The contract is the single source of truth.
                        Return ONLY the corrected reverty code, with no additional text, no markdown, no explanations."""

    return fix_parsing_prompt


def generate_initial_code_request(contract: Dict[str, Any]) -> str:
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

def generate_test_generator_fix_request(contract: Dict[str, Any], code: str, errors: str) -> str:
    """
    Generates a request for the test generator agent.
    """
    test_prompt = f"""Contract Specification:
                    {json.dumps(contract, indent=2)}

                    Implementation Code:
                    {code}

                    Errors:
                    {errors}

                    Fix the tests based on the errors and the contract."""

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
