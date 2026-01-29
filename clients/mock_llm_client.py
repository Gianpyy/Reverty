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
        print("[MockLLMClient] Generating response for \n", user_prompt_lower)

        # Hardcoded response for architect agent
        if "architect" in system_prompt_lower:
            return json.dumps(
                {
                    "function_name": "factorial",
                    "args": [{"name": "n", "type": "int"}],
                    "return_type": "int",
                    "docstring": "Calculates factorial of n.",
                    "constraints": ["n >= 0"],
                    "edge_cases": [],
                }
            )
        
        if "builder" in system_prompt_lower:
            return json.dumps(
                {
                    "code": """: tni -> (tni: n) factorial fed
                        res = 1
                        : n > 1 elihw
                            res = res * n
                            n = n - 1
                        nruter res
                    """,
                }
            )
        
        if "fix" in system_prompt_lower:
            return json.dumps(
                {
                    "code": """tni -> (tni: n) factorial fed
                        res : tni = 1
                        : n > 1 elihw
                            res = res * n
                            n = n - 1
                        nruter res
                    """,
                }
            )
