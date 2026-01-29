"""
Helper functions for generating user requests from user prompts.
"""


def generate_architect_request(user_prompt: str) -> str:
    """
    Generates a request for the architect agent.

    Args:
        user_prompt: The user's request.

    Returns:
        A string containing the request for the architect agent.
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


def generate_fix_request(reverty_code: str, errors: str) -> str:

    """
    Generates a request for the fix agent.
    """

    fix_parsing_prompt = f"""Your code has parsing errors:

                        Code:
                        {reverty_code}

                        Errors:
                        {errors}

                        Fix these parsing errors and return only the corrected code.
                    """


    return fix_parsing_prompt