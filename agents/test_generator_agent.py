from typing import Dict, Any
from agents.agent import Agent
from helpers.system_prompts import TESTER_GENERATOR_SYSTEM_PROMPT
from helpers.prompt_generator import generate_test_generator_request, generate_test_generator_fix_request


class TestGeneratorAgent(Agent):
    """
    Uses LLM to generate pytest tests based on a formal contract and implementation code.
    """

    def build_tests(self, contract: Dict[str, Any], python_code: str) -> str:
        """
        Generates pytest tests based on the contract and implementation code.

        """
        print(f"[Tester] Writing tests for: {contract.get('function_name')}...")

        test_prompt = generate_test_generator_request(contract, python_code)

        response = self.client.generate(
            user_prompt=test_prompt, system_prompt=TESTER_GENERATOR_SYSTEM_PROMPT
        )

        # Clean up potential markdown formatting
        print(f"[Tester Agent] Response: {response}")
        test_code = self._extract_json(response)["code"] + "\n"

        return test_code

    def fix_tests(self, contract: Dict[str, Any], python_code: str, test_errors: str) -> str:
        """
        Fixes pytest tests based on the contract and implementation code.

        """
        print(f"[Tester] Fixing tests for: {contract.get('function_name')}...")

        test_prompt = generate_test_generator_fix_request(contract, python_code, test_errors)

        response = self.client.generate(
            user_prompt=test_prompt, system_prompt=TESTER_GENERATOR_SYSTEM_PROMPT
        )

        # Clean up potential markdown formatting
        print(f"[Tester Agent] Response: {response}")
        test_code = self._extract_json(response)["code"] + "\n"

        return test_code