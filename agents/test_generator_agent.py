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
        self.log(f"[Tester] Writing tests for: {contract.get('function_name')}...")

        test_prompt: str = generate_test_generator_request(contract, python_code)

        response: str = self.client.generate(
            user_prompt=test_prompt, system_prompt=TESTER_GENERATOR_SYSTEM_PROMPT
        )

        # Clean up potential markdown formatting
        self.log(f"[Tester Agent] Response: {response}")
        test_code: str = self.extract_response(response)["code"] + "\n"

        return test_code

    def fix_tests(self, contract: Dict[str, Any], python_code: str, test_errors: str) -> str:
        """
        Fixes pytest tests based on the contract and implementation code.

        """
        self.log(f"[Tester] Fixing tests for: {contract.get('function_name')}...")

        test_prompt: str = generate_test_generator_fix_request(contract, python_code, test_errors)

        response: str = self.client.generate(
            user_prompt=test_prompt, system_prompt=TESTER_GENERATOR_SYSTEM_PROMPT
        )

        # Clean up potential markdown formatting
        self.log(f"[Tester Agent] Response: {response}")
        test_code: str = self.extract_response(response)["code"] + "\n"

        return test_code