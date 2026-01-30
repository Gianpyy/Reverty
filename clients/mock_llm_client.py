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

        # Hardcoded response for fix (takes priority over builder)
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

        # Hardcoded response for builder agent
        if "builder" in system_prompt_lower:
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
            print("[MockLLMClient - Builder] ", response)
            return response
