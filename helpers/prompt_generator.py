from toon_format import encode
from typing import Dict, Any

"""
Helper functions for generating user requests from user prompts.
"""


def generate_architect_request(user_prompt: str, complexity: int) -> str:
    """
    Generates a request for the architect agent.
    """

    return (
        f"User request: {user_prompt}\n"
        "Design a technical specification (contract) for this function. \n"
        "IMPORTANT: Focus ONLY on the 'User Request' above.\n"
        f"IMPORTANT: Complexity rating: {complexity}\n"
        "IMPORTANT: If the complexity is lower than 6, do not add docstrings or any other text if not explicitly mentioned in the user prompt.\n"
        "IMPORTANT: The techical specification must be in line with the complexity rating. DO NOT OVERCOMPLICATE THE TECHNICAL SPECIFICATION FOR COMPLEXITY LOWER THAN 6.\n"
        "IMPORTANT: Return ONLY a valid TOON object, with no additional text, no markdown, no explanations.\n"
    )


def generate_static_fix_request(reverty_code: str, errors: str, error_type: str, contract: Dict[str, Any]) -> str:
    """
    Generates a request for the fix agent.
    """

    contract_toon = encode(contract)

    return (
        "Contract:\n"
        f"{contract_toon}\n"
        "Code:\n"
        f"{reverty_code}\n"
        "Errors:\n"
        f"{errors}\n"
        "I have a broken Reverty code that needs fixing based on the Static Analysis errors.\n"
        f"Fix these {error_type} errors and return only the corrected code.\n"
        "Check closely the contract and the errors in order to understand where the errors come from.\n"
        "Do not add any extra text, no markdown, no explanations.\n"
    )


def generate_test_fix_request(contract: Dict[str, Any], reverty_code: str, python_code: str, errors: str) -> str:
    """
    Generates a request for the fix agent.
    """

    contract_toon = encode(contract)

    return (
        "Contract:\n"
        f"{contract_toon}\n"
        "Reverty Code:\n"
        f"{reverty_code}\n"
        "Equivalent Python Code:\n"
        f"{python_code}\n"
        "Test Execution Output (Failures):\n"
        f"{errors}\n"
        "Analyze the failures. The contract is the single source of truth.\n"
        "Return ONLY the corrected reverty code, with no additional text, no markdown, no explanations.\n"
    )


def generate_initial_code_request(contract: Dict[str, Any]) -> str:
    """
    Generates a request for the coder agent.
    """

    contract_toon = encode(contract)

    return (
        "Contract Specification:\n"
        f"{contract_toon}\n"
        "Implement the function according to this contract.\n"
    )


def generate_test_generator_request(contract: Dict[str, Any], code: str) -> str:
    """
    Generates a request for the test generator agent.
    """

    contract_toon = encode(contract)

    return (
        "Contract Specification:\n"
        f"{contract_toon}\n"
        "Implementation Code:\n"
        f"{code}\n"
        "Write comprehensive pytest tests for this implementation based on the contract.\n"
    )


def generate_test_generator_fix_request(contract: Dict[str, Any], code: str, errors: str) -> str:
    """
    Generates a request for the test generator agent.
    """
    contract_toon = encode(contract)

    return (
        "Contract Specification:\n"
        f"{contract_toon}\n"
        "Implementation Code:\n"
        f"{code}\n"
        "Errors:\n"
        f"{errors}\n"
        "Fix the tests based on the errors and the contract.\n"
    )


def generate_tester_request(contract: Dict[str, Any], python_code: str, reverty_code: str, tests: str, failed_tests: str, error_output: str) -> str:
    """
    Generates a prompt for the tester agent.
    """

    contract_toon = encode(contract)

    return (
        "Contract (The Specification):\n"
        f"{contract_toon}\n"
        "Reverty Code:\n"
        f"{reverty_code}\n"
        "Equivalent Python Code:\n"
        f"{python_code}\n"
        "Current Tests:\n"
        f"{tests}\n"
        "Test Execution Output (Failures):\n"
        f"{error_output}\n"
        "Failed Tests:\n"
        f"{failed_tests}\n"
        "Analyze the failures. The contract is the single source of truth.\n"
        "Either the code violates the contract, or the tests make incorrect assumptions.\n"
    )
